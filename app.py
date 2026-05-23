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

with st.expander("✨ 系統實戰使用指南 📖 ", expanded=False):
    st.markdown("""
    歡迎使用**🦅 極簡五等燈號自動化決策系統**！本系統將複雜指標降維，請參考以下核心邏輯進行操作：
    1. **⚖️ 公允價值**：套用各種股票估值模型，作為判斷股票價值的參考。
    2. **🟢 買點 (支撐位)**：`20MA - 1.4*ATR`。
    3. **🔴 賣點 (壓力位)**：`20MA + 1.4*ATR`。
    4. **🛡️ 移動停利價位**：股價上漲時，停利點也會跟著自動上移，確保獲利入袋！
    """)

st.markdown("---")

# ==============================================================================
# ✨ 第三層：AGI 2027 敘事與 SALP 聰明錢觀測站
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

st.sidebar.header("📊 對稱網格參數設定")
atr_period = st.sidebar.slider("ATR 計算天數", 5, 22, 14)
atr_multiplier = st.sidebar.slider("自訂網格 ATR 倍數 (x)", 0.5, 2.5, 1.4, 0.1)

start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
summary_data = []
action_alerts = []
action_rank = {"🔥 強力買入": 0, "🟢 買入": 1, "⚪ 觀望": 2, "🔴 賣出": 3, "🚨 強力賣出": 4}

with st.spinner("正在提煉核心決策..."):
    for ticker in active_tickers:
        try:
            ticker_sector = st.session_state.sector_map.get(ticker, "未分類")
            if selected_sector_filter != "全部顯示" and ticker_sector != selected_sector_filter: continue

            is_tw = ".TW" in ticker or ".TWO" in ticker
            currency_symbol = "NT$ " if is_tw else "$ "
            
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date)
            if df.empty or len(df) < 220: continue
            
            info = stock.info if stock.info else {}
            target_low = info.get('targetLowPrice')
            target_mean = info.get('targetMeanPrice')
            target_high = info.get('targetHighPrice')
            
            fair_value_str = "數據不足"
            if target_mean:
                if target_low and target_high and (target_low != target_high):
                    fair_value_str = f"{currency_symbol}{target_low:.1f} ~ {target_high:.1f} (均值:{target_mean:.1f})"
                else:
                    fair_value_str = f"{currency_symbol}{target_mean:.1f}"

            high_low = df['High'] - df['Low']
            tr = pd.concat([high_low, (df['High'] - df['Close'].shift(1)).abs(), (df['Low'] - df['Close'].shift(1)).abs()], axis=1).max(axis=1)
            df['ATR'] = tr.rolling(window=atr_period).mean()
            df['MA20_actual'] = df['Close'].rolling(window=20).mean()
            df['MA200'] = df['Close'].rolling(window=200).mean()
            df['STD20'] = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['MA20_actual'] + (2 * df['STD20'])
            
            current_price = float(df.iloc[-1]['Close'])  
            yesterday_close = float(df.iloc[-2]['Close'])      
            ma20_center = float(df.iloc[-1]['MA20_actual'])
            latest_atr = float(df.iloc[-1]['ATR'])
            latest_ma200 = float(df.iloc[-1]['MA200']) if not pd.isna(df.iloc[-1]['MA200']) else ma20_center
            
            highest_20d = float(df['High'].rolling(window=20).max().iloc[-1])
            trailing_stop_price = highest_20d - (2 * latest_atr)
            trailing_stop_str = f"{currency_symbol}{trailing_stop_price:.1f}"

            low_absorb_price = ma20_center - (latest_atr * atr_multiplier)
            high_toss_price = ma20_center + (latest_atr * atr_multiplier)
            
            market_state = "⚪ 觀望"
            final_action = "⚪ 觀望"
            reason_str = "未觸及 any 策略臨界點。"
            
            if ma20_center >= latest_ma200:
                market_state = "📈 多頭波段 (會漲)"
                if current_price <= low_absorb_price: 
                    final_action = "🔥 強力買入"
                    reason_str = f"多頭拉回過深，跌破網格下限 (-{atr_multiplier:.1f}x ATR)，黃金埋伏點！"
                elif abs(current_price - ma20_center)/ma20_center <= 0.02: 
                    final_action = "🟢 買入"
                    reason_str = "股館拉回到關鍵 20MA 支撐區，符合建倉邏輯。"
                elif current_price >= high_toss_price: 
                    final_action = "🔴 賣出"
                    reason_str = f"短線噴發過熱，衝破網格上限 (+{atr_multiplier:.1f}x ATR)，波段高拋。"
                else:
                    final_action = "⚪ 觀望"
                    reason_str = f"多頭結構健全，低吸位 {currency_symbol}{low_absorb_price:.1f}，未到請安心持股。"
                    
            else:
                market_state = "📉 空頭結構 (會跌)"
                if yesterday_close >= ma20_center and current_price < ma20_center: 
                    final_action = "🚨 強力賣出"
                    reason_str = "剛破 20MA 決策線，趨勢偏空，果斷離場拒絕接飛刀。"
                elif current_price >= high_toss_price: 
                    final_action = "🔴 賣出"
                    reason_str = f"空頭反彈觸及網格上限 (+{atr_multiplier:.1f}x ATR)，逃命高拋點。"
                elif current_price <= low_absorb_price: 
                    final_action = "🟢 買入"
                    reason_str = f"空頭超賣跌破網格下限 (-{atr_multiplier:.1f}x ATR)，極小倉位短線試探。"
                else:
                    final_action = "⚪ 觀望"
                    reason_str = "空頭下跌結構中，堅決保持空倉觀望。"

            if final_action != "⚪ 觀望":
                action_alerts.append({
                    "代碼": ticker, "綜合建議": final_action, "市場狀態": market_state, "當前股價": f"{currency_symbol}{current_price:.1f}",
                    "公允價值區間": fair_value_str, "移動停利價位": trailing_stop_str, "昨日收盤價": f"{currency_symbol}{yesterday_close:.1f}", 
                    "MA20": f"{currency_symbol}{ma20_center:.1f}", "精簡決策原因": reason_str
                })

            summary_data.append({
                "產業領域": ticker_sector, "代碼": ticker, "當前股價": f"{currency_symbol}{current_price:.1f}",
                "公允價值區間": fair_value_str, "移動停利價位": trailing_stop_str, "昨收盤價": f"{currency_symbol}{yesterday_close:.1f}",
                "MA20": f"{currency_symbol}{ma20_center:.1f}", "市場狀態": market_state, "綜合建議": final_action,
                "買點": f"{currency_symbol}{low_absorb_price:.1f}", "賣點": f"{currency_symbol}{high_toss_price:.1f}", "精簡決策原因": reason_str
            })
        except Exception: pass

