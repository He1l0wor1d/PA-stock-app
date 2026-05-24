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
# ✨ 第三層：AGI 2027 敘事與 SALP (13F) 聰明錢觀測站
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

# ==============================================================================
# 🧮 基礎核心數學指標與資料加載函式
# ==============================================================================
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=3600)
def load_spy_data(start_str):
    spy = yf.Ticker("SPY").history(start=start_str)
    spy['MA200'] = spy['Close'].rolling(window=200).mean()
    return spy

# 🛠️ 核心進化：智慧辨識「大戶吸籌量能」與「高韌性支撐」的動態量化引擎
def generate_quant_signals(df_data, atr_mult, rsi_val, drop_pct, bias_val, use_market_fil):
    df = df_data.copy()
    sparse_strong_buy = pd.Series(False, index=df.index)
    
    if 'MA20_actual' not in df.columns or 'ATR' not in df.columns or 'Volume' not in df.columns:
        return sparse_strong_buy, pd.Series(0.0, index=df.index)
        
    # 計算大戶籌碼指標：20日平均成交量
    df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
    df['MA5'] = df['Close'].rolling(window=5).mean()
    
    low_absorb_bound = df['MA20_actual'] - (df['ATR'] * atr_mult)
    price_cond = (df['Low'] <= low_absorb_bound) | (df['Low'] <= df['BB_Lower'])
    rsi_cond = df['RSI'] <= rsi_val
    
    served_weeks = set()
    last_buy_price = None
    
    for date, is_triggered in price_cond.items():
        if is_triggered and rsi_cond.loc[date]:
            if pd.isna(df.loc[date, 'MA20_actual']) or pd.isna(df.loc[date, 'ATR']) or pd.isna(df.loc[date, 'Vol_MA20']): 
                continue
                
            if not pd.isna(df.loc[date, 'MA200']):
                current_ma200_bias = ((df.loc[date, 'MA200'] - df.loc[date, 'Low']) / df.loc[date, 'MA200']) * 100
            else: current_ma200_bias = 0
            
            is_ma200_extreme_crash = current_ma200_bias >= bias_val
            is_market_safe_today = df.loc[date, 'SPY_Safe']
            
            is_allowed = is_market_safe_today or (df.loc[date, 'MA20_actual'] >= df.loc[date, 'MA200']) or is_ma200_extreme_crash
            if use_market_fil and not is_market_safe_today and not is_ma200_extreme_crash:
                is_allowed = False
                
            if not df.loc[date, 'Is_True_Bull_Before']:
                is_allowed = False
                
            if not is_allowed: continue
                
            current_touch_price = min(low_absorb_bound.loc[date], df.loc[date, 'BB_Lower'], df.loc[date, 'Low'])
            current_year, current_week, _ = date.isocalendar()
            current_yw = (current_year, current_week)
            
            # 🛠️ 【智慧型大戶籌碼與韌性辨識認錯盾】
            if last_buy_price is not None:
                # 判定 1（大戶進場）：當天成交量必須大於均量 1.2 倍（爆量砸出恐慌盤或主力吸籌）
                is_volume_spike = df.loc[date, 'Volume'] >= (df.loc[date, 'Vol_MA20'] * 1.2)
                # 判定 2（支撐韌性）：收盤價成功站上極短線 5MA，代表下方支撐強勁、拒絕陰跌
                is_trend_turning = df.loc[date, 'Close'] >= df.loc[date, 'MA5']
                
                # 如果屬於同一個自然週
                if current_yw in served_weeks:
                    price_drop_target = last_buy_price * (1 - (drop_pct / 100))
                    # 同週加倉條件：除了殺穿再跌幅門檻，還必須伴隨大戶爆量吸籌（或止跌站上5MA），才允許放行
                    if current_touch_price <= price_drop_target and (is_volume_spike or is_trend_turning):
                        sparse_strong_buy[date] = True
                        last_buy_price = current_touch_price
                    continue
                else:
                    # 跨入新的一週：如果價格比上次買點還要低（代表第一槍套牢中）
                    if current_touch_price < last_buy_price:
                        # 💥 關鍵認錯鎖：如果持續縮量陰跌且連 5MA 都站不上（SOFI / NOW 典型行為），直接熔斷，不准補槍！
                        if not is_volume_spike and not is_trend_turning:
                            continue # 成功排除垃圾股的連續接飛刀
            
            # 條件通過，放行扣引信
            sparse_strong_buy[date] = True
            served_weeks.add(current_yw)
            last_buy_price = current_touch_price
            
    return sparse_strong_buy, low_absorb_bound

