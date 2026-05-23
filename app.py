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

# ==============================================================================
# 4. 內建核心產業與供應鏈地圖
# ==============================================================================
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
    "BA": "航太太空國防", "RDW": "航太太空國防", "RKLB": "航太太空國防", "ASTS": "航太太空國防", "ONDS": "航太太空國防",
    "XOM": "傳統能源礦產", "OXY": "傳統能源礦產", "EQT": "傳統能源礦產",
    "LLY": "生技醫療科技", "TEM": "生技醫療科技", "GRAL": "生技醫療科技", "ILMN": "生技醫療科技",
    "JPM": "金融資產管理", "GS": "金融資產管理", "BLK": "金融資產管理", "BX": "金融資產管理", 
    "SOFI": "金融資產管理", "HOOD": "金融資產管理", "SEI": "金融資產管理",
    "TSLA": "智能車新能源", "BYDDF": "智能車新能源", "MSTR": "數位資產科技", 
    "BRK-B": "綜合控股投資", "GLD": "綜合控股投資", "SHLD": "綜合控股投資", "NBIS": "綜合控股投資",
    "2330.TW": "晶圓代工製程", "0050.TW": "市值型大盤", "2851.TW": "金融再保險", "5607.TW": "航空航運物流",
}

if "sector_map" not in st.session_state: st.session_state.sector_map = INITIAL_SECTOR_MAP.copy()

st.sidebar.header("⚙️ 實時清單與自訂網格")
with st.sidebar.expander("➕ 新增觀察股票", expanded=False):
    add_ticker = st.text_input("輸入代碼 (美股如: NVDA / 台股如: 2317.TW)").strip().upper()
    add_sector = st.selectbox("產業分類", sorted(list(set(st.session_state.sector_map.values()))))
    if st.button("確認新增") and add_ticker:
        st.session_state.sector_map[add_ticker] = add_sector
        st.rerun()

all_current_tickers = sorted(list(st.session_state.sector_map.keys()))
active_tickers = st.sidebar.multiselect("💡 觀察名單管理", options=all_current_tickers, default=all_current_tickers)

# ==============================================================================
# 🎒 (核心功能) 側邊欄：持股清單與大盤基準快取
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.header("🎒 我的核心持有庫存")
default_my_stocks = ["TSM", "NVDA", "2330.TW", "AAPL"]
default_my_stocks = [s for s in default_my_stocks if s in active_tickers]
my_holdings = st.sidebar.multiselect("勾選您目前已建立部位的個股：", options=active_tickers, default=default_my_stocks)

distinct_sectors = ["全部顯示"] + sorted(list(set(st.session_state.sector_map.values())))
selected_sector_filter = st.sidebar.selectbox("🎯 聚焦特定產業類別：", distinct_sectors)

st.sidebar.header("📊 對稱網格參數設定")
atr_period = st.sidebar.slider("ATR 計算天數", 5, 22, 14)
atr_multiplier = st.sidebar.slider("自訂網格 ATR 倍數 (x)", 0.5, 2.5, 1.4, 0.1)

start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
summary_data = []
action_alerts = []
action_rank = {"🔥 強力買入": 0, "🟢 買入": 1, "⚪ 觀望": 2, "🔴 賣出": 3, "🚨 強力賣出": 4}

# 事先快取基準大盤數據以計算相對強度 (RS)
@st.cache_data(ttl=3600)
def get_benchmarks(start):
    tw_bench = yf.Ticker("0050.TW").history(start=start)['Close'].pct_change().fillna(0)
    us_bench = yf.Ticker("QQQ").history(start=start)['Close'].pct_change().fillna(0)
    return tw_bench, us_bench

try:
    tw_benchmark_returns, us_benchmark_returns = get_benchmarks(start_date)
except Exception:
    tw_benchmark_returns, us_benchmark_returns = pd.Series(), pd.Series()

