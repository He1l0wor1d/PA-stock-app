import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import re

st.set_page_config(layout="wide", page_title="股票決策系統")
st.title("🦅 美股+台股『極簡五等燈號』自動化決策系統")
st.markdown("本系統已將繁雜指標降維，將多空結構簡化為**三大狀態**，並依據您設定的**MA20對稱 ATR 網格**給予五等 Action 建議。")

# ==============================================================================
# 🌐 第一層：全球總體經濟與市場情緒觀測站
# ==============================================================================
st.markdown("### 🌐 全球總體經濟與市場情緒觀測站")
macro_col1, macro_col2, macro_col3 = st.columns([1, 1, 2])

with macro_col1:
    st.markdown("##### 🧭 恐懼與貪婪指標 (Fear & Greed)")
    fg_value = 65  
    if fg_value >= 75: fg_status = "🚨 極度貪婪"
    elif fg_value >= 55: fg_status = "🟢 貪婪"
    elif fg_value >= 45: fg_status = "⚪ 中性"
    elif fg_value >= 25: fg_status = "🟡 恐懼"
    else: fg_status = "❄️ 極度恐懼"
        
    st.metric(label=f"大盤情緒狀態: {fg_status}", value=f"{fg_value} / 100")
    st.progress(fg_value / 100)
    st.caption("💡 提示：網格交易者應注意，大盤進入『極度貪婪』時應提高減倉意識。")

with macro_col2:
    st.markdown("##### 📊 席勒本益比 (Shiller PE)")
    shiller_pe = 31.5  
    historical_mean = 17.1
    deviation = ((shiller_pe - historical_mean) / historical_mean) * 100
    st.metric(label="S&P 500 CAPE Ratio", value=f"{shiller_pe:.1f}", delta=f"高於歷史均值 {deviation:.1f}%", delta_color="inverse")
    st.caption(f"歷史平均值: {historical_mean} | 超過 30 代表美股長線估值偏貴。")

with macro_col3:
    st.markdown("##### 📅 本週關鍵財經數據行事曆")
    calendar_data = {
        "公佈日期": ["05/18 (一)", "05/19 (二)", "05/20 (三)", "05/21 (四)", "05/22 (五)"],
        "關鍵數據 / 財經大事": ["紐約聯儲製造業指數", "RBA 貨幣政策紀要", "EIA 原油庫存", "Fed 貨幣政策紀要", "美國 4 月核心 PCE"],
        "市場預期與結論": ["✅ 實際值 -4.2，築底回溫", "⏳ 緊盯大宗商品態度", "⏳ 牽動能源板塊網格", "🔮 釋放降息終點密碼", "🔮 預期年增率 2.6%"]
    }
    st.dataframe(pd.DataFrame(calendar_data), use_container_width=True, hide_index=True)

# ==============================================================================
# ✨ 第三層：AGI 2027 敘事與 SALP (13F) 聰明錢觀測站（完美歸位在市場指引之後）
# ==============================================================================
st.markdown("### 🧠 AGI 2027 敘事與 SALP (13F) 聰明錢觀測站")
salp_col1, salp_col2 = st.columns([1, 1.8])

with salp_col1:
    st.markdown("##### 🔋 AGI 算力進度與物理瓶頸預警")
    st.metric(label="兆元美元集群投資進度", value="約 35%", delta="Capex 持續上修", delta_color="normal")
    st.progress(0.35)
    st.info("💡 **SALP 觀點**：AI 發展最大限制是「天然氣產量」與「變壓器交付」。AI 必須插電，電力層是未來硬資產。")

with salp_col2:
    st.markdown("##### 🏦 SALP 基金敘事層級持倉")
    salp_data = {
        "敘事層級": ["⚡ 電力層 (Power)", "☁️ AI 雲端 (AI Cloud)", "🌐 光通訊 (Photonics)", "🖥️ 運算層 (Compute)"],
        "代表標的": ["BE, CEG, VST", "CRWV, CORZ, IREN", "GLW, COHR", "NVDA, SMH, TSM"],
        "籌碼動向": ["📈 長期做多", "📈 持續加倉", "🔍 戰略佈局", "🛡️ 買入賣權避險"],
        "內化視角": ["防禦力與剛需最強", "現金流紅利即刻落地", "解決數據傳輸延遲", "防範估值擁擠泡沫"]
    }
    st.dataframe(pd.DataFrame(salp_data), use_container_width=True, hide_index=True)

st.markdown("---")

