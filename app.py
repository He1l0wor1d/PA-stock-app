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
    calendar_df = pd.DataFrame(calendar_data)
    st.dataframe(calendar_df, use_container_width=True, hide_index=True)

st.markdown("---")

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

with st.sidebar.expander("➕ 新增觀察股票", expanded=False):
    add_ticker = st.text_input("輸入代碼 (美股如: NVDA / 台股如: 2317.TW)").strip().upper()
    add_sector = st.selectbox("產業分類", sorted(list(set(st.session_state.sector_map.values()))))
    if st.button("確認新增") and add_ticker:
        st.session_state.sector_map[add_ticker] = add_sector
        st.rerun()

all_current_tickers = sorted(list(st.session_state.sector_map.keys()))
active_tickers = st.sidebar.multiselect("💡 觀察名單管理 (點 X 刪除)", options=all_current_tickers, default=all_current_tickers)

# ==============================================================================
# 🎮 三種風險偏好策略情境按鈕重構區（精準拉開出手頻率與核心勝率）
# ==============================================================================
st.sidebar.header("🎯 策略快速情境預設（一鍵切換）")

if "p_atr" not in st.session_state: st.session_state.p_atr = 1.4
if "p_rsi" not in st.session_state: st.session_state.p_rsi = 32
if "p_window" not in st.session_state: st.session_state.p_window = 30
if "p_drop" not in st.session_state: st.session_state.p_drop = 5
if "p_bias" not in st.session_state: st.session_state.p_bias = 8

btn_col1, btn_col2, btn_col3 = st.sidebar.columns(3)

with btn_col1:
    if st.button("🛡️ 保守型\n(大跌抄底)"):
        st.session_state.p_atr = 2.2         # 網格極端放寬，杜絕中途進場
        st.session_state.p_rsi = 24          # RSI 鎖死極端恐慌
        st.session_state.p_window = 45       # 拉長排他時間防止連環亮燈
        st.session_state.p_drop = 8          # 二次買入條件極其嚴苛
        st.session_state.p_bias = 7          # 配合修正A精準抓取大崩盤極值底
        st.rerun()

with btn_col2:
    if st.button("💎 中等型\n(價值低估)"):
        st.session_state.p_atr = 1.3         # 標準網格下限
        st.session_state.p_rsi = 34          # 常態板塊價值修正區
        st.session_state.p_window = 25       # 正常波段防守
        st.session_state.p_drop = 5          # 穩定加倉
        st.session_state.p_bias = 4          # 捕捉中度偏離
        st.rerun()

with btn_col3:
    if st.button("⚡ 積極型\n(高頻網格)"):
        st.session_state.p_atr = 0.7         # 網格極度敏感，輕微修正即觸發
        st.session_state.p_rsi = 45          # RSI 高位寬鬆，買在半山腰
        st.session_state.p_window = 10       # 10天即可重複扣引信
        st.session_state.p_drop = 2          # 再跌2%就瘋狂亮燈
        st.session_state.p_bias = 2          # 輕微年線負乖離即破鎖
        st.rerun()

st.sidebar.header("📊 對稱網格參數微調")
atr_period = 14

atr_multiplier = st.sidebar.slider("自訂網格 ATR 倍數 (x)", 0.5, 3.0, value=st.session_state.p_atr, step=0.1)
rsi_filter_val = st.sidebar.slider("RSI 超賣過濾限制", 15, 45, value=st.session_state.p_rsi, step=1)
wave_window_days = st.sidebar.slider("🛡️ 空間排他時間視窗 (天)", 10, 90, value=st.session_state.p_window, step=5)
min_drop_pct = st.sidebar.slider("📉 視窗內二次強買必備「再跌幅門檻」", 2, 15, value=st.session_state.p_drop, step=1)
extreme_ma200_bias = st.sidebar.slider("💥 修正A：盤中跌破年線 (200MA) 負乖離強制解鎖門檻 (%)", 3, 20, value=st.session_state.p_bias, step=1)

use_market_filter = st.sidebar.checkbox("啟用大盤多空防護鎖 (S&P500破年線時全面暫停強買)", value=True)

