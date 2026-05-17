import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 網頁基本設定
st.set_page_config(layout="wide", page_title="美股多指標共振與即時行動警告系統")
st.title("🦅 美股五等量化訊號與 ATR 低吸高拋導航系統")
st.markdown("本系統已全面將欄位統一為 **每日建議行動**，並嚴格遵循五個等級指示，方便快速篩選執行 Action。")

# 2. 內建核心產業與「卡脖子」供應鏈地圖
INITIAL_SECTOR_MAP = {
    "GEV": "⚡ 電網設備與基建 (卡脖子核心)", "ETN": "⚡ 電網設備與基建 (卡脖子核心)", "PWR": "⚡ 電網線路工程 (卡脖子核心)",
    "VRT": "❄️ 機房液冷與散熱 (卡脖子核心)", "MOD": "❄️ 機房液冷與散熱 (卡脖子核心)",
    "CEG": "☢️ 獨立核能/天然氣發電", "VST": "☢️ 獨立核能/天然氣發電",
    "ENPH": "☀️ 綠能逆變器與微電網", "SEDG": "☀️ 綠能逆變器與微電網",
    "NVDA": "AI 晶片 / 半導體設計", "AVGO": "AI 晶片 / 半導體設計", "QCOM": "AI 晶片 / 半導體設計", 
    "MRVL": "AI 晶片 / 半導體設計", "TXN": "AI 晶片 / 半導體設計", "ADI": "AI 晶片 / 半導體設計", 
    "ON": "AI 晶片 / 半導體設計", "MPWR": "AI 晶片 / 半導體設計", "NVTS": "AI 晶片 / 半導體設計",
    "MU": "記憶體與儲存 (HBM/DRAM)", "SNDK": "記憶體與儲存 (HBM/DRAM)", "RMBS": "記憶體與儲存 (HBM/DRAM)", 
    "DRAM": "記憶體與儲存 (HBM/DRAM)", "SITM": "記憶體與儲存 (HBM/DRAM)",
    "COHR": "光通訊與網通硬體", "LITE": "光通訊與網通硬體", "AAOI": "光通訊與網通硬體", 
    "FN": "光通訊與網通硬體", "CIEN": "光通訊與網通硬體", "NOK": "光通訊與網通硬體", 
    "CBRS": "光通訊與網通硬體", "ANET": "光通訊與網通硬體",
    "TSM": "晶圓代工與設備製程", "INTC": "晶圓代工與設備製程", "SNPS": "晶圓代工與設備製程", 
    "TSEM": "晶圓代工與設備製程", "AXTI": "晶圓代工與設備製程", "SIMO": "晶圓代工與設備製程", 
    "ALAB": "晶圓代工與設備製程", "ASML": "晶圓代工與設備製程",
    "META": "AI 巨頭 / 軟體平台", "AMZN": "AI 巨頭 / 軟體平台", "MSFT": "AI 巨頭 / 軟體平台", 
    "AAPL": "AI 巨頭 / 軟體平台", "GOOGL": "AI 巨頭 / 軟體平台", "PLTR": "AI 巨頭 / 軟體平台", 
    "NOW": "AI 巨頭 / 軟體平台", "ORCL": "AI 巨頭 / 軟體平台", "APP": "AI 巨頭 / 軟體平台", 
    "NET": "AI 巨頭 / 軟體平台", "CRWV": "AI 巨頭 / 軟體平台",
    "RDW": "航太、太空與國防", "RKLB": "航太、太空與國防", "ASTS": "航太、太空與國防", "BA": "航太、太空與國防", "ONDS": "航太、太空與國防",
    "OXY": "傳統能源與礦產", "EQT": "傳統能源與礦產",
    "TEM": "生技與醫療科技", "GRAL": "生技與醫療科技", "ILMN": "生技與醫療科技",
    "SOFI": "金融科技與資產管理", "HOOD": "金融科技與資產管理", "GS": "金融科技與資產管理", "BLK": "金融科技與資產管理", "BX": "金融科技與資產管理", "SEI": "金融科技與資產管理",
    "TSLA": "智能車與新能源", "MSTR": "比特幣與微策略科技", "BRK-B": "價值投資綜合控股 (波克夏)", "SHLD": "其他綜合/特殊題材", "NBIS": "其他綜合/特殊題材",
    "QQQ": "指數與主題型 ETF", "MAGS": "指數與主題型 ETF", "SOXX": "指數與主題型 ETF", "SMH": "指數與主題型 ETF", "XSD": "指數與主題型 ETF", "GLD": "指數與主題型 ETF"
}

# 3. 實時動態增減股票邏輯
if "sector_map" not in st.session_state:
    st.session_state.sector_map = INITIAL_SECTOR_MAP.copy()

st.sidebar.header("⚙️ 實時管理股票名單")