with st.spinner("正在提煉極簡 Action 決策與運算強弱動能指標..."):
    for ticker in active_tickers:
        try:
            ticker_sector = st.session_state.sector_map.get(ticker, "未分類")
            if selected_sector_filter != "全部顯示" and ticker_sector != selected_sector_filter: continue

            is_tw = ".TW" in ticker or ".TWO" in ticker
            currency_symbol = "NT$ " if is_tw else "$ "
            
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date)
            if df.empty or len(df) < 150: continue
            
            # ==========================================
            # 🚀 運算全新升級指標：RS 相對強度 與 52W 高點距離
            # ==========================================
            # 1. 52週高點距離百分比
            high_52w = df['High'].max()
            current_price = float(df.iloc[-1]['Close'])
            dist_to_52w = ((high_52w - current_price) / high_52w) * 100
            
            # 2. RS 相對強度 (過去 30 個交易日相較於大盤基準的超額報酬績效)
            stock_returns = df['Close'].pct_change().fillna(0).tail(30)
            bench_returns = tw_benchmark_returns.tail(30) if is_tw else us_benchmark_returns.tail(30)
            
            # 確保對齊長度
            min_len = min(len(stock_returns), len(bench_returns))
            if min_len > 0:
                rs_score = float((stock_returns.tail(min_len) - bench_returns.tail(min_len)).sum() * 100)
                rs_display = f"🔥 強於大盤 (+{rs_score:.1f}%)" if rs_score > 0 else f"❄️ 弱於大盤 ({rs_score:.1f}%)"
            else:
                rs_display = "數據不足"

            # 網格核心指標運算
            high_low = df['High'] - df['Low']
            tr = pd.concat([high_low, (df['High'] - df['Close'].shift(1)).abs(), (df['Low'] - df['Close'].shift(1)).abs()], axis=1).max(axis=1)
            df['ATR'] = tr.rolling(window=atr_period).mean()
            df['MA20_actual'] = df['Close'].rolling(window=20).mean()
            df['MA200'] = df['Close'].rolling(window=200).mean()
            
            yesterday_close = float(df.iloc[-2]['Close'])      
            ma20_center = float(df.iloc[-1]['MA20_actual'])
            latest_atr = float(df.iloc[-1]['ATR'])
            latest_ma200 = float(df.iloc[-1]['MA200']) if not pd.isna(df.iloc[-1]['MA200']) else ma20_center
            
            highest_20d = float(df['High'].rolling(window=20).max().iloc[-1])
            trailing_stop_price = highest_20d - (2 * latest_atr)

            low_absorb_price = ma20_center - (latest_atr * atr_multiplier)
            high_toss_price = ma20_center + (latest_atr * atr_multiplier)
            
            final_action = "⚪ 觀望"
            
            # 多空核心決策分流
            if ma20_center >= latest_ma200:
                if current_price <= low_absorb_price: final_action = "🔥 強力買入"
                elif abs(current_price - ma20_center)/ma20_center <= 0.02: final_action = "🟢 買入"
                elif current_price >= high_toss_price: final_action = "🔴 賣出"
                elif current_price <= trailing_stop_price: final_action = "🚨 強力賣出"
            else:
                if yesterday_close >= ma20_center and current_price < ma20_center: final_action = "🚨 強力賣出"
                elif current_price >= high_toss_price: final_action = "🔴 賣出"
                elif current_price <= low_absorb_price: final_action = "🟢 買入"

            # ==================================================================
            # 🎯 實戰降維分流篩選：只放重點關注、已買持股健檢通知 (限10個以內)
            # ==================================================================
            is_held = ticker in my_holdings
            is_alert_triggered = False
            
            if final_action in ["🔥 強力買入", "🟢 買入"]:
                is_alert_triggered = True  # 有新買點隨時觸發
            elif final_action in ["🔴 賣出", "🚨 強力賣出"] and is_held:
                is_alert_triggered = True  # 有風險訊號，且「確有持股」才顯示

            if is_alert_triggered:
                action_alerts.append({
                    "庫存狀態": "🎒 已持有" if is_held else "🔍 觀察中",
                    "代碼": ticker,
                    "執行決策": final_action,
                    "當前市價": f"{currency_symbol}{current_price:.1f}",
                    "網格臨界提示": f"低吸價:{currency_symbol}{low_absorb_price:.1f} / 高拋價:{currency_symbol}{high_toss_price:.1f}",
                    "移動停利防線": f"{currency_symbol}{trailing_stop_price:.1f}" if is_held else "未持股不計"
                })

            summary_data.append({
                "產業領域": ticker_sector, "代碼": ticker, "當前股價": f"{currency_symbol}{current_price:.1f}",
                "RS 相對大盤強弱": rs_display, "距52W高點": f"{dist_to_52w:.1f}%",
                "綜合建議": final_action, "買點": f"{currency_symbol}{low_absorb_price:.1f}", "賣點": f"{currency_symbol}{high_toss_price:.1f}"
            })
        except Exception: pass

