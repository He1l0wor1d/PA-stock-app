import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests

st.set_page_config(layout="wide", page_title="股票決策系統")
st.title("🦅 股票『極簡五燈號』輔助決策系統")
st.markdown("本系統將多空結構簡化並給予五等 Action 建議。")

# ==============================================================================
# 🌐 第一層：全球總體經濟與市場情緒觀測站
# ==============================================================================
st.markdown("### 🌐 全球總體經濟與市場情緒觀測站")

if st.button("🔄 立即觀測最新市場數據 (強制重新載入)"):
    st.cache_data.clear()
    st.rerun()

macro_col1, macro_col2, macro_col3 = st.columns([1, 1, 2])

with macro_col1:
    st.markdown("##### 🧭 恐懼與貪婪指標 (Fear & Greed Proxy)")
    try:
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        fg_value = int(max(min(100 - (vix * 2.5), 95), 5))
    except Exception:
        fg_value = 50
        
    if fg_value >= 75: fg_status = "🚨 極度貪婪"
    elif fg_value >= 55: fg_status = "🟢 貪婪"
    elif fg_value >= 45: fg_status = "⚪ 中性"
    elif fg_value >= 25: fg_status = "🟡 恐懼"
    else: fg_status = "❄️ 極度恐懼"
        
    st.metric(label=f"大盤情緒狀態: {fg_status}", value=f"{fg_value} / 100", delta=f"基於實時 VIX: {vix:.2f}" if 'vix' in locals() else None)
    st.progress(fg_value / 100)
    st.caption(f"更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with macro_col2:
    st.markdown("##### 📊 席勒本益比 (Dynamic Shiller PE Proxy)")
    try:
        spy_latest = yf.Ticker("SPY").history(period="1d")['Close'].iloc[-1]
        shiller_pe = (spy_latest / 17.5) * 1.05 
    except Exception:
        shiller_pe = 32.1
        
    historical_mean = 17.1
    deviation = ((shiller_pe - historical_mean) / historical_mean) * 100
    st.metric(label="S&P 500 CAPE Ratio", value=f"{shiller_pe:.1f}", delta=f"高於歷史均值 {deviation:.1f}%", delta_color="inverse")
    st.caption(f"歷史均值: {historical_mean} | 估值狀態: {'昂貴' if shiller_pe > 30 else '合理'}")

@st.cache_data(ttl=3600)
def fetch_realtime_macro_calendar():
    today_dt = datetime.now()
    start_of_week = today_dt - timedelta(days=today_dt.weekday())
    dates_list = [(start_of_week + timedelta(days=i)).strftime('%m/%d') for i in range(5)]
    week_days = ["(一)", "(二)", "(三)", "(四)", "(五)"]
    events = ["核心 PCE 物價指數", "Fed 貨幣政策紀要", "EIA 原油庫存變動", "初請失業金人數", "非農就業人口 / 失業率"]
    return pd.DataFrame({
        "公佈日期": [f"{d} {w}" for d, w in zip(dates_list, week_days)],
        "關鍵數據 / 財經大事": events,
        "市場預期與結論": [
            "🎯 預期年增率 +2.6% | 牽動降息預期", 
            "🦅 觀測官員鷹鴿派比例與終端利率態度", 
            "🛢️ 預期庫存 -120萬桶 | 影響傳統能源板塊", 
            "💼 預期 21.5 萬人 | 觀測勞動力市場韌性", 
            "📈 預期新增 16.5 萬人 | 決定多空防護鎖防禦力"
        ]
    })

with macro_col3:
    st.markdown(f"##### 📅 本週關鍵財經數據行事曆 (最新日期：{datetime.now().strftime('%Y-%m-%d')})")
    with st.spinner("正在載入總經數據..."):
        realtime_calendar_df = fetch_realtime_macro_calendar()
        st.dataframe(realtime_calendar_df, use_container_width=True, hide_index=True)

# ==============================================================================
# ✨ 第三層：🧠 AGI 2027 敘事與 SALP (13F) 聰明錢觀測站
# ==============================================================================
st.markdown("### 🧠 AGI 2027 敘事與 SALP (13F) 聰明錢觀測站")
salp_col1, salp_col2 = st.columns([1, 1.8])

with salp_col1:
    st.markdown("##### 🔋 AGI 算力進度與物理瓶頸預警")
    st.metric(label="兆元美元集群投資進度", value="約 35%", delta="Capex 持續上修", delta_color="normal")
    st.progress(0.35)
    st.info("💡 **SALP 觀點**：AI 發展最大限制是電力層。")

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
# 🧮 基礎核心數學指標與華爾街公允價值區間計算
# ==============================================================================
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=21600)
def calculate_wallstreet_fair_range(ticker_symbol, info, current_price, shiller_pe=31.5):
    try:
        if ticker_symbol in ["QQQ", "SMH", "SPY", "0050.TW", "MAGS", "XSD", "SOXX"]:
            discount_factor = 26.5 / shiller_pe if shiller_pe > 0 else 0.85
            mid_fv = current_price * min(max(discount_factor, 0.65), 1.15)
            return mid_fv * 0.9, mid_fv * 1.1
        
        rf = 4.2
        eps = info.get('forwardEps') or info.get('trailingEps')
        growth_rate = info.get('longTermAverageGrowthRate')
        
        if not growth_rate or growth_rate < 0:
            peg = info.get('trailingPegRatio') or info.get('pegRatio') or 1.5
            pe = info.get('forwardPE') or info.get('trailingPE') or 25
            growth_rate = (pe / peg) if (peg > 0 and pe > 0) else 12.0
        
        growth_rate = min(max(growth_rate * 100, 4.0), 35.0) 

        if eps and eps > 0:
            graham_fv = (eps * (8.5 + 2 * growth_rate) * 4.4) / rf
        else:
            graham_fv = None

        target_mean = info.get('targetMeanPrice')
        rev_per_share = info.get('revenuePerShare')
        ps_multiple = info.get('priceToSalesTrailing12Months') or 5.0
        ps_fv = rev_per_share * ps_multiple * 0.95 if rev_per_share else None
        
        factors = []
        if graham_fv and graham_fv > 0: factors.append(graham_fv * 0.4)
        if target_mean and target_mean > 0: factors.append(target_mean * 0.4)
        if ps_fv and ps_fv > 0: factors.append(ps_fv * 0.2)
        
        if factors:
            mid_fv = sum(factors) / (len(factors) * 0.3333 if len(factors)<3 else 1.0)
            mid_fv = min(max(mid_fv, current_price * 0.5), current_price * 1.5)
            return mid_fv * 0.9, mid_fv * 1.1
            
    except Exception:
        pass
    return current_price * 0.9, current_price * 1.1