start_date = (datetime.now() - timedelta(days=365 * 3)).strftime('%Y-%m-%d')
summary_data = []
action_alerts = []
action_rank = {"🔥 強力買入": 0, "🟢 買入": 1, "⚪ 觀望": 2, "🔴 賣出": 3, "🚨 強力賣出": 4}

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

spy_df_global = load_spy_data(start_date)

with st.spinner("正在提煉核心決策..."):
    for ticker in active_tickers:
        try:
            ticker_sector = st.session_state.sector_map.get(ticker, "未分類")
            is_tw = ".TW" in ticker or ".TWO" in ticker
            currency_symbol = "NT$ " if is_tw else "$ "
            
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date)
            if df.empty or len(df) < 220: continue
            
            high_low = df['High'] - df['Low']
            tr = pd.concat([high_low, (df['High'] - df['Close'].shift(1)).abs(), (df['Low'] - df['Close'].shift(1)).abs()], axis=1).max(axis=1)
            df['ATR'] = tr.rolling(window=atr_period).mean()
            df['MA20_actual'] = df['Close'].rolling(window=20).mean()
            df['MA200'] = df['Close'].rolling(window=200).mean()
            df['STD20'] = df['Close'].rolling(window=20).std()
            df['BB_Lower'] = df['MA20_actual'] - (2 * df['STD20'])
            df['RSI'] = calculate_rsi(df['Close'], 14)
            
            df['SPY_Close'] = spy_df_global['Close']
            df['SPY_MA200'] = spy_df_global['MA200']
            df['SPY_Safe'] = df['SPY_Close'] >= df['SPY_MA200']
            df['SPY_Safe'] = df['SPY_Safe'].fillna(True)
            
            low_absorb_bound = df['MA20_actual'] - (df['ATR'] * atr_multiplier)
            price_cond = (df['Low'] <= low_absorb_bound) | (df['Low'] <= df['BB_Lower'])
            rsi_cond = df['RSI'] <= rsi_filter_val
            raw_panic_signal = rsi_cond & price_cond & (df['SPY_Safe'] | (df['MA20_actual'] >= df['MA200']))
            if use_market_filter:
                raw_panic_signal = raw_panic_signal & df['SPY_Safe']
            
            sparse_strong_buy = pd.Series(False, index=df.index)
            last_buy_date = None
            last_buy_price = None
            
            for date, is_triggered in raw_panic_signal.items():
                if is_triggered:
                    if not pd.isna(df.loc[date, 'MA200']):
                        current_ma200_bias = ((df.loc[date, 'MA200'] - df.loc[date, 'Low']) / df.loc[date, 'MA200']) * 100
                    else:
                        current_ma200_bias = 0
                    
                    is_ma200_extreme_crash = current_ma200_bias >= extreme_ma200_bias
                    current_touch_price = min(low_absorb_bound.loc[date], df.loc[date, 'BB_Lower'], df.loc[date, 'Low'])
                    
                    if last_buy_date is None:
                        sparse_strong_buy[date] = True
                        last_buy_date = date
                        last_buy_price = current_touch_price
                    else:
                        days_passed = (date - last_buy_date).days
                        
                        if is_ma200_extreme_crash:
                            sparse_strong_buy[date] = True
                            last_buy_date = date
                            last_buy_price = current_touch_price
                        elif days_passed > wave_window_days:
                            sparse_strong_buy[date] = True
                            last_buy_date = date
                            last_buy_price = current_touch_price
                        else:
                            price_drop_target = last_buy_price * (1 - (min_drop_pct / 100))
                            if current_touch_price <= price_drop_target:
                                sparse_strong_buy[date] = True
                                last_buy_date = date
                                last_buy_price = current_touch_price

            df['Sparse_Strong_Buy'] = sparse_strong_buy
            
            current_price = float(df.iloc[-1]['Close'])  
            yesterday_close = float(df.iloc[-2]['Close'])      
            ma20_center = float(df.iloc[-1]['MA20_actual'])
            latest_atr = float(df.iloc[-1]['ATR'])
            latest_ma200 = float(df.iloc[-1]['MA200']) if not pd.isna(df.iloc[-1]['MA200']) else ma20_center
            current_bb_lower = float(df.iloc[-1]['BB_Lower'])
            
            highest_20d = float(df['High'].rolling(window=20).max().iloc[-1])
            trailing_stop_price = highest_20d - (2 * latest_atr)
            trailing_stop_str = f"{currency_symbol}{trailing_stop_price:.1f}"

            low_absorb_price = ma20_center - (latest_atr * atr_multiplier)
            high_toss_price = ma20_center + (latest_atr * atr_multiplier)
            
            market_state = "⚪ 觀望"
            final_action = "⚪ 觀望"
            
            is_today_sparse_strong_buy = bool(df.iloc[-1]['Sparse_Strong_Buy'])
            
            if ma20_center >= latest_ma200:
                market_state = "📈 多頭波段 (會漲)"
                if is_today_sparse_strong_buy: 
                    final_action = "🔥 強力買入"
                elif abs(current_price - ma20_center)/ma20_center <= 0.02: 
                    final_action = "🟢 買入"
                elif current_price >= high_toss_price: 
                    final_action = "🔴 賣出"
            else:
                market_state = "📉 空頭結構 (會跌)"
                if is_today_sparse_strong_buy:
                    final_action = "🔥 強力買入"
                elif yesterday_close >= ma20_center and current_price < ma20_center: 
                    final_action = "🚨 強力賣出"
                elif current_price >= high_toss_price: 
                    final_action = "🔴 賣出"
                elif abs(current_price - ma20_center)/ma20_center <= 0.02:
                    final_action = "🟢 買入" 

            if final_action in ["🔥 強力買入", "🟢 買入"]:
                action_alerts.append({
                    "代碼": ticker, 
                    "綜合建議": final_action, 
                    "市場狀態": market_state, 
                    "當前股價": f"{currency_symbol}{current_price:.1f}",
                    "買點": f"{currency_symbol}{min(low_absorb_price, current_bb_lower):.1f}",
                    "MA20": f"{currency_symbol}{ma20_center:.1f}"
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
    st.info("🧘 報告隊長：今日名單內皆無符合目前情境參數限制的促銷標的。")

st.markdown("---")

st.header("📊 降維極簡大看板 (點擊表頭欄位名稱可直接進行實時排序)")
if summary_data:
    summary_df = pd.DataFrame(summary_data)
    summary_df['sort'] = summary_df['綜合建議'].map(action_rank)
    summary_df = summary_df.sort_values(by=["sort", "產業領域", "代碼"]).drop('sort', axis=1)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ==============================================================================
# 🔍 個股動態決策軌道與核心基本面
# ==============================================================================
st.header("🔍 個股動態決策軌道與核心基本面")

sorted_tickers = sorted(active_tickers)
default_index = sorted_tickers.index("TSM") if "TSM" in sorted_tickers else 0

selected_stock = st.selectbox(
    "選擇個股查看歷史決策軌道：", 
    options=sorted_tickers, 
    index=default_index
)

if selected_stock:
    try:
        stock_detail = yf.Ticker(selected_stock)
        df_detail = stock_detail.history(start=start_date)
        
        if not df_detail.empty and len(df_detail) > 200:
            df_detail['MA20_plot'] = df_detail['Close'].rolling(window=20).mean()
            df_detail['MA200'] = df_detail['Close'].rolling(window=200).mean()
            df_detail['STD20'] = df_detail['Close'].rolling(window=20).std()
            df_detail['BB_Lower'] = df_detail['MA20_plot'] - (2 * df_detail['STD20'])
            df_detail['RSI'] = calculate_rsi(df_detail['Close'], 14)
            
            high_low_det = df_detail['High'] - df_detail['Low']
            tr_det = pd.concat([high_low_det, (df_detail['High'] - df_detail['Close'].shift(1)).abs(), (df_detail['Low'] - df_detail['Close'].shift(1)).abs()], axis=1).max(axis=1)
            df_detail['ATR_det'] = tr_det.rolling(window=atr_period).mean()
            df_detail['Low_Absorb'] = df_detail['MA20_plot'] - (df_detail['ATR_det'] * atr_multiplier)
            
            df_detail = df_detail.join(spy_df_global['Close'].rename('SPY_Close'), how='left')
            df_detail = df_detail.join(spy_df_global['MA200'].rename('SPY_MA200'), how='left')
            df_detail['SPY_Safe'] = df_detail['SPY_Close'] >= df_detail['SPY_MA200']
            df_detail['SPY_Safe'] = df_detail['SPY_Safe'].fillna(True)
            
            price_cond = (df_detail['Low'] <= df_detail['Low_Absorb']) | (df_detail['Low'] <= df_detail['BB_Lower'])
            rsi_cond = df_detail['RSI'] <= rsi_filter_val
            raw_panic_det = rsi_cond & price_cond & (df_detail['SPY_Safe'] | (df_detail['MA20_plot'] >= df_detail['MA200']))
            if use_market_filter:
                raw_panic_det = raw_panic_det & df_detail['SPY_Safe']
                
            sparse_buy_det = pd.Series(False, index=df_detail.index)
            last_date_det = None
            last_price_det = None
            
            for date, is_triggered in raw_panic_det.items():
                if is_triggered:
                    if not pd.isna(df_detail.loc[date, 'MA200']):
                        current_ma200_bias_det = ((df_detail.loc[date, 'MA200'] - df_detail.loc[date, 'Low']) / df_detail.loc[date, 'MA200']) * 100
                    else:
                        current_ma200_bias_det = 0
                    is_extreme_crash_det = current_ma200_bias_det >= extreme_ma200_bias
                    
                    current_touch_price_det = min(df_detail.loc[date, 'Low_Absorb'], df_detail.loc[date, 'BB_Lower'], df_detail.loc[date, 'Low'])
                    
                    if last_date_det is None:
                        sparse_buy_det[date] = True
                        last_date_det = date
                        last_price_det = current_touch_price_det
                    else:
                        days_passed = (date - last_date_det).days
                        if days_passed > wave_window_days:
                            sparse_buy_det[date] = True
                            last_date_det = date
                            last_price_det = current_touch_price_det
                        elif is_extreme_crash_det:
                            sparse_buy_det[date] = True
                            last_date_det = date
                            last_price_det = current_touch_price_det
                        else:
                            price_drop_target = last_price_det * (1 - (min_drop_pct / 100))
                            if current_touch_price_det <= price_drop_target:
                                sparse_buy_det[date] = True
                                last_date_det = date
                                last_price_det = current_touch_price_det

            df_detail['Sparse_Strong_Buy'] = sparse_buy_det
            buy_signals = df_detail[df_detail['Sparse_Strong_Buy']]

            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df_detail.index, open=df_detail['Open'], high=df_detail['High'], low=df_detail['Low'], close=df_detail['Close'], name='K線'))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA20_plot'], name='20MA 趨勢決策線', line=dict(color='orange', width=2)))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA200'], name='200MA 長期生命線', line=dict(color='crimson', width=2.5)))
            
            if not buy_signals.empty:
                fig.add_trace(go.Scatter(
                    x=buy_signals.index,
                    y=buy_signals['Low'] * 0.96,  
                    mode='text',
                    text=['🔥' for _ in range(len(buy_signals))],
                    textposition="bottom center",
                    textfont=dict(size=18),
                    name='🔥 強力買入點'
                ))
                
            fig.update_layout(
                xaxis_rangeslider_visible=False, 
                yaxis_title="價格", 
                height=500, 
                template="plotly_white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
                
    except Exception as e: 
        st.error(f"分析載入失敗: {e}")

# ==============================================================================
# ⏳ 策略回測績效驗證（已整合全量標的、多重潛在強買訊號計數器）
# ==============================================================================
st.markdown("---")
st.header("⏳ 策略回測績效驗證 (實時動態 Demo)")
st.markdown("從您指定的日期開始往後掃描，找出每一檔股票**「第一次」觸發訊號時的模擬建倉價**，並統計整個歷史區間內**累計跳出強買訊號的次數**！")

backtest_col1, backtest_col2, _ = st.columns([1, 1, 2])
with backtest_col1:
    default_backtest_date = datetime(2026, 1, 1).date()
    backtest_date = st.date_input("📅 選擇掃描起始日期：", value=default_backtest_date)

with backtest_col2:
    signal_choice = st.selectbox(
        "🎯 選擇回測訊號類型：",
        options=["單獨強力買入", "單獨買入", "買入 + 強力買入"],
        index=0
    )

bt_date_str = backtest_date.strftime('%Y-%m-%d')
backtest_results = []

with st.spinner("正在進行時光回溯與策略模擬建倉..."):
    df_spy_raw = yf.Ticker("SPY").history(start=bt_date_str)
    spy_start_price = df_spy_raw['Close'].iloc[0] if not df_spy_raw.empty else 1.0
    spy_latest_price = df_spy_raw['Close'].iloc[-1] if not df_spy_raw.empty else 1.0
    spy_performance_pct = ((spy_latest_price - spy_start_price) / spy_start_price) * 100

    for ticker in active_tickers:
        try:
            ticker_sector = st.session_state.sector_map.get(ticker, "未分類")

            df_bt = yf.Ticker(ticker).history(start=(backtest_date - timedelta(days=300)).strftime('%Y-%m-%d'))
            if df_bt.empty: continue
            
            df_bt['MA20'] = df_bt['Close'].rolling(window=20).mean()
            df_bt['MA200'] = df_bt['Close'].rolling(window=200).mean()
            df_bt['STD20'] = df_bt['Close'].rolling(window=20).std()
            df_bt['BB_Lower'] = df_bt['MA20'] - (2 * df_bt['STD20'])
            df_bt['RSI'] = calculate_rsi(df_bt['Close'], 14)
            
            hl = df_bt['High'] - df_bt['Low']
            h_pc = (df_bt['High'] - df_bt['Close'].shift(1)).abs()
            l_pc = (df_bt['Low'] - df_bt['Close'].shift(1)).abs()
            tr = pd.concat([hl, h_pc, l_pc], axis=1).max(axis=1)
            df_bt['ATR'] = tr.rolling(window=atr_period).mean()

            df_scan = df_bt.loc[bt_date_str:]
            if df_scan.empty: continue
            
            latest_today_price = df_bt['Close'].iloc[-1]
            currency = "NT$ " if ".TW" in ticker else "$ "

            df_scan = df_scan.copy()
            df_scan['SPY_Close'] = df_spy_raw['Close']
            
            # 🛠️ 核心優化：建立該個股回測區間內完整的「強買訊號」歷史矩陣，用於高精準度次數統計
            last_bt_date = None
            last_bt_price = None
            
            total_strong_buy_count = 0  # 🎯 新增：強買信號次數計數器
            first_trade_data = None     # 🎯 用於捕捉第一次觸發交易的錨點
            
            for date, row in df_scan.iterrows():
                past_close = row['Close']
                past_low = row['Low']
                past_ma20 = row['MA20']
                past_ma200 = row['MA200'] if not pd.isna(row['MA200']) else past_ma20
                past_atr = row['ATR']
                past_rsi = row['RSI'] if not pd.isna(row['RSI']) else 50
                past_bb_lower = row['BB_Lower']
                
                if pd.isna(past_ma20) or pd.isna(past_atr): continue
                
                low_b = past_ma20 - (past_atr * atr_multiplier)
                
                spy_past_series = spy_df_global.loc[:date.strftime('%Y-%m-%d')]
                if not spy_past_series.empty:
                    spy_past_close = spy_past_series['Close'].iloc[-1]
                    spy_past_ma200 = spy_past_series['MA200'].iloc[-1]
                    is_market_safe_past = spy_past_close >= spy_past_ma200 if not pd.isna(spy_past_ma200) else True
                else:
                    is_market_safe_past = True
                
                is_raw_strong_buy = (past_low <= low_b or past_low <= past_bb_lower) and past_rsi <= rsi_filter_val and (is_market_safe_past or (past_ma20 >= past_ma200))
                if use_market_filter and not is_market_safe_past:
                    is_raw_strong_buy = False
                    
                bt_touch_price = min(low_b, past_bb_lower, past_low)
                
                is_past_strong_buy = False
                if is_raw_strong_buy:
                    past_ma200_bias = ((past_ma200 - past_low) / past_ma200) * 100 if not pd.isna(past_ma200) else 0
                    is_ma200_extreme_crash_bt = past_ma200_bias >= extreme_ma200_bias
                    
                    if last_bt_date is None:
                        is_past_strong_buy = True
                        total_strong_buy_count += 1
                        last_bt_date = date
                        last_bt_price = bt_touch_price
                    else:
                        days_passed = (date - last_bt_date).days
                        if is_ma200_extreme_crash_bt:
                            is_past_strong_buy = True
                            total_strong_buy_count += 1
                            last_bt_date = date
                            last_bt_price = bt_touch_price
                        elif days_passed > wave_window_days:
                            is_past_strong_buy = True
                            total_strong_buy_count += 1
                            last_bt_date = date
                            last_bt_price = bt_touch_price
                        else:
                            price_drop_target = last_bt_price * (1 - (min_drop_pct / 100))
                            if bt_touch_price <= price_drop_target:
                                is_past_strong_buy = True
                                total_strong_buy_count += 1
                                last_bt_date = date
                                last_bt_price = bt_touch_price
                
                is_past_normal_buy = abs(past_low - past_ma20) / past_ma20 <= 0.02
                
                # 判斷當天滿足何種信號類型
                current_signal = None
                if is_past_strong_buy: 
                    current_signal = "🔥 強力買入"
                elif is_past_normal_buy and not is_past_strong_buy: 
                    current_signal = "🟢 買入"
                
                # 匹配使用者選擇的過濾類型，固定鎖定「第一次觸發」做為建倉績效基準
                if first_trade_data is None and current_signal is not None:
                    is_match = False
                    if signal_choice == "買入 + 強力買入": is_match = True
                    elif signal_choice == "單獨買入" and current_signal == "🟢 買入": is_match = True
                    elif signal_choice == "單獨強力買入" and current_signal == "🔥 強力買入": is_match = True
                    
                    if is_match:
                        final_entry_price = bt_touch_price if current_signal == "🔥 強力買入" else past_ma20
                        return_pct = ((latest_today_price - final_entry_price) / final_entry_price) * 100
                        first_trade_data = {
                            "產業": ticker_sector, "代碼": ticker,
                            "首次建倉日": date.strftime('%Y-%m-%d'), "當時訊號": current_signal,
                            "模擬買入價": f"{currency}{final_entry_price:.1f}", "今日最新價": f"{currency}{latest_today_price:.1f}",
                            "累積報酬率": f"{return_pct:.1f}%"
                        }
            
            # 歷史掃描結束後，如果該個股有觸發建倉，將累計強買訊號次數合併輸出到表格中
            if first_trade_data is not None:
                first_trade_data["強買訊號次數"] = f"{total_strong_buy_count} 次"
                backtest_results.append(first_trade_data)

        except Exception as e: pass

if backtest_results:
    df_bt_results = pd.DataFrame(backtest_results)
    df_bt_results['sort_val'] = df_bt_results['累積報酬率'].str.replace('%', '').astype(float)
    df_bt_results = df_bt_results.sort_values(by='sort_val', ascending=False).drop('sort_val', axis=1)
    
    # 調整欄位順序，讓強買次數非常直觀地出現在看板上
    cols_order = ["產業", "代碼", "首次建倉日", "當時訊號", "強買訊號次數", "模擬買入價", "今日最新價", "累積報酬率"]
    df_bt_results = df_bt_results[[c for c in cols_order if c in df_bt_results.columns]]
    
    st.dataframe(df_bt_results, use_container_width=True, hide_index=True)
    
    avg_return = df_bt_results['累積報酬率'].str.replace('%', '').astype(float).mean()
    win_rate = (df_bt_results['累積報酬率'].str.replace('%', '').astype(float) > 0).mean() * 100
    
    col_r1, col_r2, col_r3 = st.columns(3)
    if avg_return > 0:
        col_r1.success(f"📈 策略平均報酬率：**{avg_return:.1f}%**")
    else:
        col_r1.error(f"📉 策略平均報酬率：**{avg_return:.1f}%**")
    col_r2.info(f"🎯 策略勝率 (正報酬比例)：**{win_rate:.1f}%**")
    col_r3.metric(label="📊 同期對比 S&P 500 (SPY) 報酬率", value=f"{spy_performance_pct:.1f}%")
else:
    st.info(f"自 {bt_date_str} 起算，觀察名單內無任何標的觸發您選擇的條件。")
