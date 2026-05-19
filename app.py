import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# 1. 網頁基本設定
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
    if fg_value >= 75: fg_status = "🚨 極度貪婪 (Extreme Greed)"
    elif fg_value >= 55: fg_status = "🟢 貪婪 (Greed)"
    elif fg_value >= 45: fg_status = "⚪ 中性 (Neutral)"
    elif fg_value >= 25: fg_status = "🟡 恐懼 (Fear)"
    else: fg_status = "❄️ 極度恐懼 (Extreme Fear)"
        
    st.metric(label=f"大盤情緒狀態: {fg_status}", value=f"{fg_value} / 100")
    st.progress(fg_value / 100)
    st.caption("💡 提示：網格交易者應注意，大盤進入『極度貪婪』時應提高減倉意識。")

with macro_col2:
    st.markdown("##### 📊 席勒本益比 (Shiller PE)")
    shiller_pe = 31.5  
    historical_mean = 17.1
    deviation = ((shiller_pe - historical_mean) / historical_mean) * 100
    
    st.metric(label="S&P 500 CAPE Ratio", value=f"{shiller_pe}", delta=f"高於歷史均值 {deviation:.1f}%", delta_color="inverse")
    st.caption(f"歷史平均值: {historical_mean} | 超過 30 代表美股長線估值偏貴。")

with macro_col3:
    st.markdown("##### 📅 本週關鍵財經數據行事曆 (2026/05/18 - 05/22)")
    calendar_data = {
        "公佈日期": ["05/18 (一)", "05/19 (二)", "05/20 (三)", "05/21 (四)", "05/22 (五)"],
        "關鍵數據 / 財經大事項目": [
            "美國 5 月紐約聯儲製造業指數",
            "澳洲聯儲 (RBA) 貨幣政策會議紀要",
            "EIA 每週原油庫存變動數據",
            "聯準會 (Fed) 公布貨幣政策會議紀要",
            "美國 4 月核心 PCE 物價指數 (通膨核心)"
        ],
        "即時進度與數據結論 / 市場預期": [
            "✅ 已公布：實際值 -4.2 (優於預期 -7.5)，製造業築底回溫，多頭吃下定心丸。",
            "⏳ 今日焦點：市場緊盯澳洲對大宗商品與通膨的最新鷹鴿態度。",
            "⏳ 觀察中：原油走勢將直接牽動卡脖子傳統能源與礦產板塊的網格邊界。",
            "🔮 重大焦點：預期將釋放 2026 下半年降息終點利率的最新政策密碼。",
            "🔮 重大焦點：市場預期年增率維持在 2.6% 附近，若低於預期將利多科技股。"
        ]
    }
    calendar_df = pd.DataFrame(calendar_data)
    st.dataframe(calendar_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ==============================================================================
# 2. 內建核心產業與「卡脖子」供應鏈地圖 (核心標的已置頂)
# ==============================================================================
INITIAL_SECTOR_MAP = {
    "2330.TW": "🇹🇼 台股 - 半導體晶圓代工 (全球核心)", "2851.TW": "🇹🇼 台股 - 金融再保險",
    "5607.TW": "🇹🇼 台股 - 航空航運與物流", "0050.TW": "🇹🇼 台股 - 市值型 ETF (元大台灣50)",
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

if "sector_map" not in st.session_state: st.session_state.sector_map = INITIAL_SECTOR_MAP.copy()
all_current_tickers = sorted(list(st.session_state.sector_map.keys()))
active_tickers = st.sidebar.multiselect("💡 觀察名單管理", options=all_current_tickers, default=all_current_tickers)
atr_period = st.sidebar.slider("ATR 計算天數", 5, 22, 14)
atr_multiplier = st.sidebar.slider("自訂網格 ATR 倍數 (x)", 0.5, 2.5, 1.4, 0.1)

start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
summary_data, action_alerts = [], []
action_rank = {"🔥 強力買入": 0, "🟢 買入": 1, "⚪ 觀望": 2, "🔴 賣出": 3, "🚨 強力賣出": 4}

with st.spinner("正在提煉五等核心 ACTION 決策與公允價值運算..."):
    for ticker in active_tickers:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date)
            if df.empty or len(df) < 220: continue
            
            # --- 公允價值運算 ---
            info = stock.info
            eps, hist_pe, growth, dps, div_yield = info.get('forwardEps') or info.get('trailingEps'), info.get('trailingPE') or info.get('forwardPE'), info.get('earningsGrowth'), info.get('dividendRate'), info.get('dividendYield')
            vals = [eps * hist_pe] if (eps and hist_pe and eps > 0 and hist_pe > 0) else []
            if eps and growth and eps > 0 and growth > 0: vals.append(eps * growth * 100 * 1.0)
            if dps and div_yield and dps > 0 and div_yield > 0: vals.append(dps / div_yield)
            fair_value_str = f"${min(vals):.1f} ~ ${max(vals):.1f}" if vals else "數據不足"

            # --- 技術指標 ---
            df['ATR'] = pd.concat([(df['High']-df['Low']), (df['High']-df['Close'].shift(1)).abs(), (df['Low']-df['Close'].shift(1)).abs()], axis=1).max(axis=1).rolling(atr_period).mean()
            df['MA20'] = df['Close'].rolling(window=20).mean()
            curr, yesterday, ma20, atr = float(df['Close'].iloc[-1]), float(df['Close'].iloc[-2]), float(df['MA20'].iloc[-1]), float(df['ATR'].iloc[-1])
            low_b, high_b = ma20 - (atr * atr_multiplier), ma20 + (atr * atr_multiplier)
            
            # --- 邏輯判定 ---
            final_action = "⚪ 觀望"
            if curr <= low_b * 1.005: final_action = "🔥 強力買入"
            elif curr >= high_b * 0.995: final_action = "🚨 強力賣出"
            
            summary_data.append({"代碼": ticker, "當前股價": f"{curr:.1f}", "公允價值區間": fair_value_str, "MA20": f"{ma20:.1f}", "綜合建議": final_action})
        except: pass

st.header("📊 降維極簡大看板")
st.dataframe(pd.DataFrame(summary_data), use_container_width=True)

with st.expander("💡 投資決策參考守則 (公允價值對照)"):
    st.markdown("""
    * **情境 A (買點 + 遠低於公允價值)：** **大膽買進**。技術面跌到位且具備高安全邊際。
    * **情境 B (買點 + 高於公允價值)：** **縮小部位或放棄**。可能為價值陷阱，避免接飛刀。
    * **情境 C (賣點 + 遠低於公允價值)：** **分批賣出，保留底倉**。基本面強，可參與價值回歸。
    * **情境 D (賣點 + 高於公允價值)：** **果斷清倉高拋**。泡沫超漲，執行離場紀律。
    """)
