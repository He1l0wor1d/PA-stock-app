import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ==========================================
# 核心架構：Henry 策略量化分析類別
# ==========================================
class HenryStockAnalyzer:
    def __init__(self, ticker_str, start_date, end_date):
        self.ticker_str = ticker_str.strip().upper()
        self.start_date = start_date
        self.end_date = end_date
        self.df = pd.DataFrame()
        self.info = {}

    def fetch_data(self):
        """
        加入完善的異常處理，防止 yfinance 抓不到數據時導致網頁崩潰
        """
        try:
            stock = yf.Ticker(self.ticker_str)
            # 多抓 300 天以利精確計算 200MA 與長天期指標
            buffer_start = (datetime.strptime(self.start_date, "%Y-%m-%d") - timedelta(days=300)).strftime("%Y-%m-%d")
            self.df = stock.history(start=buffer_start, end=self.end_date)
            self.info = stock.info
            
            if self.df.empty:
                return False
            return True
        except Exception as e:
            st.error(f"獲取代碼 {self.ticker_str} 數據時發生錯誤: {e}")
            return False

    def calculate_indicators(self):
        """
        第一部分：基礎數據與指標運算 (完全對應 Henry 參數優化)
        """
        df = self.df
        
        # 1. 均線系統 (MA)
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA21'] = df['Close'].rolling(window=21).mean()    # 進出決策線
        df['MA25'] = df['Close'].rolling(window=25).mean()    # 2560戰法基準線
        df['MA50'] = df['Close'].rolling(window=50).mean()    # 中期多空線
        df['MA200'] = df['Close'].rolling(window=200).mean()  # 長期生命線

        # 2. 成交量均量線 (Volume MA)
        df['Vol_MA5'] = df['Volume'].rolling(window=5).mean()
        df['Vol_MA60'] = df['Volume'].rolling(window=60).mean() # 2560戰法地量參考線

        # 3. 機構級 MACD (參數: 5, 34, 5)
        df['EMA5'] = df['Close'].ewm(span=5, adjust=False).mean()
        df['EMA34'] = df['Close'].ewm(span=34, adjust=False).mean()
        df['MACD'] = df['EMA5'] - df['EMA34']
        df['MACD_Signal'] = df['MACD'].ewm(span=5, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

        # 4. RSI 伏擊參數 (短期 9, 中期 55)
        df['RSI_9'] = self._compute_rsi(df['Close'], 9)
        df['RSI_55'] = self._compute_rsi(df['Close'], 55)

        # 5. 乖離率 (BIAS)
        df['BIAS_5'] = ((df['Close'] - df['MA5']) / df['MA5']) * 100
        df['BIAS_200'] = ((df['Close'] - df['MA200']) / df['MA200']) * 100

        # 僅保留使用者選擇的日期區間顯示
        self.df = df.loc[self.start_date:self.end_date]

    def _compute_rsi(self, series, window):
        delta = series.diff()
        gain = (delta.clip(lower=0)).rolling(window=window).mean()
        loss = (-delta.clip(upper=0)).rolling(window=window).mean()
        rs = gain / loss.replace(0, 0.00001)
        return 100 - (100 / (1 + rs))

    # ==========================================
    # 第二部分：核心戰法邏輯診斷 (Strategy Logic)
    # ==========================================
    def diagnose_2133(self):
        """
        2133 戰法：看懂主力在 21MA 決策線上的防守與突破意圖
        """
        df = self.df
        if len(df) < 3: return "⚪ 數據不足，無法診斷"

        latest = df.iloc[-1]
        last_3 = df.tail(3)

        # 買入診斷
        buy_cond_1 = latest['Close'] >= latest['MA21'] * 1.03
        buy_cond_2 = (last_3['Close'] > last_3['MA21']).all()
        
        # 賣出診斷
        sell_cond_1 = latest['Close'] <= latest['MA21'] * 0.97
        sell_cond_2 = (last_3['Close'] < last_3['MA21']).all()

        if buy_cond_1 or buy_cond_2:
            return "🚀 買入訊號：股價已強勢突破 21MA 決策線（高於3%或連續3天站穩），多頭趨勢確立！"
        elif sell_cond_1 or sell_cond_2:
            return "🚨 賣出警訊：股價已跌破 21MA 決策線（跌幅超3%或連續3天在線下），建議全面控管風險！"
        else:
            return "⚪ 觀望：目前股價在 21MA 附近常態震盪，未出現決定性突破。"

    def diagnose_2560(self):
        """
        2560 戰法：尋找主力極致洗盤後的「量價共振」臨界點
        """
        df = self.df
        if len(df) < 10: return "⚪ 數據不足，無法診斷"
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 條件 1：價格在 25MA 之上
        p_above_ma25 = latest['Close'] > latest['MA25']
        
        # 條件 2：近期（過去10天內）成交量曾縮至 60日均量線以下（主力洗盤休兵地量）
        had_low_volume = (df['Volume'].tail(10) < df['Vol_MA60'].tail(10)).any()
        
        # 條件 3：5日均量線向上拐頭，且與 60日均量線粘合（進入高度共振擠壓區）
        vol_ma5_up = latest['Vol_MA5'] > prev['Vol_MA5']
        vol_binding = abs(latest['Vol_MA5'] - latest['Vol_MA60']) / latest['Vol_MA60'] < 0.12 # 12% 內視為粘合

        if p_above_ma25 and had_low_volume and vol_ma5_up and vol_binding:
            return "🔥 2560 戰法共振：符合『地量洗盤後拐頭粘合』！主力即將重新點火，建議高度關注發動點！"
        else:
            return "⚪ 未觸發：量價結構未達到 2560 戰法的緊密共振臨界狀態。"

    def diagnose_macd_shapes(self):
        """
        機構級 MACD 特殊形態識別
        """
        df = self.df
        if len(df) < 5: return "⚪ 數據不足"
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 佛手向上：DIF > 0, DEA > 0，快線拉回不破慢線（或短暫死叉後立刻向上開口），柱狀體重新放大
        if latest['MACD'] > 0 and latest['MACD_Signal'] > 0:
            if latest['MACD_Hist'] > prev['MACD_Hist'] and prev['MACD_Hist'] <= df['MACD_Hist'].iloc[-3]:
                return "🌟 佛手向上：機構資金在零軸上方完成洗盤，再度展開多頭主升浪！"
                
        # 小鴨出水：DIF 與 DEA 在零軸下方低位金叉後，快線（DIF）向零軸爬升，形態如小鴨冒出水面
        if prev['MACD'] <= prev['MACD_Signal'] and latest['MACD'] > latest['MACD_Signal']:
            if latest['MACD'] < 0:
                return "🦆 小鴨出水：築底結束！快線在零軸下黃金交叉，屬於極具爆發力的底部反轉訊號。"
                
        return "⚪ 常態訊號：MACD 目前未呈現特殊主力籌碼型態。"

# ==========================================
# 第三部分：前端介面佈局 (UI Layout)
# ==========================================
st.set_page_config(layout="wide", page_title="Henry 秒懂美股實戰策略儀表板")
st.title("📈 「Henry 秒懂美股」實戰策略分析儀表板")
st.markdown("本工具完美移植 Henry 經典量化戰法，透過多維度技術指標共振與基本面篩選，助您抓準進出場 Action。")

# --- 側邊欄配置 (Sidebar) ---
st.sidebar.header("⚙️ 實戰策略配置面板")
ticker_input = st.sidebar.text_input("輸入美股代碼 (例如: NVDA, AAPL, TSLA)", "NVDA")

col_date1, col_date2 = st.sidebar.columns(2)
with col_date1:
    start_d = st.date_input("開始日期", datetime.now() - timedelta(days=120))
with col_date2:
    end_d = st.date_input("結束日期", datetime.now())

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 選取欲診斷的 Henry 戰法")
check_2133 = st.sidebar.checkbox("2133 波段決策戰法", value=True)
check_2560 = st.sidebar.checkbox("2560 量價共振戰法", value=True)
check_macd = st.sidebar.checkbox("機構級 MACD 特殊型態", value=True)

# 實戰止盈輔助輸入
st.sidebar.subheader("💰 個人持倉成本設定 (333止盈用)")
user_cost = st.sidebar.number_input("您的買入平均成本價 ($)", value=0.0, min_value=0.0)

# --- 核心程式執行邏輯 ---
if ticker_input:
    analyzer = HenryStockAnalyzer(ticker_input, start_d.strftime("%Y-%m-%d"), end_d.strftime("%Y-%m-%d"))
    
    with st.spinner("正在向華爾街調閱即時數據並計算 Henry 指標偏好..."):
        success = analyzer.fetch_data()
        
    if success:
        analyzer.calculate_indicators()
        df = analyzer.df
        latest_data = df.iloc[-1]
        
        # ------------------------------------------
        # 核心功能：行動告警板 (Action Panel)
        # ------------------------------------------
        st.header("🚨 今日即時行動告警板 (Action Panel)")
        
        # 顯示 2133 診斷
        if check_2133:
            res_2133 = analyzer.diagnose_2133()
            if "🚀" in res_2133:
                st.success(f"**【2133 波段戰法】** {res_2133}")
            elif "🚨" in res_2133:
                st.error(f"**【2133 波段戰法】** {res_2133}")
            else:
                st.warning(f"**【2133 波段戰法】** {res_2133}")

        # 顯示 2560 診斷
        if check_2560:
            res_2560 = analyzer.diagnose_2560()
            if "🔥" in res_2560:
                st.success(f"**【2560 量價共振】** {res_2560}")
            else:
                st.info(f"**【2560 量價共振】** {res_2560}")
                
        # 顯示 MACD 特殊型態
        if check_macd:
            res_shapes = analyzer.diagnose_macd_shapes()
            if "🌟" in res_shapes or "🦆" in res_shapes:
                st.success(f"**【機構級 MACD 型態】** {res_shapes}")
            else:
                st.info(f"**【機構級 MACD 型態】** {res_shapes}")

        # 伏擊指標即時資訊快報
        st.markdown("##### 🔍 伏擊指標即時數據快報")
        col_i1, col_i2, col_i3, col_i4 = st.columns(4)
        col_i1.metric("RSI_9 短期伏擊值", f"{latest_data['RSI_9']:.2f}", "超買臨界: 75" if latest_data['RSI_9'] > 75 else "")
        col_i2.metric("RSI_55 中期防守值", f"{latest_data['RSI_55']:.2f}")
        col_i3.metric("5日 均線乖離率 (BIAS)", f"{latest_data['BIAS_5']:.2f}%")
        col_i4.metric("200日 生命線乖離率", f"{latest_data['BIAS_200']:.2f}%")

        # 自動化止盈提醒功能
        if user_cost > 0:
            current_return = (latest_data['Close'] - user_cost) / user_cost
            st.markdown("##### 📈 333 與 532 策略動態止盈指南")
            if current_return >= 0.25:
                st.error(f"⚠️ **【333 止盈警告】** 目前帳面回報已高達 {current_return*100:.1f}%！已跨越 25% 強烈止盈線，請切實執行分批減倉，落袋為安！")
            elif current_return >= 15:
                st.warning(f"⚠️ **【333 止盈提醒】** 目前帳面回報達 {current_return*100:.1f}%（超過 15% 基準線），建議啟動第一階段減倉紀律。")
            else:
                st.info(f"ℹ️ 目前帳面報酬率為 {current_return*100:.1f}%，尚未觸發 333 止盈減倉門檻。")
            st.caption("💡 **【532 時間止盈提醒】** 若近期有重大總體經濟消息（如聯準會 FOMC 利率決議、核心 CPI 公布），請務必具備防守抽水意識，提前回收部分流動性。")

        st.markdown("---")

        # ------------------------------------------
        # 視覺化：主圖表與副圖整合區域 (Charts Area)
        # ------------------------------------------
        st.header(f"📊 {analyzer.ticker_str} 戰法視覺化動態通道")
        
        # 建立三列的 Plotly 聯動圖表
        fig = make_subplots(
            rows=3, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.04, 
            row_heights=[0.5, 0.2, 0.3],
            subplot_titles=(f"K線與均線決策系統", "2560 戰法成交量量能監控", "機構級 MACD (5, 34, 5) 能量潮")
        )

        # 副圖一：K 線圖與五大均線系統
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="K線"
        ), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], name="5MA 攻防線", line=dict(color='gray', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA21'], name="21MA 進出決策線", line=dict(color='orange', width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA25'], name="25MA 2560基準線", line=dict(color='cyan', width=1.5, dash='dash')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name="50MA 中期多空線", line=dict(color='blue', width=1.5)), row=1, col=1)
        # 顯眼色強調 200 日長期生命線
        fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], name="⚠️ 200MA 長期生命線", line=dict(color='crimson', width=3)), row=1, col=1)

        # 副圖二：成交量與 5/60日均量線
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="當日成交量", marker_color='rgba(100, 149, 237, 0.6)'), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['Vol_MA5'], name="5日均量線", line=dict(color='orange', width=1.5)), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['Vol_MA60'], name="60日均量地量線", line=dict(color='purple', width=2)), row=2, col=1)

        # 副圖三：機構級 MACD
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name="DIF 快線", line=dict(color='dodgerblue', width=1.5)), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name="DEA 慢線", line=dict(color='tomato', width=1.5)), row=3, col=1)
        
        # 繪製 MACD 紅綠柱狀體
        colors = ['rgba(235, 71, 71, 0.8)' if val >= 0 else 'rgba(71, 235, 115, 0.8)' for val in df['MACD_Hist']]
        fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], name='柱狀體', marker_color=colors), row=3, col=1)

        # 佈局美化
        fig.update_layout(
            height=850,
            xaxis_rangeslider_visible=False,
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # ------------------------------------------
        # 核心功能：3+1 潛力股基本面篩選面板
        # ------------------------------------------
        st.header("🧱 3+1 潛力股核心基本面診斷面板")
        
        info = analyzer.info
        if info:
            col_f1, col_f2, col_f3 = st.columns(3)
            
            # 財務指標安全性過濾
            net_margin = info.get('netIncomeToCommon', 0) / info.get('totalRevenue', 1) if info.get('netIncomeToCommon') else 0
            current_ratio = info.get('currentRatio', 0)
            pe_ratio = info.get('trailingPE', "無資料")
            
            with col_f1:
                st.metric("公司淨利率 (Net Profit Margin)", f"{net_margin * 100:.2f}%")
                st.caption("💡 Henry 實戰心法：淨利率需高於同業平均水準，代表公司在產業鏈中擁有強大的定價權。")
                
            with col_f2:
                status_cr = "✅ 安全" if current_ratio > 1.5 else "⚠️ 偏低"
                st.metric("流動比率 (Current Ratio)", f"{current_ratio:.2f}", help="需大於 1.5")
                st.caption(f"目前狀態：{status_cr}（Henry 指標：流動比率 > 1.5 代表短期償債防禦力極佳）。")
                
            with col_f3:
                st.metric("當前 PE 估值 (Trailing P/E)", f"{pe_ratio}")
                st.caption("💡 估值需結合當前產業增長率，避免在瘋狂泡沫期追入高 PE 的股票。")

            # 第「+1」項指標：護城河 (Moat)
            st.info("💡 **【Henry 核心提醒：不可忽視的第 +1 項指標 — 企業護城河 (Moat)】**\n\n"
                    "量化數據只能代表過去的成績單，請您在建倉前務必自行評估該企業的『質化護城河』："
                    "例如該公司是否具備巨大的**技術代際壁壘**（如 ASML、TSMC）、**高昂的用戶轉換成本**（如 MSFT 商業生態），"
                    "或**無可取代的品牌壟斷溢價**（如 AAPL）。唯有兼具高淨利率與強大護城河，才是能抱得住的 3+1 頂級標的。")
        else:
            st.warning("無法從伺服器取得該公司的基本面 info 財務數據，請手動至財經網站比對。")

    else:
        st.error("❌ 查無此美股代碼或無法讀取數據，請確認代碼是否輸入正確（如：NVDA, TSLA）。")