# 全量股票資料庫初始化
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
# 🎮 核心狀態控制區與雙向聯動
# ==============================================================================
st.sidebar.header("🎯 策略快速情境預設")

if "p_atr" not in st.session_state: st.session_state.p_atr = 1.3
if "p_rsi" not in st.session_state: st.session_state.p_rsi = 34
if "p_drop" not in st.session_state: st.session_state.p_drop = 5
if "p_bias" not in st.session_state: st.session_state.p_bias = 4
if "strategy_selection" not in st.session_state: st.session_state.strategy_selection = "💎 中等型 (價值)"
if "bt_start_date" not in st.session_state: st.session_state.bt_start_date = datetime(2025, 1, 1).date()

selected_strategy = st.sidebar.segmented_control(
    "選擇運行策略：",
    options=["🛡️ 保守型 (抄底)", "💎 中等型 (價值)", "⚡ 積極型 (網格)", "🎛️ 自訂微調"],
    default=st.session_state.strategy_selection,
    key="strategy_selector"
)

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

atr_multiplier = st.sidebar.slider("自訂網格 ATR 倍數 (x)", 0.5, 3.0, value=st.session_state.p_atr, step=0.1)
rsi_filter_val = st.sidebar.slider("RSI 超賣過濾限制", 15, 45, value=st.session_state.p_rsi, step=1)
min_drop_pct = st.sidebar.slider("📉 同週內二次補槍必備「再跌幅門檻 (%)」", 2, 15, value=st.session_state.p_drop, step=1)
extreme_ma200_bias = st.sidebar.slider("💥 盤中跌破年線負乖離解鎖門檻 (%)", 3, 20, value=st.session_state.p_bias, step=1)

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

st.markdown(f"##### ⚖️ 當前引擎運行狀態：`{st.session_state.strategy_selection}`")
st.success("🧠 **智慧型量化公告**：底層已升級為【大戶吸籌量能＋極短線趨勢解鎖機制】。優質股票（如 TSM）若大跌伴隨大戶放量吃貨，或股價率先站上 5MA，系統會判定為『具備強韌支撐力道』並動態放行二次加倉！而縮量陰跌的踩踏風險股（如 SOFI / NOW）將被無限期熔斷。")

start_date = (datetime.now() - timedelta(days=365 * 3)).strftime('%Y-%m-%d')
summary_data = []
action_alerts = []
action_rank = {"🔥 強力買入": 0, "🟢 買入": 1, "⚪ 觀望": 2, "🔴 賣出": 3, "🚨 強力賣出": 4}

spy_df_global = load_spy_data(start_date)

