import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 網頁基本設定
st.set_page_config(layout="wide", page_title="美股+台股指標趨勢與網格波段雙軌導航系統")
st.title("🦅 美股 + 台股指標趨勢 vs 網格波段雙軌導航系統")
st.markdown("本系統已全面支援**美股與台股**！將決策拆解為**『指標趨勢決策』**與**『網格波段決策』**，雙軌並行。")

# 2. 內建核心產業與「卡脖子」供應鏈地圖 (新增台股核心板塊)
INITIAL_SECTOR_MAP = {
    # 🇹🇼 台灣股市核心名單 (後綴需為 .TW)
    "2330.TW": "🇹🇼 台股 - 半導體晶圓代工 (全球核心)", 
    "2851.TW": "🇹🇼 台股 - 金融再保險",
    
    # 🇺🇸 2026 美股核心卡脖子：電力基建、液冷與綠能技術
    "GEV": "⚡ 電網設備與基建 (卡脖子核心)", "ETN": "⚡ 電網設備與基建 (卡脖子核心)", "PWR": "⚡ 電網線路工程 (卡脖子核心)",
    "VRT": "❄️ 機房液冷與散熱 (卡脖子核心)", "MOD": "❄️ 機房液冷與散熱 (卡脖子核心)",
    "CEG": "☢️ 獨立核能/天然氣發電", "VST": "☢️ 獨立核能/天然氣發電",
    "ENPH": "☀️ 綠能逆變器與微電網", "SEDG": "☀️ 綠能逆變器與微電網",
    
    # 美股 AI 核心晶片、記憶體與網通
    "NVDA": "AI 晶片 / 半導體設計", "AVGO": "AI 晶片 / 半導體設計", "QCOM": "AI 晶片 / 半導體設計", 
    "MRVL": "AI 晶片 / 半導體設計", "TXN": "AI 晶片 / 半導體設計", "ADI": "AI 晶片 / 半導體設計", 
    "ON": "AI 晶片 / 半導體設計", "MPWR": "AI 晶片 / 半導體設計", "NVTS": "AI 晶片 / 半導體設計",
    "MU": "記憶體與儲存 (HBM/DRAM)", "SNDK": "記憶體與儲存 (HBM/DRAM)", "RMBS": "記憶體與儲存 (HBM/DRAM)", 
    "DRAM": "記憶體與儲存 (HBM/DRAM)", "SITM": "記憶體與儲存 (HBM/DRAM)",
    "COHR": "光通訊與網通硬體", "LITE": "光通訊與網通硬體", "AAOI": "光通訊與網通硬體", 
    "FN": "光通訊與網通硬體", "CIEN": "光通訊與網通硬體", "NOK": "光通訊與網通硬體", 
    "CBRS": "光通訊與網通硬體", "ANET": "光通訊與網通硬體",
    
    # 美股 晶圓代工與軟體巨頭
    "TSM": "晶圓代工與設備製程", "INTC": "晶圓代工與設備製程", "SNPS": "晶圓代工與設備製程", 
    "TSEM": "晶圓代工與設備製程", "AXTI": "晶圓代工與設備製程", "SIMO": "晶圓代工與設備製程", 
    "ALAB": "晶圓代工與設備製程", "ASML": "晶圓代工與設備製程",
    "META": "AI 巨頭 / 軟體平台", "AMZN": "AI 巨頭 / 軟體平台", "MSFT": "AI 巨頭 / 軟體平台", 
    "AAPL": "AI 巨頭 / 軟體平台", "GOOGL": "AI 巨頭 / 軟體平台", "PLTR": "AI 巨頭 / 軟體平台", 
    "NOW": "AI 巨頭 / 軟體平台", "ORCL": "AI 巨頭 / 軟體平台", "APP": "AI 巨頭 / 軟體平台", 
    "NET": "AI 巨頭 / 軟體平台", "CRWV": "AI 巨頭 / 軟體平台",
    
    # 美股 其他綜合/特殊題材/ETF
    "RDW": "航太、太空與國防", "RKLB": "航太、太空與國防", "ASTS": "航太、太空與國防", "BA": "航太、太空與國防", "ONDS": "航太、太空與國防",
    "OXY": "傳統能源與礦產", "EQT": "傳統能源與礦產",
    "TEM": "生技與醫療科技", "GRAL": "生技與醫療科技", "ILMN": "生技與醫療科技",
    "SOFI": "金融科技與資產管理", "HOOD": "金融科技與資產管理", "GS": "金融科技與資產管理", "BLK": "金融科技與資產管理", "BX": "金融科技與資產管理", "SEI": "金融科技與資產管理",
    "TSLA": "智能車與新能源", "MSTR": "比特幣與微策略科技", "BRK-B": "價值投資綜合控股 (波克夏)", "SHLD": "其他綜合/特殊題材", "NBIS": "其他綜合/特殊題材",
    "QQQ": "指數與主題型 ETF", "MAGS": "指數與主題型 ETF", "SOXX": "指數與主題型 ETF", "SMH": "指數與主題型 ETF", "XSD": "指數與主題型 ETF", "GLD": "指數與主題型 ETF"
}