with st.sidebar.expander("➕ 新增股票至觀察清單", expanded=False):
    add_ticker = st.text_input("輸入美股代碼 (例如: SMCI)").strip().upper()
    add_sector = st.selectbox("選擇或指定其產業分類", sorted(list(set(st.session_state.sector_map.values()))))
    if st.button("確認新增"):
        if add_ticker:
            st.session_state.sector_map[add_ticker] = add_sector
            st.toast(f"成功新增 {add_ticker} 進入清單！")
            st.rerun()

all_current_tickers = sorted(list(st.session_state.sector_map.keys()))
active_tickers = st.sidebar.multiselect("💡 目前觀察清單 (點選 X 可直接刪除)", options=all_current_tickers, default=all_current_tickers)

# 策略參數配置
st.sidebar.header("📊 波動率參數設定")
atr_period = st.sidebar.slider("ATR 計算天數", 5, 22, 14)
entry_multiplier = st.sidebar.slider("低吸買進 ATR 倍數 (最新價減幾倍)", 0.5, 2.5, 1.0, 0.1)
exit_multiplier = st.sidebar.slider("高拋賣出 ATR 倍數 (最新價加幾倍)", 0.5, 2.5, 1.5, 0.1)
days_back = st.sidebar.number_input("追蹤歷史天數", value=180, min_value=60)
start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

# 導讀專區
with st.expander("💡 華爾街最新 AI 基礎建設『卡脖子』前沿趨勢導讀", expanded=False):
    st.markdown("""
    * **電網與變壓器荒**：全美資料中心因電力短缺卡關。**龍頭標的**：`GEV`, `ETN`, `PWR`，核電獨立發電商 `CEG`, `VST`。
    * **高密度液冷轉折點**：新世代晶片功耗飆破物理極限，全面強制轉向液冷。**龍頭標的**：全球液冷龍頭 `VRT`、散熱黑馬 `MOD`。
    * **分散式綠能微電網**：科技巨頭推動機房自我綠能發電。**龍頭標的**：微型逆變器大廠 `ENPH`, `SEDG`。
    """)

# 核心數據儲存器
summary_data = []
action_alerts = []

# 定義嚴格的訊號階層排序映射
rank_map = {"🔥 強烈買進": 0, "🟢 買進": 1, "⚪ 觀望": 2, "🔴 賣出": 3, "🚨 強烈賣出": 4}

with st.spinner("正在即時計算五等量化指標與篩選 ACTION 訊號..."):
    for ticker in active_tickers:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date)
            if df.empty or len(df) < 35:
                continue
                
            # --- 技術指標計算 ---
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
            atr_val = float(latest['ATR'])
            
            # --- ATR 動態點位擬訂 ---
            low_absorb_price = current_price - (atr_val * entry_multiplier)
            high_toss_price = current_price + (atr_val * exit_multiplier)
            
            # --- 五等量化計分系統 ---
            bullish_score = 0
            bearish_score = 0
            
            if latest['RSI'] < 38: bullish_score += 1
            if current_price <= latest['BB_Lower']: bullish_score += 1
            if prev['K'] <= prev['D'] and latest['K'] > latest['D']: bullish_score += 1
            if prev['MACD'] <= prev['MACD_Signal'] and latest['MACD'] > latest['MACD_Signal']: bullish_score += 1
            
            if latest['RSI'] > 68: bearish_score += 1
            if current_price >= latest['BB_Upper']: bearish_score += 1
            if prev['K'] >= prev['D'] and latest['K'] < latest['D']: bearish_score += 1
            if prev['MACD'] >= prev['MACD_Signal'] and latest['MACD'] < latest['MACD_Signal']: bearish_score += 1
            
            volume_spike = latest['Volume'] > (latest['Vol_MA20'] * 1.5)
            
            # 決定五個標準等級
            action_status = "⚪ 觀望"
            reason_str = ""
            
            if bullish_score >= 3 or (bullish_score >= 2 and volume_spike):
                action_status = "🔥 強烈買進"
                reason_str = "指標低檔強烈共振，且主力資金爆量開火，右側噴發訊號強烈！"
            elif bullish_score == 2 or abs(current_price - low_absorb_price) / current_price <= 0.015:
                action_status = "🟢 買進"
                if abs(current_price - low_absorb_price) / current_price <= 0.015:
                    reason_str = "股價已精準拉回到 ATR 動態低吸埋伏位，適合左側分批布局。"
                else:
                    reason_str = "技術指標觸底回升，具備初步止跌反彈動能。"
            elif bearish_score >= 3 or (bearish_score >= 2 and volume_spike):
                action_status = "🚨 強烈賣出"
                reason_str = "指標高檔死叉共振且爆量滯漲，多頭動能耗盡，強烈建議高拋獲利。"
            elif bearish_score == 2 or abs(current_price - high_toss_price) / current_price <= 0.015:
                action_status = "🔴 賣出"
                if abs(current_price - high_toss_price) / current_price <= 0.015:
                    reason_str = "股價已推升至 ATR 動態高拋壓力位，觸及預設短線獲利目標。"
                else:
                    reason_str = "技術指標超買死叉，上行空間受阻，建議適度減碼。"

            # 如果觸發非觀望訊號，加入頂部 Action 警告
            if action_status != "⚪ 觀望":
                action_alerts.append({
                    "代碼": ticker,
                    "每日建議行動": action_status,
                    "最新價": f"${current_price:.2f}",
                    "關鍵原因": reason_str
                })

            summary_data.append({
                "產業領域": st.session_state.sector_map.get(ticker, "未分類"),
                "代碼": ticker,
                "最新收盤價": f"${current_price:.2f}",
                "每日建議行動": action_status,
                "共振多/空分": f"多:{bullish_score} | 空:{bearish_score}",
                "量能爆發": "⚠️ 爆量" if volume_spike else "正常",
                "建議低吸價 (買點)": f"${low_absorb_price:.2f}",
                "建議高拋價 (賣點)": f"${high_toss_price:.2f}",
                "RSI": f"{latest['RSI']:.1f}"
            })
        except Exception:
            pass

