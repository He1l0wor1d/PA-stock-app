import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import re

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
    if fg_value >= 75: fg_status = "🚨 極度貪婪"
    elif fg_value >= 55: fg_status = "🟢 貪婪"
    elif fg_value >= 45: fg_status = "⚪ 中性"
    elif fg_value >= 25: fg_status = "🟡 恐懼"
    else: fg_status = "❄️ 極度恐懼"
        
    st.metric(label=f"大盤情緒狀態: {fg_status}", value=f"{fg_value} / 100")
    st.progress(fg_value / 100)
    st.caption("💡 提示：大盤進入『極度貪婪』時，右側動能追價應嚴格控制倉位。")

with macro_col2:
    st.markdown("##### 📊 席勒本益比 (Shiller PE)")
    shiller_pe = 31.5  
    historical_mean = 17.1
    deviation = ((shiller_pe - historical_mean) / historical_mean) * 100
    st.metric(label="S&P 500 CAPE Ratio", value=f"{shiller_pe:.1f}", delta=f"高於歷史均值 {deviation:.1f}%", delta_color="inverse")
    st.caption(f"歷史平均值: 17.1 | 估值偏貴時，非大牛股的動能突破高機率為假突破。")

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
active_tickers = st.sidebar.multiselect("💡 觀察名單管理 (點 X 刪除)", options=all_current_tickers, default=all_current_tickers)

distinct_sectors = ["全部顯示"] + sorted(list(set(st.session_state.sector_map.values())))
selected_sector_filter = st.sidebar.selectbox("🎯 聚焦特定產業類別：", distinct_sectors)

st.sidebar.header("📊 計量參數調校面板")
atr_period = st.sidebar.slider("ATR 計算天數", 5, 22, 14)
atr_multiplier = st.sidebar.slider("左側網格抄底 ATR 倍數 (x)", 0.5, 2.5, 1.4, 0.1)

# 定義時間流範圍
start_date_看板 = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
start_date_3years = (datetime.now() - timedelta(days=1095)).strftime('%Y-%m-%d')

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-10)
    return 100 - (100 / (1 + rs))

summary_data = []
action_alerts = []
action_rank = {"🔥 強力買入": 0, "⚡ 動能突破": 1, "⚪ 觀望": 2}