if "sector_map" not in st.session_state:
    st.session_state.sector_map = INITIAL_SECTOR_MAP.copy()

st.sidebar.header("⚙️ 實時管理股票名單")

with st.sidebar.expander("➕ 新增股票至觀察清單", expanded=False):
    add_ticker = st.text_input("輸入代碼 (美股如: SMCI / 台股如: 2317.TW)").strip().upper()
    add_sector = st.selectbox("選擇或指定其產業分類", sorted(list(set(st.session_state.sector_map.values()))))
    if st.button("確認新增"):
        if add_ticker:
            st.session_state.sector_map[add_ticker] = add_sector
            st.toast(f"成功新增 {add_ticker} 進入清單！")
            st.rerun()

all_current_tickers = sorted(list(st.session_state.sector_map.keys()))
active_tickers = st.sidebar.multiselect("💡 目前觀察清單 (點選 X 可直接刪除)", options=all_current_tickers, default=all_current_tickers)

# 策略參數配置
st.sidebar.header("📊 波動率與網格參數設定")
atr_period = st.sidebar.slider("ATR 計算天數", 5, 22, 14)
entry_multiplier = st.sidebar.slider("低吸買進 ATR 倍數", 0.5, 2.5, 1.0, 0.1)
exit_multiplier = st.sidebar.slider("高拋賣出 ATR 倍數", 0.5, 2.5, 1.5, 0.1)
days_back = st.sidebar.number_input("追蹤歷史天數", value=180, min_value=60)
start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

# 數據容器
summary_data = []
action_alerts = []

# 五等標準排序映射
rank_map = {"🔥 強烈買進": 0, "🟢 買進": 1, "⚪ 觀望": 2, "🔴 賣出": 3, "🚨 強烈賣出": 4}