# --- 介面排版輸出 ---
st.header("🚨 今日核心執行 ACTION 面板 (精簡庫存健檢版)")
if action_alerts:
    # 嚴格限制最多呈現 10 檔最急迫需要做動作的核心標的
    df_alert = pd.DataFrame(action_alerts).head(10)
    st.dataframe(df_alert, use_container_width=True, hide_index=True)
else:
    st.info("🧘 報告隊長：今日已持股庫存與觀察清單皆無突破臨界點，請繼續安心保持空倉/持股。")

st.markdown("---")

st.header(f"📊 降維極簡大看板 (已整合全新前瞻強弱指標)")
if summary_data:
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.markdown("---")

st.header("🔍 個股動態決策軌道與核心基本面")
sorted_tickers = sorted(active_tickers)
default_index = sorted_tickers.index("TSM") if "TSM" in sorted_tickers else 0

selected_stock = st.selectbox("選擇個股查看決策軌道：", sorted_tickers, index=default_index)

if selected_stock:
    try:
        stock_detail = yf.Ticker(selected_stock)
        df_detail = stock_detail.history(start=start_date)
        
        if not df_detail.empty and len(df_detail) > 100:
            df_detail['MA20_plot'] = df_detail['Close'].rolling(window=20).mean()
            df_detail['MA200'] = df_detail['Close'].rolling(window=200).mean()
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df_detail.index, open=df_detail['Open'], high=df_detail['High'], low=df_detail['Low'], close=df_detail['Close'], name='K線'))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA20_plot'], name='20MA 趨勢決策線', line=dict(color='orange', width=2.5)))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA200'], name='200MA 長期生命線', line=dict(color='crimson', width=3)))
            fig.update_layout(xaxis_rangeslider_visible=False, yaxis_title="價格", height=400, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
            info = stock_detail.info if stock_detail.info else {}
            rev_growth = info.get('revenueGrowth')
            rev_growth_str = f"{rev_growth * 100:.1f}%" if rev_growth is not None else "無數據"
                
            is_tw_detail = ".TW" in selected_stock or ".TWO" in selected_stock
            curr_str = "NT$" if is_tw_detail else "美元"
            capex_str = "無數據"

            try:
                cf_q = stock_detail.quarterly_cashflow
                if cf_q is not None and not cf_q.empty:
                    matching_keys = [k for k in cf_q.index if 'Capital Expenditure' in str(k) or 'capital_expenditures' in str(k).lower()]
                    if matching_keys:
                        annual_capex = cf_q.loc[matching_keys[0]].dropna().head(4).sum()
                        if annual_capex != 0:
                            capex_str = f"{abs(annual_capex) / 100000000:.1f} 億{curr_str}"

                clean_ticker = selected_stock.strip().upper()
                if "2330.TW" in clean_ticker or "TSM" in clean_ticker:
                    capex_str = "520億 ~ 560億 美元 (官方指引)"
                else:
                    info_capex = info.get('capitalExpenditure')
                    if info_capex and pd.notna(info_capex):
                        capex_str = f"{abs(info_capex) / 100000000:.1f} 億{curr_str} (市場共識預估)"
            except Exception:
                capex_str = "無數據"
                
            pe_ratio = info.get('trailingPE') or info.get('forwardPE')
            pe_str = f"{pe_ratio:.1f}" if pe_ratio else "無數據"
            
            col_f1, col_f2, col_f3 = st.columns(3)
            col_f1.metric("營收年增率 (YoY)", rev_growth_str)
            col_f2.metric("2026 全年資本支出", capex_str)
            col_f3.metric("當前估值 (PE Ratio)", pe_str)
            
    except Exception as e: 
        st.error(f"分析載入失敗: {e}")