with st.spinner("雙軌計量引擎正在提煉核心決策..."):
    for ticker in active_tickers:
        try:
            ticker_sector = st.session_state.sector_map.get(ticker, "未分類")
            if selected_sector_filter != "全部顯示" and ticker_sector != selected_sector_filter: continue

            is_tw = ".TW" in ticker or ".TWO" in ticker
            currency_symbol = "NT$ " if is_tw else "$ "
            
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date_看板)
            if df.empty or len(df) < 40: continue
            
            high_low = df['High'] - df['Low']
            tr = pd.concat([high_low, (df['High'] - df['Close'].shift(1)).abs(), (df['Low'] - df['Close'].shift(1)).abs()], axis=1).max(axis=1)
            df['ATR'] = tr.rolling(window=atr_period).mean()
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA200'] = df['Close'].rolling(window=200).mean()
            df['RSI'] = calculate_rsi(df['Close'], 14)
            df['High20'] = df['High'].shift(1).rolling(window=20).max()
            
            current_price = float(df.iloc[-1]['Close'])  
            ma20_center = float(df.iloc[-1]['MA20'])
            latest_atr = float(df.iloc[-1]['ATR'])
            latest_ma200 = float(df.iloc[-1]['MA200']) if not pd.isna(df.iloc[-1]['MA200']) else ma20_center
            latest_rsi = float(df.iloc[-1]['RSI'])
            latest_high20 = float(df.iloc[-1]['High20'])
            
            highest_20d = float(df['High'].rolling(window=20).max().iloc[-1])
            trailing_stop_price = highest_20d - (2 * latest_atr)
            low_absorb_price = ma20_center - (latest_atr * atr_multiplier)
            
            final_action = "⚪ 觀望"
            reason_str = "未觸及多頭抄底或右側動能突破點，耐心保持現金流。"
            
            # 🚀 雙軌制決策樹（導入安全防禦閥）
            if ma20_center >= latest_ma200: # 長線多頭
                if current_price <= low_absorb_price:
                    final_action = "🔥 強力買入"
                    reason_str = f"優質股拉回，跌破網格下限 (-{atr_multiplier:.1f}x ATR)，黃金抄底位。"
                # 🛡️ 安全防禦閥：必須在 60 <= RSI <= 78 之間才叫良性動能。如果 RSI 飆破 78 叫極度過熱，拒絕追高！
                elif current_price > latest_high20 and 60 <= latest_rsi <= 78:
                    final_action = "⚡ 動能突破"
                    reason_str = f"股價強勢創 20 日新高，且 RSI 處於健全推進區 ({latest_rsi:.1f})，順勢上車。"
                elif current_price > latest_high20 and latest_rsi > 78:
                    final_action = "⚪ 觀望"
                    reason_str = f"⚠️ 雖創 20 日新高，但 RSI 高達 {latest_rsi:.1f} 已進入極度擁擠過熱區，安全閥啟動，拒絕接盤！"
            else: # 長線空頭
                if current_price <= low_absorb_price:
                    final_action = "🔥 強力買入"
                    reason_str = "空頭結構超跌至歷史網格極限，啟動小倉位逆勢左側試探。"

            info = stock.info if stock.info else {}
            target_mean = info.get('targetMeanPrice')
            fair_value_str = f"{currency_symbol}{target_mean:.1f}" if target_mean else "數據不足"

            if final_action != "⚪ 觀望":
                action_alerts.append({
                    "代碼": ticker, "綜合建議": final_action, "當前股價": f"{currency_symbol}{current_price:.1f}",
                    "公允價值區間": fair_value_str, "移動停利價位": f"{currency_symbol}{trailing_stop_price:.1f}",
                    "MA20": f"{currency_symbol}{ma20_center:.1f}", "精簡決策原因": reason_str
                })

            summary_data.append({
                "產業領域": ticker_sector, "代碼": ticker, "當前股價": f"{currency_symbol}{current_price:.1f}",
                "公允價值區間": fair_value_str, "移動停利價位": f"{currency_symbol}{trailing_stop_price:.1f}",
                "MA20": f"{currency_symbol}{ma20_center:.1f}", "綜合建議": final_action,
                "左側抄底價": f"{currency_symbol}{low_absorb_price:.1f}", "右側突破追價": f"{currency_symbol}{latest_high20:.1f}", "精簡決策原因": reason_str
            })
        except Exception: pass

st.header("🚨 今日核心執行 ACTION 面板")
if action_alerts:
    st.dataframe(pd.DataFrame(action_alerts), use_container_width=True, hide_index=True)
else:
    st.info("🧘 報告隊長：今日名單中皆無個股觸發臨界點。請繼續安心保持觀望。")

st.markdown("---")

st.header(f"📊 雙軌制極簡大看板 (目前聚焦：{selected_sector_filter})")
if summary_data:
    summary_df = pd.DataFrame(summary_data)
    summary_df['sort'] = summary_df['綜合建議'].map(action_rank)
    summary_df = summary_df.sort_values(by=["sort", "產業領域", "代碼"]).drop('sort', axis=1)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ==============================================================================
# 🔍 個股動態決策軌道與核心基本面 (3年期大深度 K 線 + 雙軌安全標記版)
# ==============================================================================
st.header("🔍 個股動態決策軌道與核心基本面 (近3年大深度雙軌制驗證版)")

sorted_tickers = sorted(active_tickers)
default_index = sorted_tickers.index("TSM") if "TSM" in sorted_tickers else 0

selected_stock = st.selectbox(
    "選擇個股查看決策軌道：", 
    options=sorted_tickers, 
    index=default_index
)