with st.spinner("正在即時拆解指標趨勢與網格波段數據..."):
    for ticker in active_tickers:
        try:
            # 💡 自動判定幣別符號 (台股後綴有 .TW 則使用 NT$，其餘美股使用 $)
            is_tw = ".TW" in ticker or ".TWO" in ticker
            currency_symbol = "NT$ " if is_tw else "$ "
            
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date)
            if df.empty or len(df) < 35:
                continue
                
            # --- 技術數據計算 ---
            high_low = df['High'] - df['Low']
            high_cp = (df['High'] - df['Close'].shift(1)).abs()
            low_cp = (df['Low'] - df['Close'].shift(1)).abs()
            tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
            df['ATR'] = tr.rolling(window=atr_period).mean()
            
            delta = df['Close'].diff()
            gain = (delta.clip(lower=0)).rolling(window=14).mean()
            loss = (-delta.clip(upper=0)).rolling(window=14).mean()
            rs = gain / loss.replace(0, 0.00001)
            df['RSI'] = 100 - (100 / (1 + rs))
            
            df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA12'] - df['EMA26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['STD20'] = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['MA20'] + (2 * df['STD20'])
            df['BB_Lower'] = df['MA20'] - (2 * df['STD20'])
            
            df['L9'] = df['Low'].rolling(window=9).min()
            df['H9'] = df['High'].rolling(window=9).max()
            df['RSV'] = 100 * ((df['Close'] - df['L9']) / (df['H9'] - df['L9']).replace(0, 0.00001))
            df['K'] = df['RSV'].ewm(alpha=1/3, adjust=False).mean()
            df['D'] = df['K'].ewm(alpha=1/3, adjust=False).mean()
            df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            current_price = float(latest['Close'])
            prev_close = float(prev['Close'])
            prev_atr = float(prev['ATR'])
            
            # --- 軌道計算：以昨日收盤為基礎建立今日定價網格邊界 ---
            low_absorb_price = prev_close - (prev_atr * entry_multiplier)
            high_toss_price = prev_close + (prev_atr * exit_multiplier)
            
            # ==========================================
            # 軌道一：技術指標決策 (KD/MACD/RSI/布林共振)
            # ==========================================
            bullish_score = 0
            bearish_score = 0
            
            if latest['RSI'] < 36: bullish_score += 1
            if current_price <= latest['BB_Lower']: bullish_score += 1
            if prev['K'] <= prev['D'] and latest['K'] > latest['D']: bullish_score += 1
            if prev['MACD'] <= prev['MACD_Signal'] and latest['MACD'] > latest['MACD_Signal']: bullish_score += 1
            
            if latest['RSI'] > 66: bearish_score += 1
            if current_price >= latest['BB_Upper']: bearish_score += 1
            if prev['K'] >= prev['D'] and latest['K'] < latest['D']: bearish_score += 1
            if prev['MACD'] >= prev['MACD_Signal'] and latest['MACD'] < latest['MACD_Signal']: bearish_score += 1
            
            volume_spike = latest['Volume'] > (latest['Vol_MA20'] * 1.5)
            
            ind_status = "⚪ 觀望"
            ind_reason = "指標處於中性震盪區間。"
            
            if bullish_score >= 3 or (bullish_score >= 2 and volume_spike):
                ind_status = "🔥 強烈買進"
                ind_reason = f"四大技術指標出現低位多頭共振 (得分:{bullish_score}/4)，主力帶量開火！"
            elif bullish_score >= 1:
                ind_status = "🟢 買進"
                ind_reason = f"技術指標初步見底回升 (得分:{bullish_score}/4)，動能微幅轉強。"
            elif bearish_score >= 3 or (bearish_score >= 2 and volume_spike):
                ind_status = "🚨 強烈賣出"
                ind_reason = f"四大技術指標高檔嚴重超買並出現死叉 (得分:{bearish_score}/4)，動能耗盡。"
            elif bearish_score >= 1:
                ind_status = "🔴 賣出"
                ind_reason = f"技術指標高位滯漲轉弱 (得分:{bearish_score}/4)，上行遭受壓制。"

            # ==========================================
            # 軌道二：網格波段決策 (ATR 空間定價)
            # ==========================================
            atr_status = "⚪ 觀望"
            atr_reason = "股價處於網格合理震盪中樞，未觸及極端拋吸位。"
            
            if current_price <= low_absorb_price:
                atr_status = "🔥 強烈買進"
                atr_reason = f"股價已完全跌破昨日設定之 ATR 動態低吸價，網格觸發強力買入紀律。"
            elif current_price <= low_absorb_price * 1.015:
                atr_status = "🟢 買進"
                atr_reason = f"股價已逼近 ATR 低吸埋伏位 (1.5%以內)，進入預設左側分批布局區。"
            elif current_price >= high_toss_price:
                atr_status = "🚨 強烈賣出"
                atr_reason = f"股價已強力突破昨日設定之 ATR 動態高拋價，達到網格極端獲利區，強力高拋。"
            elif current_price >= high_toss_price * 0.985:
                atr_status = "🔴 賣出"
                atr_reason = f"股價已逼近 ATR 高拋獲利位 (1.5%以內)，達到波段網格落袋為安區。"

            # 只要任一軌道有訊號，就送入今日核心交易行動
            if ind_status != "⚪ 觀望" or atr_status != "⚪ 觀望":
                action_alerts.append({
                    "代碼": ticker,
                    "指標趨勢決策": ind_status,
                    "網格波段決策": atr_status,
                    "最新收盤價": f"{currency_symbol}{current_price:.2f}",
                    "指標警示原因": ind_reason,
                    "網格警示原因": atr_reason
                })

            summary_data.append({
                "產業領域": st.session_state.sector_map.get(ticker, "未分類"),
                "代碼": ticker,
                "最新收盤價": f"{currency_symbol}{current_price:.2f}",
                "指標趨勢決策": ind_status,
                "網格波段決策": atr_status,
                "量能爆發": "⚠️ 爆量" if volume_spike else "正常",
                "建議低吸價 (買點)": f"{currency_symbol}{low_absorb_price:.2f}",
                "建議高拋價 (賣點)": f"{currency_symbol}{high_toss_price:.2f}",
                "共振得分": f"多:{bullish_score} | 空:{bearish_score}"
            })
        except Exception:
            pass