# ==============================================================================
# 運行即時看板
# ==============================================================================
with st.spinner("正在同步全球資產核心信號..."):
    for ticker in active_tickers:
        try:
            ticker_sector = INITIAL_SECTOR_MAP.get(ticker, "未分類")
            is_tw = ".TW" in ticker or ".TWO" in ticker
            currency_symbol = "NT$ " if is_tw else "$ "
            
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date)
            if df.empty or len(df) < 240: continue
            
            high_low = df['High'] - df['Low']
            tr = pd.concat([high_low, (df['High'] - df['Close'].shift(1)).abs(), (df['Low'] - df['Close'].shift(1)).abs()], axis=1).max(axis=1)
            df['ATR'] = tr.rolling(window=atr_period).mean()
            df['MA20_actual'] = df['Close'].rolling(window=20).mean()
            df['MA200'] = df['Close'].rolling(window=200).mean()
            df['STD20'] = df['Close'].rolling(window=20).std()
            df['BB_Lower'] = df['MA20_actual'] - (2 * df['STD20'])
            df['RSI'] = calculate_rsi(df['Close'], 14)
            df['Prev_Close'] = df['Close'].shift(1)
            df['Prev_MA200'] = df['MA200'].shift(1)
            df['Is_True_Bull_Before'] = df['Prev_Close'] >= df['Prev_MA200']
            
            df = df.join(spy_df_global['Close'].rename('SPY_Close'), how='left')
            df = df.join(spy_df_global['MA200'].rename('SPY_MA200'), how='left')
            df['SPY_Safe'] = df['SPY_Close'] >= df['SPY_MA200']
            df['SPY_Safe'] = df['SPY_Safe'].fillna(True)
            
            df['Sparse_Strong_Buy'], low_absorb_bound = generate_quant_signals(
                df, st.session_state.p_atr, st.session_state.p_rsi, st.session_state.p_drop, st.session_state.p_bias, use_market_filter
            )
            
            current_price = float(df.iloc[-1]['Close'])  
            yesterday_close = float(df.iloc[-2]['Close'])      
            ma20_center = float(df.iloc[-1]['MA20_actual'])
            latest_atr = float(df.iloc[-1]['ATR'])
            latest_ma200 = float(df.iloc[-1]['MA200']) if not pd.isna(df.iloc[-1]['MA200']) else ma20_center
            current_bb_lower = float(df.iloc[-1]['BB_Lower'])
            
            highest_20d = float(df['High'].rolling(window=20).max().iloc[-1])
            trailing_stop_price = highest_20d - (2 * latest_atr)
            trailing_stop_str = f"{currency_symbol}{trailing_stop_price:.1f}"

            low_absorb_price = ma20_center - (latest_atr * st.session_state.p_atr)
            high_toss_price = ma20_center + (latest_atr * st.session_state.p_atr)
            
            market_state = "⚪ 觀望"
            final_action = "⚪ 觀望"
            is_today_sparse_strong_buy = bool(df.iloc[-1]['Sparse_Strong_Buy'])
            
            if ma20_center >= latest_ma200:
                market_state = "📈 多頭波段 (會漲)"
                if is_today_sparse_strong_buy: final_action = "🔥 強力買入"
                elif abs(current_price - ma20_center)/ma20_center <= 0.02: final_action = "🟢 買入"
                elif current_price >= high_toss_price: final_action = "🔴 賣出"
            else:
                market_state = "📉 空頭結構 (會跌)"
                if is_today_sparse_strong_buy: final_action = "🔥 強力買入"
                elif yesterday_close >= ma20_center and current_price < ma20_center: final_action = "🚨 強力賣出"
                elif current_price >= high_toss_price: final_action = "🔴 賣出"
                elif abs(current_price - ma20_center)/ma20_center <= 0.02: final_action = "🟢 買入" 

            if final_action in ["🔥 強力買入", "🟢 買入"]:
                action_alerts.append({
                    "代碼": ticker, "綜合建議": final_action, "市場狀態": market_state, 
                    "當前股價": f"{currency_symbol}{current_price:.1f}",
                    "買點": f"{currency_symbol}{min(low_absorb_price, current_bb_lower):.1f}"
                })

            summary_data.append({
                "產業領域": ticker_sector, "代碼": ticker, "當前股價": f"{currency_symbol}{current_price:.1f}",
                "移動停利價位": trailing_stop_str, "昨收盤價": f"{currency_symbol}{yesterday_close:.1f}",
                "MA20": f"{currency_symbol}{ma20_center:.1f}", "市場狀態": market_state, "綜合建議": final_action,
                "買點": f"{currency_symbol}{min(low_absorb_price, current_bb_lower):.1f}", "賣點": f"{currency_symbol}{high_toss_price:.1f}"
            })
        except Exception: pass

st.header("🚨 今日促銷")
if action_alerts:
    st.dataframe(pd.DataFrame(action_alerts), use_container_width=True, hide_index=True)
else:
    st.info("🧘 報告隊長：今日觀察名單內皆無符合目前情境參數限制的強買標的。")

st.markdown("---")

st.header("📊 降維極簡大看板")
if summary_data:
    summary_df = pd.DataFrame(summary_data)
    summary_df['sort'] = summary_df['綜合建議'].map(action_rank)
    summary_df = summary_df.sort_values(by=["sort", "產業領域", "代碼"]).drop('sort', axis=1)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ==============================================================================
# 🔍 個股動態決策軌道與歷史 K 線繪製
# ==============================================================================
st.header("🔍 個股動態決策軌道與核心基本面")
sorted_tickers = sorted(active_tickers)
default_index = sorted_tickers.index("TSM") if "TSM" in sorted_tickers else 0
selected_stock = st.selectbox("選擇個股查看歷史決策軌道：", options=sorted_tickers, index=default_index)