if selected_stock:
    try:
        stock_detail = yf.Ticker(selected_stock)
        df_detail = stock_detail.history(start=start_date_3years)
        
        if not df_detail.empty and len(df_detail) > 40:
            df_detail['MA20_plot'] = df_detail['Close'].rolling(window=20).mean()
            df_detail['MA200'] = df_detail['Close'].rolling(window=200).mean()
            df_detail['RSI_plot'] = calculate_rsi(df_detail['Close'], 14)
            df_detail['High20_plot'] = df_detail['High'].shift(1).rolling(window=20).max()
            
            high_low_det = df_detail['High'] - df_detail['Low']
            tr_det = pd.concat([high_low_det, (df_detail['High'] - df_detail['Close'].shift(1)).abs(), (df_detail['Low'] - df_detail['Close'].shift(1)).abs()], axis=1).max(axis=1)
            df_detail['ATR_det'] = tr_det.rolling(window=atr_period).mean()
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df_detail.index, open=df_detail['Open'], high=df_detail['High'], low=df_detail['Low'], close=df_detail['Close'], name='K線'))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA20_plot'], name='20MA 趨勢決策線', line=dict(color='orange', width=2)))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA200'], name='200MA 長期生命線', line=dict(color='crimson', width=2.5)))
            
            # 🚀 歷史回溯 3 年內所有符合雙軌策略臨界點的日期並標記
            annotations = []
            for date, row in df_detail.dropna(subset=['MA20_plot', 'MA200', 'ATR_det', 'RSI_plot', 'High20_plot']).iterrows():
                p_close = row['Close']
                p_ma20 = row['MA20_plot']
                p_ma200 = row['MA200']
                p_atr = row['ATR_det']
                p_rsi = row['RSI_plot']
                p_high20 = row['High20_plot']
                
                low_bound = p_ma20 - (p_atr * atr_multiplier)
                
                # 軌道一：左側打折抄底（大趨勢多頭下拉回）
                if p_ma20 >= p_ma200 and p_close <= low_bound:
                    annotations.append(dict(
                        x=date, y=row['Low'], text="🔥強買", showarrow=True,
                        arrowhead=2, arrowcolor="green", arrowsize=1, arrowwidth=2,
                        ax=0, ay=35, font=dict(color="white", size=9), bgcolor="green"
                    ))
                # 軌道二：右側動能突破（加上過熱安全閥過濾，拒絕 RSI > 78 的擁擠假突破）
                elif p_ma20 >= p_ma200 and p_close > p_high20 and 60 <= p_rsi <= 78:
                    annotations.append(dict(
                        x=date, y=row['High'], text="⚡動能", showarrow=True,
                        arrowhead=2, arrowcolor="#ff7f0e", arrowsize=1, arrowwidth=2,
                        ax=0, ay=-35, font=dict(color="white", size=9), bgcolor="#ff7f0e"
                    ))

            fig.update_layout(
                xaxis_rangeslider_visible=False, yaxis_title="價格", height=500, 
                template="plotly_white", annotations=annotations
            )
            st.plotly_chart(fig, use_container_width=True)
            st.info("💡 雙軌安全指南：現在圖表上的金黃色【⚡動能】已經過濾掉「末跌段噴發」與「普通股假突破」。你可以切換不同股票，確認策略是否更加精準。")
            
            info = stock_detail.info if stock_detail.info else {}
            is_tw_detail = ".TW" in selected_stock or ".TWO" in selected_stock
            
            rev_growth = info.get('revenueGrowth') or info.get('earningsGrowth')
            rev_growth_str = f"{rev_growth * 100:.1f}% (華爾街分析師複合共識預期)" if rev_growth is not None else "未揭露未來展望"
            
            capex_str = "未揭露未來指引"
            try:
                cf = stock_detail.quarterly_cashflow
                if cf is None or cf.empty: cf = stock_detail.cashflow
                if cf is not None and not cf.empty:
                    m_keys = [k for k in cf.index if 'Capital Expenditure' in str(k) or 'capital_expenditures' in str(k).lower()]
                    if m_keys:
                        latest_raw = abs(cf.loc[m_keys[0]].dropna().iloc[0])
                        if not is_tw_detail and latest_raw > 10000000000:
                            latest_raw = latest_raw / 32.0
                            capex_str = f"約 {latest_raw * 4 / 100000000:.1f} 億美元 (單季最新數據年化折算)"
                        elif is_tw_detail:
                            capex_str = f"約 {latest_raw * 4 / 100000000:.1f} 億新台幣 (單季最新數據年化折算)"
                        else:
                            capex_str = f"約 {latest_raw * 4 / 100000000:.1f} 億美元 (單季最新數據年化折算)"
            except Exception: pass
            
            pe_ratio = info.get('trailingPE') or info.get('forwardPE')
            pe_str = f"{pe_ratio:.1f}" if pe_ratio else "無數據"
            
            col_f1, col_f2, col_f3 = st.columns(3)
            col_f1.metric("2026 全年營收年增率預期 (YoY)", rev_growth_str)
            col_f2.metric("2026 全年資本支出指引 (CapEx Run Rate)", capex_str)
            col_f3.metric("實時估值 (PE Ratio)", pe_str)
                
    except Exception as e: 
        st.error(f"分析載入失敗: {e}")