# 全量股票資料庫
INITIAL_SECTOR_MAP = {
    "TSM": "晶圓代工製程", "ASML": "晶圓代工製程", "AMAT": "晶圓代工製程", "LRCX": "晶圓代工製程", 
    "FORM": "晶圓代工製程", "INTC": "晶圓代工製程", "SNPS": "晶圓代工製程", "TSEM": "晶圓代工製程", 
    "AXTI": "晶圓代工製程", "SIMO": "晶圓代工製程", "ALAB": "晶圓代工製程", "SMH": "晶圓代工製程",
    "CSCO": "光通訊與網通", "ANET": "光通訊與網通", "GLW": "光通訊與網通", "COHR": "光通訊與網通", 
    "LITE": "光通訊與網通", "AAOI": "光通訊與網通", "FN": "光通訊與網通", "CIEN": "光通訊與網通", 
    "NOK": "光通訊與網通",  
    "DRAM": "記憶體與儲存", "MU": "記憶體與儲存", "SNDK": "記憶體與儲存", "RMBS": "記憶體與儲存", "SITM": "記憶體與儲存",
    "NEE": "電網設備基建", "GEV": "電網設備基建", "ETN": "電網設備基建", "PWR": "電網設備基建",
    "VRT": "機房液冷散熱", "MOD": "機房液冷散熱", "3017.TW": "機房液冷散熱",
    "CEG": "核能與天然氣", "VST": "核能與天然氣", "ENPH": "綠能與微電網", "SEDG": "綠能與微電網",
    "SOXX": "AI晶片與設計", "XSD": "AI晶片與設計", "NVDA": "AI晶片與設計", "AVGO": "AI晶片與設計", 
    "AMD": "AI晶片與設計", "QCOM": "AI晶片與設計", "MRVL": "AI晶片與設計", "TXN": "AI晶片與設計", 
    "ADI": "AI晶片與設計", "ON": "AI晶片與設計", "MPWR": "AI晶片與設計", "NVTS": "AI晶片與設計", "2454.TW": "AI晶片與設計",
    "QQQ": "市值型大盤", "MAGS": "市值型大盤", "MSFT": "AI巨頭與軟體", "AAPL": "AI巨頭與軟體", 
    "GOOGL": "AI巨頭與軟體", "AMZN": "AI巨頭與軟體", "META": "AI巨頭與軟體", "PLTR": "AI巨頭與軟體", 
    "NOW": "AI巨頭與軟體", "ORCL": "AI巨頭與軟體", "APP": "AI巨頭與軟體", "NET": "AI巨頭與軟體", 
    "CRWV": "AI巨頭與軟體", "2317.TW": "AI巨頭與軟體", "2382.TW": "AI巨頭與軟體", "CBRS": "AI巨頭與軟體",
    "ARKX": "航太太空國防", "NASA": "航太太空國防", "LMT": "航太太空國防", "RTX": "航太太空國防", 
    "BA": "航太太防航太", "RDW": "航太太空國防", "RKLB": "航太太空國防", "ASTS": "航太太空國防", "ONDS": "航太太空國防",
    "XOM": "傳統能源礦產", "OXY": "傳統能源礦產", "EQT": "傳統能源礦產",
    "LLY": "生技醫療科技", "TEM": "生技醫療科技", "GRAL": "生技醫療科技", "ILMN": "生技醫療科技",
    "JPM": "金融資產管理", "GS": "金融資產管理", "BLK": "金融資產管理", "BX": "金融資產管理", 
    "SOFI": "金融資產管理", "HOOD": "金融資產管理", "SEI": "金融資產管理",
    "TSLA": "智能車新能源", "BYDDF": "智能車新能源", "MSTR": "數位資產科技", 
    "BRK-B": "綜合控股投資", "GLD": "綜合控股投資", "SHLD": "綜合控股投資", "NBIS": "綜合控股投資",
    "2330.TW": "晶圓代工製程", "0050.TW": "市值型大盤", "2851.TW": "金融再保險", "5607.TW": "航空航運物流",
}

if "sector_map" not in st.session_state: st.session_state.sector_map = INITIAL_SECTOR_MAP.copy()

all_current_tickers = sorted(list(st.session_state.sector_map.keys()))
active_tickers = st.sidebar.multiselect("💡 觀察名單管理", options=all_current_tickers, default=all_current_tickers)

# ==============================================================================
# 🎮 核心狀態控制區與雙向聯動優化
# ==============================================================================
st.sidebar.header("🎯 策略快速情境預設")