# --- 畫面呈現排版 ---

# 【第一層：🚨 今日核心交易行動警告區】
st.header("🚨 今日雙軌核心交易行動 (Action Alerts)")
if action_alerts:
    alert_df = pd.DataFrame(action_alerts)
    alert_df['sort_1'] = alert_df['指標趨勢決策'].map(rank_map)
    alert_df['sort_2'] = alert_df['網格波段決策'].map(rank_map)
    alert_df['final_sort'] = alert_df[['sort_1', 'sort_2']].min(axis=1)
    alert_df = alert_df.sort_values('final_sort').drop(['sort_1', 'sort_2', 'final_sort'], axis=1)
    st.dataframe(alert_df, use_container_width=True, hide_index=True)
else:
    st.info("🧘 今日趨勢指標與網格軌道皆無觸發邊界，請繼續安心抱股觀望。")

st.markdown("---")

# 【第二層：📊 完整產業雙軌訊號清單】
st.header("📊 完整產業雙軌量化清單")
if summary_data:
    summary_df = pd.DataFrame(summary_data)
    summary_df['sort_1'] = summary_df['指標趨勢決策'].map(rank_map)
    summary_df['sort_2'] = summary_df['網格波段決策'].map(rank_map)
    summary_df['final_sort'] = summary_df[['sort_1', 'sort_2']].min(axis=1)
    summary_df = summary_df.sort_values(by=["final_sort", "產業領域", "代碼"]).drop(['sort_1', 'sort_2', 'final_sort'], axis=1)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.markdown("---")

# 【第三層：🔍 個股深度通道視覺化】
st.header("🔍 個股動態雙軌通道分析")
selected_stock = st.selectbox("選擇你想查看的個股細節：", sorted(active_tickers))

if selected_stock:
    try:
        is_tw = ".TW" in selected_stock or ".TWO" in selected_stock
        currency_label = "新台幣" if is_tw else "美元"
        
        stock_detail = yf.Ticker(selected_stock)
        df_detail = stock_detail.history(start=start_date)
        if not df_detail.empty and len(df_detail) > 20:
            df_detail['MA20'] = df_detail['Close'].rolling(window=20).mean()
            df_detail['STD20'] = df_detail['Close'].rolling(window=20).std()
            df_detail['BB_Upper'] = df_detail['MA20'] + (2 * df_detail['STD20'])
            df_detail['BB_Lower'] = df_detail['MA20'] - (2 * df_detail['STD20'])
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df_detail.index, open=df_detail['Open'], high=df_detail['High'], low=df_detail['Low'], close=df_detail['Close'], name='K線'))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['BB_Upper'], name='布林上軌 (指標超買線)', line=dict(color='rgba(255, 165, 0, 0.6)', width=1.5)))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA20'], name='20MA生命線', line=dict(color='rgba(128, 128, 128, 0.5)', width=1)))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['BB_Lower'], name='布林下軌 (指標超賣線)', line=dict(color='rgba(0, 191, 255, 0.6)', width=1.5)))
            
            fig.update_layout(xaxis_rangeslider_visible=False, yaxis_title=f"價格 ({currency_label})", height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🕵️‍♂️ 公司內部人交易動向 (Insider)")
                if is_tw:
                    st.info("💡 提示：本區塊內部人數據為美股 SEC 規範申報。台股內部人籌碼變化請至台灣公開資訊觀測站查詢。")
                else:
                    try:
                        insider_df = stock_detail.insider_transactions
                        if insider_df is not None and not insider_df.empty:
                            st.dataframe(insider_df[['Start Date', 'Insider', 'Position', 'Transaction', 'Shares', 'Value']].head(6), use_container_width=True)
                        else: st.write("近期無內部人大幅交易申報。")
                    except Exception:
                        st.write("暫時無法調閱美股內部人數據。")
            with col2:
                st.subheader("📰 影響股價的最新市場消息")
                try:
                    news_list = stock_detail.news
                    if news_list:
                        for article in news_list[:3]:
                            st.markdown(f"**[{article.get('title', '無標題')}]({article.get('link', '#')})**")
                            st.caption(f"來源: {article.get('publisher', '未知媒体')}")
                    else: st.write("暫無即時新聞。")
                except Exception:
                    st.write("暫時無法取得實時新聞流。")
    except Exception as e:
        st.error(f"分析失敗: {e}")
