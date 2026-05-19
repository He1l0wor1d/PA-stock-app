import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 網頁基本設定
st.set_page_config(layout="wide", page_title="股票決策系統")
st.title("🦅 美股+台股『極簡五等燈號』自動化決策系統")
st.markdown("本系統已將繁雜指標降維，將多空結構簡化為**三大狀態**，並依據您設定的**MA20對稱 ATR 網格**給予五等 Action 建議。")

# ==============================================================================
# 第一層：宏觀觀測站與 SALP 內化敘事
# ==============================================================================
st.markdown("### 🌐 全球總體經濟與市場情緒觀測站")
macro_col1, macro_col2, macro_col3 = st.columns([1, 1, 2])
with macro_col1:
    st.markdown("##### 🧭 恐懼與貪婪指標")
    fg_value = 65
    st.metric(label="大盤情緒", value=f"{fg_value} / 100")
    st.progress(fg_value / 100)
with macro_col2:
    st.markdown("##### 📊 席勒本益比 (Shiller PE)")
    st.metric(label="S&P 500 CAPE", value="31.5", delta="高於歷史均值 84%", delta_color="inverse")
with macro_col3:
    st.markdown("##### 📅 本週關鍵財經行事曆")
    st.dataframe(pd.DataFrame({
        "日期": ["05/18", "05/22"], "項目": ["製造業指數", "核心 PCE"], "結論": ["築底回溫", "預期 2.6%"]
    }), use_container_width=True, hide_index=True)

st.markdown("### 🧠 AGI 2027 敘事與 SALP (13F) 聰明錢觀測站")
salp_col1, salp_col2 = st.columns([1, 1.8])
with salp_col1:
    st.metric(label="AGI 算力投資進度", value="35%")
    st.progress(0.35)
    st.info("💡 **SALP 核心**：AI 瓶頸在於電力與變壓器，實體能源即是硬資產。")
with salp_col2:
    st.dataframe(pd.DataFrame({
        "層級": ["電力", "AI雲端", "光通訊", "運算"],
        "籌碼": ["做多", "加倉", "佈局", "避險(Put)"],
        "觀點": ["剛需防禦", "現金流紅利", "解決延遲", "留意估值擁擠"]
    }), use_container_width=True, hide_index=True)

st.markdown("---")

# ==============================================================================
# 2. 核心邏輯與看板
# ==============================================================================
INITIAL_SECTOR_MAP = {
    "2330.TW": "🇹🇼 半導體", "2851.TW": "🇹🇼 金融", "5607.TW": "🇹🇼 物流", "0050.TW": "🇹🇼 ETF",
    "NVDA": "運算", "BE": "電力", "CRWV": "雲端", "GLW": "光通訊"
}
if "sector_map" not in st.session_state: st.session_state.sector_map = INITIAL_SECTOR_MAP.copy()

active_tickers = st.sidebar.multiselect("💡 觀察名單", options=sorted(st.session_state.sector_map.keys()), default=list(INITIAL_SECTOR_MAP.keys()))
atr_multiplier = st.sidebar.slider("網格 ATR 倍數", 0.5, 2.5, 1.4, 0.1)

summary_data = []
for ticker in active_tickers:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")
        if df.empty: continue
        
        # 公允價值計算
        info = stock.info
        eps, pe = info.get('forwardEps') or info.get('trailingEps'), info.get('trailingPE') or 20
        fv = f"${(eps * pe):.1f}" if eps else "N/A"
        
        # 技術指標
        atr = pd.concat([(df['High']-df['Low']), (df['High']-df['Close'].shift(1)).abs()], axis=1).max(axis=1).rolling(14).mean().iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        curr = df['Close'].iloc[-1]
        
        summary_data.append({
            "代碼": ticker,
            "當前股價": f"{curr:.1f}",
            "公允價值": fv,
            "MA20": f"{ma20:.1f}",
            "建議": "🔥 買入" if curr <= (ma20 - atr * atr_multiplier) else "⚪ 觀望"
        })
    except: pass

st.header("📊 降維極簡大看板")
st.dataframe(pd.DataFrame(summary_data), use_container_width=True)

with st.expander("💡 投資決策參考守則"):
    st.markdown("""
    * **情境 A (買點 + 遠低於公允價值)：** **大膽買進**。技術與基本面共振，高安全邊際。
    * **情境 B (買點 + 高於公允價值)：** **縮小部位**。恐為接飛刀陷阱。
    * **情境 C (賣點 + 遠低於公允價值)：** **分批賣出，保留底倉**。基本面強，參與價值回歸。
    * **情境 D (賣點 + 高於公允價值)：** **果斷清倉**。技術面泡沫，執行離場紀律。
    """)