# --- 畫面呈現與排版 ---

# 【第一層：🚨 今日核心交易行動警告區】
st.header("🚨 今日核心交易行動 (Action Alerts)")
if action_alerts:
    alert_df = pd.DataFrame(action_alerts)
    # 按強烈買進 -> 買進 -> 賣出 -> 強烈賣出排序
    alert_df['sort_order'] = alert_df['每日建議行動'].map(rank_map)
    alert_df = alert_df.sort_values('sort_order').drop('sort_order', axis=1)
    st.dataframe(alert_df, use_container_width=True, hide_index=True)
else:
    st.info("🧘 今日無任何個股觸發臨界點，請保持觀察，繼續按兵不動觀望。")

st.markdown("---")

# 【第二層：📊 完整產業五等訊號清單】
st.header("📊 完整產業五等訊號清單")
if summary_data:
    summary_df = pd.DataFrame(summary_data)
    summary_df['rank'] = summary_df['每日建議行動'].map(rank_map)
    summary_df = summary_df.sort_values(by=["rank", "產業領域", "代碼"]).drop('rank', axis=1)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.markdown("---")

# 【第三層：🔍 個股深度通道視覺化】
st.header("🔍 個股動態低吸高拋通道分析")
selected_stock = st.selectbox("選擇你想查看的個股細節：", sorted(active_tickers))

if selected_stock:
    try:
        stock_detail = yf.Ticker(selected_stock)
        df_detail = stock_detail.history(start=start_date)
        if not df_detail.empty and len(df_detail) > 20:
            df_detail['MA20'] = df_detail['Close'].rolling(window=20).mean()
            df_detail['STD20'] = df_detail['Close'].rolling(window=20).std()
            df_detail['BB_Upper'] = df_detail['MA20'] + (2 * df_detail['STD20'])
            df_detail['BB_Lower'] = df_detail['MA20'] - (2 * df_detail['STD20'])
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df_detail.index, open=df_detail['Open'], high=df_detail['High'], low=df_detail['Low'], close=df_detail['Close'], name='K線'))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['BB_Upper'], name='布林上軌 (高檔壓力線)', line=dict(color='rgba(255, 165, 0, 0.6)', width=1.5)))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA20'], name='20MA生命線', line=dict(color='rgba(128, 128, 128, 0.5)', width=1)))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['BB_Lower'], name='布林下軌 (低檔支撐線)', line=dict(color='rgba(0, 191, 255, 0.6)', width=1.5)))
            
            fig.update_layout(xaxis_rangeslider_visible=False, yaxis_title="價格 (美元)", height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🕵️‍♂️ 公司內部人交易動向 (Insider)")
                insider_df = stock_detail.insider_transactions
                if insider_df is not None and not insider_df.empty:
                    st.dataframe(insider_df[['Start Date', 'Insider', 'Position', 'Transaction', 'Shares', 'Value']].head(6), use_container_width=True)
                else: st.write("近期無內部人大幅交易申報。")
            with col2:
                st.subheader("📰 影響股價的最新市場消息")
                news_list = stock_detail.news
                if news_list:
                    for article in news_list[:3]:
                        st.markdown(f"**[{article.get('title', '無標題')}]({article.get('link', '#')})**")
                        st.caption(f"來源: {article.get('publisher', '未知')}")
                else: st.write("暫無即時新聞。")
    except Exception as e:
        st.error(f"分析失敗: {e}")