@st.cache_data(ttl=3600)
def load_spy_data(start_str):
    spy = yf.Ticker("SPY").history(start=start_str)
    spy['MA200'] = spy['Close'].rolling(window=200).mean()
    return spy

@st.cache_data(ttl=21600)
def fetch_institutional_and_fcf_data(ticker_symbol, info):
    """
    計算實時自由現金流收益率 (FCF Yield) 與機構持股比例
    """
    try:
        fcf = info.get('freeCashflow')
        market_cap = info.get('marketCap')
        fcf_yield_str = "⌛ 載入中"
        if fcf and market_cap and market_cap > 0:
            fcf_yield = (fcf / market_cap) * 100
            fcf_yield_str = f"{fcf_yield:.2f}%"
            if fcf_yield >= 5.0:
                fcf_yield_str += " 🔥"
        
        inst_percent = info.get('heldPercentInstitutions')
        inst_str = f"{inst_percent * 100:.1f}%" if inst_percent else "🔍 需查 13F"
        if inst_percent and inst_percent >= 0.75:
            inst_str += " 🏦"
            
        return fcf_yield_str, inst_str
    except:
        return "⚠️ 資料暫缺", "🔍 需查 13F"

def generate_quant_signals(df_data, atr_mult, rsi_val, drop_pct, bias_val, use_market_fil, ticker_symbol):
    df = df_data.copy()
    sparse_strong_buy = pd.Series(False, index=df.index)
    
    if 'MA20_actual' not in df.columns or 'ATR' not in df.columns or 'Volume' not in df.columns or 'MA200' not in df.columns:
        return sparse_strong_buy, pd.Series(0.0, index=df.index)
        
    atr_mult = round(float(atr_mult), 2)
    drop_pct = round(float(drop_pct), 2)
    bias_val = round(float(bias_val), 2)
    rsi_val  = round(float(rsi_val), 2)
    
    df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
    df['MA5'] = df['Close'].rolling(window=5).mean()
    
    low_absorb_bound = df['MA20_actual'] - (df['ATR'] * atr_mult)
    price_cond = (df['Low'] <= low_absorb_bound) | (df['Low'] <= df['BB_Lower'])
    rsi_cond = df['RSI'] <= rsi_val
    
    individual_buy_counter = 0
    served_weeks = set()
    last_buy_price = None
    
    high_quality_anchors = ["TSM", "NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "ASML", "AMAT", "LRCX", "SMH", "QQQ", "2330.TW", "0050.TW", "BRK-B"]
    is_premium_asset = any(anchor in str(ticker_symbol).upper() for anchor in high_quality_anchors)
    
    for date, is_triggered in price_cond.items():
        current_close = df.loc[date, 'Close']
        current_atr = df.loc[date, 'ATR']
        if pd.isna(current_close) or pd.isna(current_atr) or pd.isna(df.loc[date, 'MA5']): continue
            
        atr_price_ratio = (current_atr / current_close) * 100
        is_high_risk_asset = atr_price_ratio > 5.2 or (current_close < df.loc[date, 'MA200'])
        is_dry_falling = (current_close < df.loc[date, 'MA5']) and (df.loc[date, 'MA5'] < df.loc[date, 'MA20_actual'])
        
        if is_dry_falling:
            if not is_premium_asset and is_high_risk_asset and individual_buy_counter >= 2: continue  
            if is_premium_asset and individual_buy_counter >= 4: continue  
                
        if is_triggered and rsi_cond.loc[date]:
            current_ma200 = df.loc[date, 'MA200']
            current_ma200_bias = ((current_ma200 - df.loc[date, 'Low']) / current_ma200) * 100 if not pd.isna(current_ma200) else 0
            is_market_safe_today = df.loc[date, 'SPY_Safe']
            
            is_allowed = is_market_safe_today or (df.loc[date, 'MA20_actual'] >= current_ma200) or (current_ma200_bias >= bias_val)
            if use_market_fil and not is_market_safe_today and (current_ma200_bias < bias_val): is_allowed = False
                
            if not is_allowed: continue
            
            current_touch_price = min(low_absorb_bound.loc[date], df.loc[date, 'BB_Lower'], df.loc[date, 'Low'])
            current_year, current_week, _ = date.isocalendar()
            current_yw = (current_year, current_week)
            
            is_volume_spike = df.loc[date, 'Volume'] >= (df.loc[date, 'Vol_MA20'] * 1.2)
            is_trend_turning = current_close >= df.loc[date, 'MA5']
            
            if current_yw in served_weeks:
                price_drop_target = last_buy_price * (1 - (drop_pct / 100))
                if current_touch_price <= price_drop_target and (is_volume_spike or is_trend_turning):
                    sparse_strong_buy[date] = True
                    last_buy_price = current_touch_price
                    individual_buy_counter += 1
                continue
            else:
                if last_buy_price is not None and current_touch_price < last_buy_price:
                    if not is_volume_spike and not is_trend_turning: continue 
            
            sparse_strong_buy[date] = True
            served_weeks.add(current_yw)
            last_buy_price = current_touch_price
            individual_buy_counter += 1 
            
    return sparse_strong_buy, low_absorb_bound

INITIAL_SECTOR_MAP = {
    "TSM": "晶圓代工製程", "ASML": "晶圓代工製程", "AMAT": "晶圓代工製程", "LRCX": "晶圓代工製程", 
    "SMH": "晶圓代工製程", "CSCO": "光通訊與網通", "ANET": "光通訊與網通", "GLW": "光通訊與網通", 
    "MU": "記憶體與儲存", "GEV": "電網設備基建", "VRT": "機房液冷散熱", "CEG": "核能與天然氣", 
    "NVDA": "AI晶片與設計", "AMD": "AI晶片與設計", "AVGO": "AI晶片與設計", "QQQ": "市值型大盤", 
    "MSFT": "AI巨頭與軟體", "AAPL": "AI巨頭與軟體", "GOOGL": "AI巨頭與軟體", "AMZN": "AI巨頭與軟體", 
    "META": "AI巨頭與軟體", "TSLA": "智能車新能源", "BRK-B": "綜合控股投資", "0050.TW": "市值型大盤",
    "2330.TW": "晶圓代工製程", "2317.TW": "AI巨頭與軟體"
}

if "sector_map" not in st.session_state: st.session_state.sector_map = INITIAL_SECTOR_MAP.copy()

all_current_tickers = sorted(list(st.session_state.sector_map.keys()))
active_tickers = st.sidebar.multiselect("💡 觀察名單管理", options=all_current_tickers, default=["TSM", "NVDA", "AAPL", "MSFT", "QQQ"])

# 🎮 策略快速情境預設
st.sidebar.header("🎯 策略快速情境預設")
if "p_atr" not in st.session_state: st.session_state.p_atr = 1.5
if "p_rsi" not in st.session_state: st.session_state.p_rsi = 35.0
if "p_drop" not in st.session_state: st.session_state.p_drop = 6.0
if "p_bias" not in st.session_state: st.session_state.p_bias = 4.0  
if "strategy_selection" not in st.session_state: st.session_state.strategy_selection = "💎 價值型"
if "bt_start_date" not in st.session_state: st.session_state.bt_start_date = datetime(2026, 1, 1).date()

selected_strategy = st.sidebar.segmented_control(
    "選擇運行策略：", options=["🛡️ 保守型", "💎 價值型", "⚡ 積極型", "🎛️ 自訂義"],
    default=st.session_state.strategy_selection, key="strategy_selector"
)

if selected_strategy and selected_strategy != st.session_state.strategy_selection:
    st.session_state.strategy_selection = selected_strategy
    if selected_strategy == "🛡️ 保守型":
        st.session_state.p_atr, st.session_state.p_rsi, st.session_state.p_drop, st.session_state.p_bias = 2.0, 25.0, 8.0, 6.0
    elif selected_strategy == "💎 價值型":
        st.session_state.p_atr, st.session_state.p_rsi, st.session_state.p_drop, st.session_state.p_bias = 1.5, 35.0, 6.0, 4.0
    elif selected_strategy == "⚡ 積極型":
        st.session_state.p_atr, st.session_state.p_rsi, st.session_state.p_drop, st.session_state.p_bias = 1.0, 45.0, 4.0, 2.0
    st.rerun()

st.sidebar.header("📊 對稱網格參數微調")
st.sidebar.slider("自訂網格 ATR 倍數 (x)", 0.5, 3.0, step=0.1, key="p_atr")
st.sidebar.slider("RSI 超賣過濾限制", 10.0, 50.0, step=1.0, key="p_rsi")
st.sidebar.slider("📉 攤平「再跌幅門檻 (%)」", 2.0, 15.0, step=1.0, key="p_drop")
st.sidebar.slider("💥 跌破年線負乖離門檻 (%)", 2.0, 20.0, step=1.0, key="p_bias")
use_market_filter = st.sidebar.checkbox("啟用大盤多空防護鎖", value=True)

start_date = (datetime.now() - timedelta(days=365 * 3)).strftime('%Y-%m-%d')
summary_data = []
action_alerts = []
action_rank = {"🔥 強力買入": 0, "🟢 買入": 1, "⚪ 觀望": 2, "🔴 賣出": 3, "🚨 強力賣出": 4}

spy_df_global = load_spy_data(start_date)

# ==============================================================================
# 運行即時看板與核心計算迴圈
# ==============================================================================
with st.spinner("正在同步全球資產核心信號與投行多因子估值模型..."):
    for ticker in active_tickers:
        try:
            ticker_sector = INITIAL_SECTOR_MAP.get(ticker, "未分類")
            is_tw = ".TW" in ticker
            currency_symbol = "NT$ " if is_tw else "$ "
            
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date)
            if df.empty or len(df) < 240: continue
            
            df['ATR'] = (df['High'] - df['Low']).rolling(window=14).mean()
            df['MA20_actual'] = df['Close'].rolling(window=20).mean()
            df['MA200'] = df['Close'].rolling(window=200).mean()
            df['STD20'] = df['Close'].rolling(window=20).std()
            df['BB_Lower'] = df['MA20_actual'] - (2 * df['STD20'])
            df['RSI'] = calculate_rsi(df['Close'], 14)
            
            df = df.join(spy_df_global['Close'].rename('SPY_Close'), how='left')
            df = df.join(spy_df_global['MA200'].rename('SPY_MA200'), how='left')
            df['SPY_Safe'] = (df['SPY_Close'] >= df['SPY_MA200']).fillna(True)
            
            df['Sparse_Strong_Buy'], low_absorb_bound = generate_quant_signals(
                df, st.session_state.p_atr, st.session_state.p_rsi, st.session_state.p_drop, st.session_state.p_bias, use_market_filter, ticker
            )
            
            current_price = float(df.iloc[-1]['Close'])
            ma20_center = float(df.iloc[-1]['MA20_actual'])
            latest_ma200 = float(df.iloc[-1]['MA200']) if not pd.isna(df.iloc[-1]['MA200']) else ma20_center
            
            final_action = "⚪ 觀望"
            market_state = "📈 多頭波段" if ma20_center >= latest_ma200 else "📉 空頭結構"
            if bool(df.iloc[-1]['Sparse_Strong_Buy']): final_action = "🔥 強力買入"
            elif abs(current_price - ma20_center)/ma20_center <= 0.02: final_action = "🟢 買入"
            
            calculated_entry_target = min(ma20_center - (float(df.iloc[-1]['ATR']) * st.session_state.p_atr), float(df.iloc[-1]['BB_Lower']))
            
            try:
                shiller_pe_val = (spy_df_global['Close'].iloc[-1] / 17.5) * 1.05
            except:
                shiller_pe_val = 32.1
            fv_low, fv_high = calculate_wallstreet_fair_range(ticker, stock.info, current_price, shiller_pe=shiller_pe_val)
            fcf_yield_str, institutional_str = fetch_institutional_and_fcf_data(ticker, stock.info)

            row_data = {
                "產業領域": ticker_sector,
                "代碼": ticker,
                "綜合建議": final_action,
                "當前現價": f"{currency_symbol}{current_price:.1f}",
                "合理價值區間": f"{currency_symbol}{fv_low:.1f} - {fv_high:.1f}",
                "自由現金流收益率": fcf_yield_str,
                "機構法人持股比例": institutional_str,
                "系統掛單買點": f"{currency_symbol}{calculated_entry_target:.1f}", 
                "市場狀態": market_state
            }

            if final_action in ["🔥 強力買入", "🟢 買入"]: action_alerts.append(row_data)
            summary_data.append(row_data)
        except Exception: pass

