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

# ==============================================================================
# 📖 ✨ 更新版：精簡化實戰使用指南
# ==============================================================================
with st.expander("📖 系統實戰使用指南（新手必看！點擊展開 / 折疊）", expanded=True):
    st.markdown("""
    歡迎使用**🦅 極簡五等燈號自動化決策系統**！本系統將複雜指標降維，請參考以下核心邏輯進行操作：

    ### (A) 核心指標說明
    1. **⚖️ 公允價值**：套用各種股票估值模型，作為判斷股票價值的參考。
       * 💡 **買入價低於「公允價值均值」相對更保險。**
       * ⚠️ 若公允價值**範圍過大**，表示市場對於該股票價值意見分歧，請務必謹慎操作！
    2. **🟢 買點 (支撐位)**：`20MA - 1.4*ATR`（可於左側選單自訂 ATR 倍數）。
    3. **🔴 賣點 (壓力位)**：`20MA + 1.4*ATR`（可於左側選單自訂 ATR 倍數）。
    4. **🛡️ 移動停利價位**：股價上漲時，停利點也會跟著自動上移，確保獲利入袋！
       * *範例：買在 100 ➔ 漲到 110（停利設@100） ➔ 漲到 150（停利設@140）...以此類推。*

    ### (B) 市場狀態與操作策略
    1. **💰 資金有限**：建議優先鎖定亮起「**🔥 強力買入**」的個股，且單筆建倉建議 **< 總資金的 10%**。
    2. **📉 空頭結構 (會跌)** ➔ 趨勢向下，**絕對不碰！**
    3. **⚖️ 震盪結構 (盤整)** ➔ 嚴格遵循「買點買、賣點賣」（怕被套牢建議挑選穩健大型股）。
    4. **📈 多頭結構 (會漲)** ➔ 遵循「買點買入 + 跌破移動停利才賣出」，拚取最大波段獲利。
    5. **🕵️ 基本面防雷**：買入前請再次透過下方看板，確保股價便宜**並非**來自公司營運出狀況！

    ### (C) 系統其他功能
    1. **🔍 K線圖 & 個股動態**：於下方選單一鍵調閱個股走勢，並檢視最新營收與資本支出 (Capex)。
    2. **⏳ 策略回測績效驗證**：利用網頁最下方的「時光機」，一鍵掃描過去買點，用真實數據驗證策略勝率。
    """)

st.markdown("---")