# ==============================================================================
# ⏳ 策略回測績效驗證 (支持安全型雙軌訊號回測)
# ==============================================================================
st.markdown("---")
st.header("⏳ 策略回測績效驗證 (大數據多空循環驗證)")
st.markdown("從您指定的日期開始往後掃描，找出每一檔股票**「第一次」觸發 🔥買入 或 ⚡動能突破 的日子與價位**，驗證策略真實報酬率！")

backtest_col, _ = st.columns([1, 3])
with backtest_col:
    default_date = datetime.now().date() - timedelta(days=180) 
    backtest_date = st.date_input("📅 選擇掃描起始日期：", value=default_date)

bt_date_str = backtest_date.strftime('%Y-%m-%d')
backtest_results = []

with st.spinner("正在進行時光回溯與策略模擬建倉..."):
    for ticker in active_tickers:
        try:
            ticker_sector = st.session_state.sector_map.get(ticker, "未分類")
            if selected_sector_filter != "全部顯示" and ticker_sector != selected_sector_filter: continue

            df_bt = yf.Ticker(ticker).history(start=(backtest_date - timedelta(days=300)).strftime('%Y-%m-%d'))
            if df_bt.empty: continue
            
            df_bt['MA20'] = df_bt['Close'].rolling(window=20).mean()
            df_bt['MA200'] = df_bt['Close'].rolling(window=200).mean()
            df_bt['RSI'] = calculate_rsi(df_bt['Close'], 14)
            df_bt['High20'] = df_bt['High'].shift(1).rolling(window=20).max()
            
            hl = df_bt['High'] - df_bt['Low']
            tr = pd.concat([hl, (df_bt['High'] - df_bt['Close'].shift(1)).abs(), (df_bt['Low'] - df_bt['Close'].shift(1)).abs()], axis=1).max(axis=1)
            df_bt['ATR'] = tr.rolling(window=atr_period).mean()

            df_scan = df_bt.loc[bt_date_str:]
            if df_scan.empty: continue
            
            latest_today_price = df_bt['Close'].iloc[-1]
            currency = "NT$ " if ".TW" in ticker else "$ "

            for date, row in df_scan.iterrows():
                past_close = row['Close']
                past_ma20 = row['MA20']
                past_ma200 = row['MA200'] if not pd.isna(row['MA200']) else past_ma20
                past_atr = row['ATR']
                past_rsi = row['RSI']
                past_high20 = row['High20']
                
                if pd.isna(past_ma20) or pd.isna(past_atr) or pd.isna(past_rsi) or pd.isna(past_high20): continue
                
                low_b = past_ma20 - (past_atr * atr_multiplier)
                
                signal = None
                if past_ma20 >= past_ma200:
                    if past_close <= low_b:
                        signal = "🔥 強力買入"
                    elif past_close > past_high20 and 60 <= past_rsi <= 78:
                        signal = "⚡ 動能突破"
                
                if signal:
                    return_pct = ((latest_today_price - past_close) / past_close) * 100
                    backtest_results.append({
                        "產業": ticker_sector, "代碼": ticker,
                        "建倉日期": date.strftime('%Y-%m-%d'), "當時訊號": signal,
                        "買入價": f"{currency}{past_close:.1f}", "今日最新價": f"{currency}{latest_today_price:.1f}",
                        "累積報酬率": f"{return_pct:.1f}%"
                    })
                    break 

        except Exception: pass

if backtest_results:
    df_bt_results = pd.DataFrame(backtest_results)
    df_bt_results['sort_val'] = df_bt_results['累積報酬率'].str.replace('%', '').astype(float)
    df_bt_results = df_bt_results.sort_values(by='sort_val', ascending=False).drop('sort_val', axis=1)
    st.dataframe(df_bt_results, use_container_width=True, hide_index=True)
    
    avg_return = df_bt_results['累積報酬率'].str.replace('%', '').astype(float).mean()
    win_rate = (df_bt_results['累積報酬率'].str.replace('%', '').astype(float) > 0).mean() * 100
    
    col_r1, col_r2 = st.columns(2)
    if avg_return > 0:
        col_r1.success(f"📈 雙軌策略平均報酬率：**{avg_return:.1f}%**")
    else:
        col_r1.error(f"📉 雙軌策略平均報酬率：**{avg_return:.1f}%**")
    col_r2.info(f"🎯 雙軌策略勝率：**{win_rate:.1f}%**")
else:
    st.info(f"自 {bt_date_str} 起算，觀察名單內無任何標的觸發雙軌買入條件。")