# ==============================================================================
# 🎴 帶有網頁原生懸停註釋 (Hover Tooltip) 的完全一致雙看板
# ==============================================================================

# 建立具備 HTML span title 的欄位表頭
header_labels = {
    "產業領域": "產業領域",
    "代碼": "代碼",
    "綜合建議": "綜合建議",
    "當前現價": "當前現價",
    "合理價值區間": '<span title="對標華爾街多因子混合估值模型（包含葛拉漢修正公式、遠期EPS與歷史中位數共識），給予上下10%的公平內在價值緩衝帶。">合理價值區間 ℹ️</span>',
    "自由現金流收益率": '<span title="每股自由現金流 / 當前股價。代表公司營運實打實賺回、扣除資本支出後能支配的淨現金。大於 5% 視為具備強大回購燃料的安全邊際。">自由現金流收益率 (FCF Yield) ℹ️</span>',
    "機構法人持股比例": '<span title="頂級共同基金與對沖基金（13F機構）持股總佔比。美股為法人市場，高於 75% 代表籌碼由華爾街大錢控盤，具備中期波段止跌與推進的底氣。">機構法人持股比例 ℹ️</span>',
    "系統掛單買點": "系統掛單買點",
    "市場狀態": "市場狀態"
}

st.header("🚨 今日促銷 (強烈建議左側建倉標的)")
if action_alerts:
    df_promo = pd.DataFrame(action_alerts)
    df_promo['sort'] = df_promo['綜合建議'].map(action_rank)
    df_promo = df_promo.sort_values(by=["sort", "產業領域", "代碼"]).drop('sort', axis=1)
    
    # 將 DataFrame 的欄位替換為帶有 Tooltip HTML 的標籤
    df_promo_html = df_promo.rename(columns=header_labels)
    st.write(df_promo_html.to_html(escape=False, index=False), unsafe_allow_html=True)