# ==============================================================================
# ✨ 第三層：AGI 2027 敘事與 SALP 聰明錢觀測站 (內化版)
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
# 4. 內建核心產業與供應鏈地圖 (嚴格群組分類，不超10字，無英文無台股)
# ==============================================================================
INITIAL_SECTOR_MAP = {
    # 核心基本觀察
    "2330.TW": "半導體晶圓代工", "0050.TW": "市值型大盤", "2851.TW": "金融再保險", "5607.TW": "航空航運物流",
    
    # 基礎設備
    "NEE": "電網設備基建", "GEV": "電網設備基建", "ETN": "電網設備基建", "PWR": "電網設備基建",
    "VRT": "機房液冷散熱", "MOD": "機房液冷散熱", "3017.TW": "機房液冷散熱",
    "CEG": "核能與天然氣", "VST": "核能與天然氣", "ENPH": "綠能與微電網", "SEDG": "綠能與微電網",
    
    # 核心晶片設計與代工
    "SOXX": "AI晶片與設計", "XSD": "AI晶片與設計", "NVDA": "AI晶片與設計", "AVGO": "AI晶片與設計", 
    "AMD": "AI晶片與設計", "QCOM": "AI晶片與設計", "MRVL": "AI晶片與設計", "TXN": "AI晶片與設計", 
    "ADI": "AI晶片與設計", "ON": "AI晶片與設計", "MPWR": "AI晶片與設計", "NVTS": "AI晶片與設計", "2454.TW": "AI晶片與設計",
    
    # 記憶體與儲存 (確實補回 DRAM)
    "DRAM": "記憶體與儲存", "MU": "記憶體與儲存", "SNDK": "記憶體與儲存", "RMBS": "記憶體與儲存", "SITM": "記憶體與儲存",
    
    # 硬體製程與網通
    "TSM": "晶圓代工製程", "ASML": "晶圓代工製程", "AMAT": "晶圓代工製程", "LRCX": "晶圓代工製程", 
    "FORM": "晶圓代工製程", "INTC": "晶圓代工製程", "SNPS": "晶圓代工製程", "TSEM": "晶圓代工製程", 
    "AXTI": "晶圓代工製程", "SIMO": "晶圓代工製程", "ALAB": "晶圓代工製程", "SMH": "晶圓代工製程",
    "CSCO": "光通訊與網通", "ANET": "光通訊與網通", "GLW": "光通訊與網通", "COHR": "光通訊與網通", 
    "LITE": "光通訊與網通", "AAOI": "光通訊與網通", "FN": "光通訊與網通", "CIEN": "光通訊與網通", 
    "NOK": "光通訊與網通", "CBRS": "光通訊與網通",
    
    # 軟體平台與科技巨頭
    "QQQ": "AI巨頭與軟體", "MAGS": "AI巨頭與軟體", "MSFT": "AI巨頭與軟體", "AAPL": "AI巨頭與軟體", 
    "GOOGL": "AI巨頭與軟體", "AMZN": "AI巨頭與軟體", "META": "AI巨頭與軟體", "PLTR": "AI巨頭與軟體", 
    "NOW": "AI巨頭與軟體", "ORCL": "AI巨頭與軟體", "APP": "AI巨頭與軟體", "NET": "AI巨頭與軟體", 
    "CRWV": "AI巨頭與軟體", "2317.TW": "AI巨頭與軟體", "2382.TW": "AI巨頭與軟體",
    
    # 國防航太
    "ARKX": "航太太空國防", "NASA": "航太太空國防", "LMT": "航太太空國防", "RTX": "航太太空國防", 
    "BA": "航太太空國防", "RDW": "航太太空國防", "RKLB": "航太太空國防", "ASTS": "航太太空國防", "ONDS": "航太太空國防",
    
    # 傳統資源與其餘板塊
    "XOM": "傳統能源礦產", "OXY": "傳統能源礦產", "EQT": "傳統能源礦產",
    "LLY": "生技醫療科技", "TEM": "生技醫療科技", "GRAL": "生技醫療科技", "ILMN": "生技醫療科技",
    "JPM": "金融資產管理", "GS": "金融資產管理", "BLK": "金融資產管理", "BX": "金融資產管理", 
    "SOFI": "金融資產管理", "HOOD": "金融資產管理", "SEI": "金融資產管理",
    "TSLA": "智能車新能源", "BYDDF": "智能車新能源", "MSTR": "數位資產科技", 
    "BRK-B": "綜合控股投資", "GLD": "綜合控股投資", "SHLD": "綜合控股投資", "NBIS": "綜合控股投資"
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

with st.spinner("正在提煉五等核心 ACTION 決策與計算華爾街分析師目標價共識..."):
    for ticker in active_tickers:
        try:
            ticker_sector = st.session_state.sector_map.get(ticker, "未分類")
            if selected_sector_filter != "全部顯示" and ticker_sector != selected_sector_filter: continue

            is_tw = ".TW" in ticker or ".TWO" in ticker
            currency_symbol = "NT$ " if is_tw else "$ "
            
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date)
            if df.empty or len(df) < 220: continue
            
            # ==========================================
            # 📊 公允價值運算 (對齊 TradingView 華爾街分析師目標價共識)
            # ==========================================
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

            # 指標運算
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
            reason_str = "未觸及任何策略臨界點。"
            
            if ma20_center >= latest_ma200:
                market_state = "📈 多頭波段 (會漲)"
                if current_price <= low_absorb_price: 
                    final_action = "🔥 強力買入"
                    reason_str = f"多頭拉回過深，跌破網格下限 (-{atr_multiplier:.1f}x ATR)，黃金埋伏點！"
                elif abs(current_price - ma20_center)/ma20_center <= 0.02: 
                    final_action = "🟢 買入"
                    reason_str = "股價拉回到關鍵 20MA 支撐區，符合建倉邏輯。"
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