# 初始化 session state 預設值
if "p_atr" not in st.session_state: st.session_state.p_atr = 1.3
if "p_rsi" not in st.session_state: st.session_state.p_rsi = 34
if "p_drop" not in st.session_state: st.session_state.p_drop = 5
if "p_bias" not in st.session_state: st.session_state.p_bias = 4
if "strategy_selection" not in st.session_state: st.session_state.strategy_selection = "💎 中等型 (價值)"

# 定義標準策略的精確對照表，用來比對使用者有沒有動過參數
STRATEGY_MAP = {
    "🛡️ 保延型 (抄底)": {"atr": 1.8, "rsi": 29, "drop": 8, "bias": 6},
    "💎 中等型 (價值)": {"atr": 1.3, "rsi": 34, "drop": 5, "bias": 4},
    "⚡ 積極型 (網格)": {"atr": 0.6, "rsi": 45, "drop": 2, "bias": 2}
}

# 渲染頂部按鈕組
selected_strategy = st.sidebar.segmented_control(
    "選擇運行策略：",
    options=["🛡️ 保守型 (抄底)", "💎 中等型 (價值)", "⚡ 積極型 (網格)", "🎛️ 自訂微調"],
    default=st.session_state.strategy_selection,
    key="strategy_selector"
)

# 如果使用者點擊了三大標準策略按鈕，強制重置滑桿參數
if selected_strategy and selected_strategy != st.session_state.strategy_selection:
    st.session_state.strategy_selection = selected_strategy
    if selected_strategy == "🛡️ 保守型 (抄底)":
        st.session_state.p_atr = 1.8         
        st.session_state.p_rsi = 29          
        st.session_state.p_drop = 8          
        st.session_state.p_bias = 6          
    elif selected_strategy == "💎 中等型 (價值)":
        st.session_state.p_atr = 1.3         
        st.session_state.p_rsi = 34          
        st.session_state.p_drop = 5          
        st.session_state.p_bias = 4          
    elif selected_strategy == "⚡ 積極型 (網格)":
        st.session_state.p_atr = 0.6         
        st.session_state.p_rsi = 45          
        st.session_state.p_drop = 2          
        st.session_state.p_bias = 2          
    st.rerun()

st.sidebar.header("📊 對稱網格參數微調")
atr_period = 14

# 渲染參數滑桿
atr_multiplier = st.sidebar.slider("自訂網格 ATR 倍數 (x)", 0.5, 3.0, value=st.session_state.p_atr, step=0.1)
rsi_filter_val = st.sidebar.slider("RSI 超賣過濾限制", 15, 45, value=st.session_state.p_rsi, step=1)
min_drop_pct = st.sidebar.slider("📉 同週內二次補槍必備「再跌幅門檻 (%)」", 2, 15, value=st.session_state.p_drop, step=1)
extreme_ma200_bias = st.sidebar.slider("💥 盤中跌破年線負乖離解鎖門檻 (%)", 3, 20, value=st.session_state.p_bias, step=1)

# 🛠️ 修正 (2)：當滑桿參數被更動、不再符合標準策略數值時，高亮狀態立刻自動強制切換成「🎛️ 自訂微調」
is_any_slider_changed = (
    atr_multiplier != st.session_state.p_atr or 
    rsi_filter_val != st.session_state.p_rsi or 
    min_drop_pct != st.session_state.p_drop or 
    extreme_ma200_bias != st.session_state.p_bias
)

if is_any_slider_changed:
    st.session_state.p_atr = atr_multiplier
    st.session_state.p_rsi = rsi_filter_val
    st.session_state.p_drop = min_drop_pct
    st.session_state.p_bias = extreme_ma200_bias
    st.session_state.strategy_selection = "🎛️ 自訂微調"
    st.rerun()

use_market_filter = st.sidebar.checkbox("啟用大盤多空防護鎖 (S&P500破年線時全面暫停強買)", value=True)

# 頂部戰略指示牌提示
st.markdown(f"##### ⚖️ 當前引擎運行狀態：`{st.session_state.strategy_selection}` (滑桿參數：ATR {st.session_state.p_atr}x / RSI {st.session_state.p_rsi} / 再跌門檻 {st.session_state.p_drop}% / 年線負乖離 {st.session_state.p_bias}%)")
st.caption("💡 量化引擎已完全解耦。所有策略判定100%只依據滑桿絕對數值，絕無隱藏額外限制，保證各策略與特調引信完全一視同仁。")

start_date = (datetime.now() - timedelta(days=365 * 3)).strftime('%Y-%m-%d')
summary_data = []
action_alerts = []
action_rank = {"🔥 強力買入": 0, "🟢 買入": 1, "⚪ 觀望": 2, "🔴 賣出": 3, "🚨 強力賣出": 4}