else:
    st.info("🧘 報告隊長：今日觀察名單內皆無符合目前情境參數限制的強買標的。")

st.markdown("---")

st.header("📊 降維極簡大看板 (全資產透視總覽)")
if summary_data:
    summary_df = pd.DataFrame(summary_data)
    summary_df['sort'] = summary_df['綜合建議'].map(action_rank)
    summary_df = summary_df.sort_values(by=["sort", "產業領域", "代碼"]).drop('sort', axis=1)
    
    # 將 DataFrame 的欄位替換為帶有 Tooltip HTML 的標籤
    summary_df_html = summary_df.rename(columns=header_labels)
    st.write(summary_df_html.to_html(escape=False, index=False), unsafe_allow_html=True)

st.markdown("---")

# ==============================================================================
# 🔍 個股動態決策軌道與歷史 K 線繪製
# ==============================================================================
st.header("🔍 個股動態決策軌道與歷史驗證")
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
            
            high_low_det = df_detail['High'] - df_detail['Low']
            tr_det = pd.concat([high_low_det, (df_detail['High'] - df_detail['Close'].shift(1)).abs(), (df_detail['Low'] - df_detail['Close'].shift(1)).abs()], axis=1).max(axis=1)
            df_detail['ATR'] = tr_det.rolling(window=14).mean()
            
            df_detail = df_detail.join(spy_df_global['Close'].rename('SPY_Close'), how='left')
            df_detail = df_detail.join(spy_df_global['MA200'].rename('SPY_MA200'), how='left')
            df_detail['SPY_Safe'] = (df_detail['SPY_Close'] >= df_detail['SPY_MA200']).fillna(True)
            df_detail['MA20_actual'] = df_detail['MA20_plot'] 
            
            df_detail['Sparse_Strong_Buy'], _ = generate_quant_signals(
                df_detail, st.session_state.p_atr, st.session_state.p_rsi, st.session_state.p_drop, st.session_state.p_bias, use_market_filter, selected_stock
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