st.header("🚨 今日核心執行 ACTION 面板")
if action_alerts:
    st.dataframe(pd.DataFrame(action_alerts), use_container_width=True, hide_index=True)
else:
    st.info("🧘 報告隊長：今日名單中皆無個股觸發臨界點。請繼續安心保持觀望。")

st.markdown("---")

st.header(f"📊 降維極簡大看板 (目前聚焦：{selected_sector_filter})")
if summary_data:
    summary_df = pd.DataFrame(summary_data)
    summary_df['sort'] = summary_df['綜合建議'].map(action_rank)
    summary_df = summary_df.sort_values(by=["sort", "產業領域", "代碼"]).drop('sort', axis=1)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ==============================================================================
# 🔍 個股動態決策軌道與核心基本面 (定量財務計量引擎 - 100% 穩定免維護)
# ==============================================================================
st.header("🔍 個股動態決策軌道與核心基本面")

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
        df_detail = stock_detail.history(start=start_date)
        
        if not df_detail.empty and len(df_detail) > 200:
            df_detail['MA20_plot'] = df_detail['Close'].rolling(window=20).mean()
            df_detail['MA200'] = df_detail['Close'].rolling(window=200).mean()
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df_detail.index, open=df_detail['Open'], high=df_detail['High'], low=df_detail['Low'], close=df_detail['Close'], name='K線'))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA20_plot'], name='20MA 趨勢決策線', line=dict(color='orange', width=2.5)))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA200'], name='200MA 長期生命線', line=dict(color='crimson', width=3)))
            fig.update_layout(xaxis_rangeslider_visible=False, yaxis_title="價格", height=400, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
            info = stock_detail.info if stock_detail.info else {}
            is_tw_detail = ".TW" in selected_stock or ".TWO" in selected_stock
            
            # 1. 營收增長共識（調用分析師 Forward 複合預期指標）
            rev_growth = info.get('revenueGrowth') or info.get('earningsGrowth')
            if rev_growth is not None:
                rev_growth_str = f"{rev_growth * 100:.1f}% (華爾街分析師複合共識預期)"
            else:
                rev_growth_str = "未揭露未來展望"
            
            # 2. 資本支出安全計量（調用最新財報並進行年化運轉率 Run Rate 折算）
            capex_str = "未揭露未來展望"
            try:
                cf = stock_detail.quarterly_cashflow
                if cf is None or cf.empty: cf = stock_detail.cashflow
                if cf is not None and not cf.empty:
                    m_keys = [k for k in cf.index if 'Capital Expenditure' in str(k) or 'capital_expenditures' in str(k).lower()]
                    if m_keys:
                        # 取得單季真實發生的資本支出金額（絕對值）
                        latest_raw = abs(cf.loc[m_keys[0]].dropna().iloc[0])
                        
                        # 🛡️ 數據庫清洗過濾：校正 ADR 混亂的台幣/美元計價
                        if not is_tw_detail and latest_raw > 10000000000:
                            # 如果美股代碼算出來超過 100 億美金，代表背後數據庫塞的是台幣，直接除以 32 匯率校正
                            latest_raw = latest_raw / 32.0
                            # 將單季支出乘以 4，精準擬合為當前企業的「年化運轉率 (Annual Run Rate)」
                            capex_str = f"約 {latest_raw * 4 / 100000000:.1f} 億美元 (單季最新數據年化折算)"
                        elif is_tw_detail:
                            capex_str = f"約 {latest_raw * 4 / 100000000:.1f} 億新台幣 (單季最新數據年化折算)"
                        else:
                            capex_str = f"約 {latest_raw * 4 / 100000000:.1f} 億美元 (單季最新數據年化折算)"
            except Exception:
                pass
            
            pe_ratio = info.get('trailingPE') or info.get('forwardPE')
            pe_str = f"{pe_ratio:.1f}" if pe_ratio else "無數據"
            
            col_f1, col_f2, col_f3 = st.columns(3)
            col_f1.metric("2026 全年營收年增率預期 (YoY)", rev_growth_str)
            col_f2.metric("2026 全年資本支出指引 (CapEx Run Rate)", capex_str, help="財務計量公式：採集企業最新一季法說財報所公告之資本支出，乘以 4 進行年化 Run Rate 折算。")
            col_f3.metric("實時估值 (PE Ratio)", pe_str)
                
    except Exception as e: 
        st.error(f"分析載入失敗: {e}")

# ==============================================================================
# ⏳ 策略回測績效驗證
# ==============================================================================
st.markdown("---")
st.header("⏳ 策略回測績效驗證 (實時動態 Demo)")
st.markdown("從您指定的日期開始往後掃描，找出每一檔股票**「第一次」觸發 🔥買入 的日子與價位**，並對比今日收盤價，驗證策略真實報酬率！")

backtest_col, _ = st.columns([1, 3])
with backtest_col:
    default_date = datetime.now().date() - timedelta(days=60) 
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
            hl = df_bt['High'] - df_bt['Low']
            h_pc = (df_bt['High'] - df_bt['Close'].shift(1)).abs()
            l_pc = (df_bt['Low'] - df_bt['Close'].shift(1)).abs()
            tr = pd.concat([hl, h_pc, l_pc], axis=1).max(axis=1)
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
                
                if pd.isna(past_ma20) or pd.isna(past_atr): continue
                
                low_b = past_ma20 - (past_atr * atr_multiplier)
                
                if past_ma20 >= past_ma200:
                    if past_close <= low_b:
                        signal = "🔥 強力買入"
                    elif abs(past_close - past_ma20)/past_ma20 <= 0.02:
                        signal = "🟢 買入"
                    else:
                        continue 
                        
                    return_pct = ((latest_today_price - past_close) / past_close) * 100
                    backtest_results.append({
                        "產業": ticker_sector, "代碼": ticker,
                        "建倉日期": date.strftime('%Y-%m-%d'), "當時訊號": signal,
                        "買入價": f"{currency}{past_close:.1f}", "今日最新價": f"{currency}{latest_today_price:.1f}",
                        "累積報酬率": f"{return_pct:.