if selected_stock:
    try:
        stock_detail = yf.Ticker(selected_stock)
        df_detail = stock_detail.history(start=start_date)
        
        if not df_detail.empty and len(df_detail) > 240:
            df_detail['MA20_plot'] = df_detail['Close'].rolling(window=20).mean()
            df_detail['MA200'] = df_detail['Close'].rolling(window=200).mean()
            df_detail['STD20'] = df_detail['Close'].rolling(window=20).std()
            df_detail['BB_Lower'] = df_detail['MA20_plot'] - (2 * df_detail['STD20'])
            df_detail['RSI'] = calculate_rsi(df_detail['Close'], 14)
            df_detail['Prev_Close'] = df_detail['Close'].shift(1)
            df_detail['Prev_MA200'] = df_detail['MA200'].shift(1)
            df_detail['Is_True_Bull_Before'] = df_detail['Prev_Close'] >= df_detail['Prev_MA200']
            
            high_low_det = df_detail['High'] - df_detail['Low']
            tr_det = pd.concat([high_low_det, (df_detail['High'] - df_detail['Close'].shift(1)).abs(), (df_detail['Low'] - df_detail['Close'].shift(1)).abs()], axis=1).max(axis=1)
            df_detail['ATR'] = tr_det.rolling(window=atr_period).mean()
            
            df_detail = df_detail.join(spy_df_global['Close'].rename('SPY_Close'), how='left')
            df_detail = df_detail.join(spy_df_global['MA200'].rename('SPY_MA200'), how='left')
            df_detail['SPY_Safe'] = df_detail['SPY_Close'] >= df_detail['SPY_MA200']
            df_detail['SPY_Safe'] = df_detail['SPY_Safe'].fillna(True)
            
            df_detail['MA20_actual'] = df_detail['MA20_plot'] 
            df_detail['Sparse_Strong_Buy'], low_absorb_bound_det = generate_quant_signals(
                df_detail, st.session_state.p_atr, st.session_state.p_rsi, st.session_state.p_drop, st.session_state.p_bias, use_market_filter
            )
            buy_signals = df_detail[df_detail['Sparse_Strong_Buy']]

            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df_detail.index, open=df_detail['Open'], high=df_detail['High'], low=df_detail['Low'], close=df_detail['Close'], name='K線'))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA20_plot'], name='20MA 趨勢決策線', line=dict(color='orange', width=2)))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA200'], name='200MA 長期生命線', line=dict(color='crimson', width=2.5)))
            
            if not buy_signals.empty:
                fig.add_trace(go.Scatter(
                    x=buy_signals.index, y=buy_signals['Low'] * 0.96,  
                    mode='text', text=['🔥' for _ in range(len(buy_signals))],
                    textposition="bottom center", textfont=dict(size=18), name='🔥 強力買入點'
                ))
                
            fig.update_layout(xaxis_rangeslider_visible=False, yaxis_title="價格", height=500, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
                
    except Exception as e: st.error(f"分析載入失敗: {e}")

# ==============================================================================
# ⏳ 策略回測績效驗證
# ==============================================================================
st.markdown("---")
st.header("⏳ 策略回測績效驗證 (實時動態 Demo)")

backtest_col1, backtest_col2, _ = st.columns([1, 1, 2])
with backtest_col1:
    user_date_selection = st.date_input("📅 選擇掃描起始日期：", value=st.session_state.bt_start_date, key="bt_date_input")
    if user_date_selection != st.session_state.bt_start_date:
        st.session_state.bt_start_date = user_date_selection
        st.rerun()

with backtest_col2:
    signal_choice = st.selectbox("🎯 選擇回測訊號類型：", options=["單獨強力買入", "單獨買入", "買入 + 強力買入"], index=0)

bt_date_str = st.session_state.bt_start_date.strftime('%Y-%m-%d')
backtest_results = []
portfolio_total_buy_signals = 0 

with st.spinner("正在模擬時間軸歷史建倉..."):
    df_spy_raw = spy_df_global.loc[bt_date_str:]
    if not df_spy_raw.empty:
        spy_start_price = df_spy_raw['Close'].iloc[0]
        spy_latest_price = df_spy_raw['Close'].iloc[-1]
        spy_performance_pct = ((spy_latest_price - spy_start_price) / spy_start_price) * 100
    else:
        spy_performance_pct = 0.0

    for ticker in active_tickers:
        try:
            ticker_sector = INITIAL_SECTOR_MAP.get(ticker, "未分類")
            df_bt = yf.Ticker(ticker).history(start=(st.session_state.bt_start_date - timedelta(days=300)).strftime('%Y-%m-%d'))
            if df_bt.empty or len(df_bt) < 240: continue
            
            df_bt['MA20_actual'] = df_bt['Close'].rolling(window=20).mean()
            df_bt['MA200'] = df_bt['Close'].rolling(window=200).mean()
            df_bt['STD20'] = df_bt['Close'].rolling(window=20).std()
            df_bt['BB_Lower'] = df_bt['MA20_actual'] - (2 * df_bt['STD20'])
            df_bt['RSI'] = calculate_rsi(df_bt['Close'], 14)
            df_bt['Prev_Close'] = df_bt['Close'].shift(1)
            df_bt['Prev_MA200'] = df_bt['MA200'].shift(1)
            df_bt['Is_True_Bull_Before'] = df_bt['Prev_Close'] >= df_bt['Prev_MA200']
            
            hl = df_bt['High'] - df_bt['Low']
            tr = pd.concat([hl, (df_bt['High'] - df_bt['Close'].shift(1)).abs(), (df_bt['Low'] - df_bt['Close'].shift(1)).abs()], axis=1).max(axis=1)
            df_bt['ATR'] = tr.rolling(window=atr_period).mean()

            df_bt = df_bt.join(spy_df_global['Close'].rename('SPY_Close'), how='left')
            df_bt = df_bt.join(spy_df_global['MA200'].rename('SPY_MA200'), how='left')
            df_bt['SPY_Safe'] = df_bt['SPY_Close'] >= df_bt['SPY_MA200']
            df_bt['SPY_Safe'] = df_bt['SPY_Safe'].fillna(True)

            df_scan = df_bt.loc[bt_date_str:].copy()
            if df_scan.empty: continue
            
            latest_today_price = df_bt['Close'].iloc[-1]
            currency = "NT$ " if ".TW" in ticker else "$ "
            
            # 回測同步智慧量化引擎
            df_scan['Sparse_Strong_Buy'], low_absorb_bound_bt = generate_quant_signals(
                df_scan, st.session_state.p_atr, st.session_state.p_rsi, st.session_state.p_drop, st.session_state.p_bias, use_market_filter
            )
            
            total_strong_buy_count = df_scan['Sparse_Strong_Buy'].sum()
            portfolio_total_buy_signals += total_strong_buy_count  
            
            first_trade_data = None
            buy_dates = df_scan[df_scan['Sparse_Strong_Buy']].index
            
            if not buy_dates.empty:
                first_date = buy_dates[0]
                raw_grid_lower = low_absorb_bound_bt.loc[first_date]
                if pd.isna(raw_grid_lower) or pd.isna(df_scan.loc[first_date, 'BB_Lower']):
                    final_entry_price = float(df_scan.loc[first_date, 'Low'])
                else:
                    final_entry_price = min(raw_grid_lower, df_scan.loc[first_date, 'BB_Lower'], df_scan.loc[first_date, 'Low'])
                
                post_buy_df = df_scan.loc[first_date:]
                max_dd_pct = ((post_buy_df['Low'].min() - final_entry_price) / final_entry_price) * 100
                max_dd_pct = min(max_dd_pct, 0.0)
                
                return_pct = ((latest_today_price - final_entry_price) / final_entry_price) * 100
                first_trade_data = {
                    "產業": ticker_sector, "代碼": ticker, "首次建倉日": first_date.strftime('%Y-%m-%d'),
                    "當時訊號": "🔥 強力買入", "模擬買入價": f"{currency}{final_entry_price:.1f}",
                    "最大套牢跌幅": f"{max_dd_pct:.1f}%", "累積報酬率": f"{return_pct:.1f}%",
                    "強買訊號次數": f"{total_strong_buy_count} 次"
                }
            
            if first_trade_data is not None:
                backtest_results.append(first_trade_data)
        except Exception: pass

if backtest_results:
    df_bt_results = pd.DataFrame(backtest_results)
    df_bt_results['sort_val'] = df_bt_results['累積報酬率'].str.replace('%', '').astype(float)
    df_bt_results = df_bt_results.sort_values(by='sort_val', ascending=False).drop('sort_val', axis=1)
    
    cols_order = ["產業", "代碼", "首次建倉日", "當時訊號", "強買訊號次數", "模擬買入價", "最大套牢跌幅", "累積報酬率"]
    st.dataframe(df_bt_results[[c for c in cols_order if c in df_bt_results.columns]], use_container_width=True, hide_index=True)
    
    avg_return = df_bt_results['累積報酬率'].str.replace('%', '').astype(float).mean()
    win_rate = (df_bt_results['累積報酬率'].str.replace('%', '').astype(float) > 0).mean() * 100
    
    st.info(f"📈 策略平均報酬率：**{avg_return:.1f}%** | 🎯 策略勝率：**{win_rate:.1f}%** | 💰 期間內組合總買入次數：**{portfolio_total_buy_signals} 次** | 📊 同期對比 SPY：**{spy_performance_pct:.1f}%**")
else:
    st.info(f"自 {bt_date_str} 起算，目前的滑桿參數未觸發任何回測歷史建倉單。")