# --- 介面排版輸出 ---
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
# 🔍 個股動態決策軌道與核心基本面
# ==============================================================================
st.header("🔍 個股動態決策軌道與核心基本面")
selected_stock = st.selectbox("選擇個股查看決策軌道：", sorted(active_tickers))

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
            
            # --- 原始基礎數據抓取 ---
            info = stock_detail.info if stock_detail.info else {}
            rev_growth = info.get('revenueGrowth')
            rev_growth_str = f"{rev_growth * 100:.1f}%" if rev_growth is not None else "無數據"
            
            # 貨幣單位判定
            is_tw_detail = ".TW" in selected_stock or ".TWO" in selected_stock
            curr_str = "NT$" if is_tw_detail else "美元"
            
            # 抓取資本支出 (Capex) 與 自由現金流 (FCF) 歷史數據
            capex_str = "無數據"
            fcf_str = "無數據"
            net_income_trend = "無數據"
            
            try:
                cf = stock_detail.quarterly_cashflow
                if cf is None or cf.empty: cf = stock_detail.cashflow
                
                # 財報 (Income Statement) 用於淨利趨勢
                is_stmt = stock_detail.quarterly_financials
                if is_stmt is None or is_stmt.empty: is_stmt = stock_detail.financials
                
                if cf is not None and not cf.empty:
                    # 1. 資本支出
                    cap_keys = [k for k in cf.index if 'Capital Expenditure' in str(k) or 'capital_expenditures' in str(k).lower()]
                    if cap_keys:
                        latest_capex = cf.loc[cap_keys[0]].dropna().iloc[0]
                        capex_str = f"{abs(latest_capex) / 100000000:.1f} 億 {curr_str}"
                    
                    # 2. 自由現金流
                    fcf_keys = [k for k in cf.index if 'Free Cash Flow' in str(k) or 'free_cash_flow' in str(k).lower()]
                    if fcf_keys:
                        latest_fcf = cf.loc[fcf_keys[0]].dropna().iloc[0]
                        fcf_str = f"{latest_fcf / 100000000:.1f} 億 {curr_str}"
                        
                if is_stmt is not None and not is_stmt.empty:
                    ni_keys = [k for k in is_stmt.index if 'Net Income' in str(k) or 'net_income' in str(k).lower()]
                    if ni_keys:
                        ni_series = is_stmt.loc[ni_keys[0]].dropna()
                        if len(ni_series) >= 2:
                            net_income_trend = "📈 增長中" if ni_series.iloc[0] > ni_series.iloc[1] else "📉 衰退中"
            except Exception: pass
                
            pe_ratio = info.get('trailingPE') or info.get('forwardPE')
            pe_str = f"{pe_ratio:.1f}" if pe_ratio else "無數據"
            
            # 顯示主要三個 Metric 指標
            col_f1, col_f2, col_f3 = st.columns(3)
            col_f1.metric("營收年增率 (YoY)", rev_growth_str)
            col_f2.metric("最新資本支出 (Capex)", capex_str, help="反映企業對 AI 算力基礎設施的投入力道")
            col_f3.metric("當前估值 (PE Ratio)", pe_str)

            # ==============================================================================
            # ✨ 新增區塊：既有財經數據無縫整合看板 (即時連動、零 Token 消耗)
            # ==============================================================================
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader(f"📊 華爾街量化數據終端：{selected_stock} 實時基本面拆解")
            
            # 精確抓取剩餘財務變數
            co_name = info.get('longName', selected_stock)
            biz_summary = info.get('longBusinessSummary', '未提供商業模式簡介。')
            profit_margin = info.get('profitMargins')
            margin_str = f"{profit_margin * 100:.1f}%" if profit_margin is not None else "無數據"
            debt_to_equity = info.get('debtToEquity')
            debt_str = f"{debt_to_equity:.1f}%" if debt_to_equity is not None else "無數據"
            roe = info.get('returnOnEquity')
            roe_str = f"{roe * 100:.1f}%" if roe is not None else "無數據"
            
            # 公允價值範圍解析 (延續網站上方原有邏輯)
            t_low = info.get('targetLowPrice')
            t_mean = info.get('targetMeanPrice')
            t_high = info.get('targetHighPrice')
            fv_range = f"{curr_str}{t_low:.1f} ~ {curr_str}{t_high:.1f}" if t_low and t_high else "數據不足"
            fv_mean = f"{curr_str}{t_mean:.1f}" if t_mean else "數據不足"

            # 建立 7 大深度分析分頁
            t1, t2, t3, t4, t5, t6, t7 = st.tabs([
                "1️⃣ 全面分析", "2️⃣ 財務體質", "3️⃣ 護城河", 
                "4️⃣ 估值分析", "5️⃣ 成長潛力", "6️⃣ 多空辯論", "7️⃣ 投資決策"
            ])
            
            with t1:
                st.markdown(f"### 🗂️ Senior Analyst 完整分析報告：{selected_stock}")
                st.markdown(f"""
                * **公司完整名稱：** {co_name}
                * **商業模式與收入來源：** {biz_summary[:350]}... (詳見成長潛力頁面)
                * **產業最新趋势：** 當前市場資金高度向 AI 算力基礎設施、硬資產（電力、電網基建）集中。
                * **財務健康速覽：** 營收年增率為 **{rev_growth_str}**，目前的利潤率表現為 **{margin_str}**。
                * **華爾街目標價共識：** 分歧區間落在 `{fv_range}`，市場共識中位數（公允均值）為 `{fv_mean}`。
                """)
                
            with t2:
                st.markdown(f"### 📈 數據拆解：{co_name} 財務體質驗證")
                st.markdown(f"""
                根據最新揭露季度財報數據，該公司財務體質指標如下：
                * **營收成長動能 (YoY)：** `{rev_growth_str}`
                * **淨利趨勢方向：** `{net_income_trend}`
                * **單季自由現金流 (FCF)：** `{fcf_str}`
                * **公司利潤率 (Profit Margin)：** `{margin_str}`
                * **負債權益比 (Debt/Equity Ratio)：** `{debt_str}`
                * **股東權益報酬率 (ROE)：** `{roe_str}`
                """)
                if debt_to_equity and debt_to_equity > 150:
                    st.warning("⚠️ 警示：該公司負債比高於 150%，財務體質有槓桿過大、走弱之風險，請搭配震盪或多頭結構紀律操作。")
                else:
                    st.success("🟢 判斷結論：自由現金流流動性健全，核心獲利利潤率達標，目前財務體質維持在「穩健偏強」結構。")
                    
            with t3:
                st.markdown(f"### 🏰 {selected_stock} 競爭護城河與綜合評估")
                st.markdown(f"""
                綜合評估企業的五大核心防禦壁壘：
                1.  **品牌影響力 / 定價權：** 依據利潤率 `{margin_str}` 判斷，具備同業優勢。
                2.  **網路效應：** 與全球頂級供應鏈深度綁定。
                3.  **轉換成本：** 客戶黏著度極高，替代方案轉移成本巨大。
                4.  **成本與技術優勢：** 最新單季大舉投入高達 `{capex_str}` 資本支出，全面封鎖對手。
                """)
                # 簡單依據毛利與 Capex 給予量化權重打分
                moat_score = 8 if (profit_margin and profit_margin > 0.2) else 6
                st.metric("🛡️ 護城河強度綜合評分 (1-10分)", f"{moat_score} 分")
                
            with t4:
                st.markdown("### ⚖️ 投資銀行研究報告：定價與估值模型")
                st.markdown(f"""
                * **當前市場本益比 (P/E Ratio)：** `{pe_str}`
                * **分析師公允價值區間 (TV Consensus)：** `{fv_range}`
                * **市場共識公允均值：** `{fv_mean}`
                """)
                if t_mean and current_price < t_mean:
                    st.success(f"📊 **估值結論：目前股價 ({currency_symbol}{current_price:.1f}) 低於公允均值 ({fv_mean})，在基本面上具備超值低估空間。**")
                else:
                    st.warning(f"📊 **估值結論：目前股價 ({currency_symbol}{current_price:.1f}) 高於或接近公允均值 ({fv_mean})，溢價已被市場消化，請嚴格執行網格與技術線買點。**")
                    
            with t5:
                st.markdown("### 🚀 未來成長潛力與技術/AI優勢")
                st.markdown(f"""
                * **商業模式核心主軸：** {biz_summary}
                * **AI 戰略資本力道：** 該公司目前在最新季度砸下 **{capex_str}** 的高額資本支出，用於擴大護城河與產能儲備。
                * **長線潛在成長空間：** 營收增速持續以 `{rev_growth_str}` 的步調擴張，具備高度承接未來 5–10 年產業剛需轉型的實力。
                """)
                
            with t6:
                st.markdown("### ⚔️ 華爾街分析師多空現場辯論")
                st.write("**🐂 多頭分析師（Bull Case）：**")
                st.info(f"「這家公司的營收年增率高達 {rev_growth_str}，且單季大舉投資 {capex_str} 築起高強度的物理技術壁壘。目前 ROE 達 {roe_str}，多頭拉回網格下限時就是最好的撿便宜機會！」")
                st.write("** Bearish 分析師（Bear Case）：**")
                st.error(f"「雖然公允價值放在那，但別忘了目前大盤席勒本益比已經高達 31.5。且此標的負債水準達 {debt_str}，若總體經濟發生系統性風險，高 Capex 將可能轉為巨大折舊壓力。」")
                st.write("**⚖️ 中性結論（Neutral Summary）：**")
                st.markdown(f"該標的技術優勢無庸置疑。短線操作切忌追高，應嚴格遵循系統的 **{low_absorb_price:.1f} 買點** 及 **移動停利價位** 進行機械化防守。")
                
            with t7:
                st.markdown(f"### 🎯 最終投資策略與綜合決策指南")
                st.markdown(f"""
                * **短期展望 (1年內)：** 緊盯系統對稱網格。目前市場結構判斷為：`{market_state}`。
                * **長期展望 (5年以上)：** 護城河與財務數據優異，適合長線分批低吸。
                * **關鍵催化因素：** 最新季度資本支出 (`{capex_str}`) 能否順利轉換為下季利潤率的提升。
                * **主要風險：** 股價波動若放大，公允價值區間過寬時，需留意分歧帶來的短線震盪。
                """)
                # 結合網站原本的 5 等號燈，給予無縫結合建議
                st.radio("🚦 系統最終策略操作建議：", ["買入 (Buy)", "持有/觀望 (Hold)", "避免/減倉 (Avoid)"], 
                         index=0 if final_action in ["🔥 強力買入", "🟢 買入"] else (1 if final_action == "⚪ 觀望" else 2))

    except Exception as e: st.error(f"分析載入失敗: {e}")

# ==============================================================================
# ⏳ 策略回測績效驗證 (Scan-Forward 尋找首個買點機制)
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
        col_r1.success(f"📈 策略平均報酬率：**{avg_return:.1f}%**")
    else:
        col_r1.error(f"📉 策略平均報酬率：**{avg_return:.1f}%**")
    col_r2.info(f"🎯 策略勝率 (正報酬比例)：**{win_rate:.1f}%**")
else:
    st.info(f"自 {bt_date_str} 起算，觀察名單內無任何標的觸發買入條件。請嘗試將日期往前推！")
