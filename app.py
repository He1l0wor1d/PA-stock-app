import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 頁面基礎設定
st.set_page_config(layout="wide", page_title="股票決策系統")
st.title("🦅 美股+台股『極簡五等燈號』雙軌制決策系統")
st.markdown("本系統已進化為**雙軌制安全引擎**：具備左側抄底的**【🔥強買】**，與具備防追高安全閥的右側**【⚡動能突破】**。")

# ==============================================================================
# 🌐 第一層：全球總體經濟與市場情緒觀測站
# ==============================================================================
st.markdown("### 🌐 全球總體經濟與市場情緒觀測站")
macro_col1, macro_col2, macro_col3 = st.columns([1, 1, 2])

with macro_col1:
    st.markdown("##### 🧭 恐懼與貪婪指標 (Fear & Greed)")
    fg_value = 65  
    fg_status = "🟢 貪婪" if fg_value >= 55 else "⚪ 中性"
    st.metric(label=f"大盤情緒狀態: {fg_status}", value=f"{fg_value} / 100")
    st.progress(fg_value / 100)

with macro_col2:
    st.markdown("##### 📊 席勒本益比 (Shiller PE)")
    st.metric(label="S&P 500 CAPE Ratio", value="31.5", delta="高於歷史均值", delta_color="inverse")

with macro_col3:
    st.markdown("##### 📅 本週關鍵財經數據行事曆")
    calendar_data = {
        "公佈日期": ["05/18", "05/19", "05/20", "05/21", "05/22"],
        "關鍵數據": ["製造業指數", "RBA紀要", "EIA庫存", "Fed紀要", "核心 PCE"],
        "市場結論": ["回溫", "緊盯", "牽動能源", "降息密碼", "預期2.6%"]
    }
    st.dataframe(pd.DataFrame(calendar_data), use_container_width=True, hide_index=True)

st.markdown("---")

# ==============================================================================
# ⚙️ 初始化與參數設定
# ==============================================================================
INITIAL_SECTOR_MAP = {
    "TSM": "晶圓代工", "NVDA": "AI晶片", "AAPL": "軟體服務", "MSFT": "軟體服務", "2330.TW": "晶圓代工", "2317.TW": "電子代工"
}
if "sector_map" not in st.session_state: st.session_state.sector_map = INITIAL_SECTOR_MAP.copy()

st.sidebar.header("⚙️ 實時清單與計量調校")
with st.sidebar.expander("➕ 新增股票", expanded=False):
    add_ticker = st.text_input("輸入代碼").strip().upper()
    if st.button("確認新增") and add_ticker:
        st.session_state.sector_map[add_ticker] = "其他"
        st.rerun()

active_tickers = st.sidebar.multiselect("💡 觀察名單", options=sorted(st.session_state.sector_map.keys()), default=["TSM", "NVDA"])
atr_multiplier = st.sidebar.slider("抄底 ATR 倍數", 0.5, 2.5, 1.4, 0.1)

# ==============================================================================
# 🔍 核心計量引擎
# ==============================================================================
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

summary_data = []
action_alerts = []

for ticker in active_tickers:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")
        if df.empty: continue
        
        # 指標計算
        high_low = df['High'] - df['Low']
        tr = pd.concat([high_low, (df['High'] - df['Close'].shift(1)).abs(), (df['Low'] - df['Close'].shift(1)).abs()], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(14).mean()
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA200'] = df['Close'].rolling(200).mean()
        df['RSI'] = calculate_rsi(df['Close'], 14)
        df['High20'] = df['High'].shift(1).rolling(20).max()
        
        # 最新數據
        cur_p = float(df.iloc[-1]['Close'])
        ma20 = float(df.iloc[-1]['MA20'])
        ma200 = float(df.iloc[-1]['MA200']) if not pd.isna(df.iloc[-1]['MA200']) else ma20
        rsi = float(df.iloc[-1]['RSI'])
        h20 = float(df.iloc[-1]['High20'])
        atr = float(df.iloc[-1]['ATR'])
        
        # 雙軌訊號
        if ma20 >= ma200:
            if cur_p <= (ma20 - (atr * atr_multiplier)):
                action_alerts.append({"代碼": ticker, "訊號": "🔥 強力買入", "原因": "多頭拉回抄底"})
            elif cur_p > h20 and 60 <= rsi <= 78:
                action_alerts.append({"代碼": ticker, "訊號": "⚡ 動能突破", "原因": "強勢創新高"})
        elif cur_p <= (ma20 - (atr * atr_multiplier)):
            action_alerts.append({"代碼": ticker, "訊號": "🔥 強力買入", "原因": "空頭極端超賣"})
            
    except Exception: pass

# 輸出結果
st.header("🚨 今日核心執行 ACTION 面板")
if action_alerts: st.dataframe(pd.DataFrame(action_alerts), use_container_width=True)
else: st.info("🧘 今日無標的觸發決策條件。")

# 繪圖區
st.header("🔍 個股動態軌道驗證 (3年期)")
selected_stock = st.selectbox("選擇個股：", active_tickers)
if selected_stock:
    df = yf.Ticker(selected_stock).history(period="3y")
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA200'] = df['Close'].rolling(200).mean()
    df['ATR'] = (df['High']-df['Low']).rolling(14).mean()
    df['RSI'] = calculate_rsi(df['Close'], 14)
    df['H20'] = df['High'].shift(1).rolling(20).max()
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))
    
    ann = []
    for date, row in df.dropna().iterrows():
        if row['MA20'] >= row['MA200'] and row['Close'] <= (row['MA20'] - row['ATR']*atr_multiplier):
            ann.append(dict(x=date, y=row['Low'], text="🔥", showarrow=True, bgcolor="green", font=dict(color="white")))
        elif row['MA20'] >= row['MA200'] and row['Close'] > row['H20'] and 60 <= row['RSI'] <= 78:
            ann.append(dict(x=date, y=row['High'], text="⚡", showarrow=True, bgcolor="orange", font=dict(color="white")))
            
    fig.update_layout(height=500, template="plotly_white", annotations=ann)
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 綠色【🔥】代表左側抄底；橘色【⚡】代表安全閥控制下的右側動能上車。")
