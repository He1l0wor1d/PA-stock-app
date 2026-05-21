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
    if fg_value >= 75:
        fg_status = "🚨 極度貪婪 (Extreme Greed)"
    elif fg_value >= 55:
        fg_status = "🟢 貪婪 (Greed)"
    elif fg_value >= 45:
        fg_status = "⚪ 中性 (Neutral)"
    elif fg_value >= 25:
        fg_status = "🟡 恐懼 (Fear)"
    else:
        fg_status = "❄️ 極度恐懼 (Extreme Fear)"
        
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
        "關鍵數據 / 財經大事項目": [
            "美國 5 月紐約聯儲製造業指數",
            "澳洲聯儲 (RBA) 貨幣政策會議紀要",
            "EIA 每週原油庫存變動數據",
            "聯準會 (Fed) 公布貨幣政策會議紀要",
            "美國 4 月核心 PCE 物價指數 (通膨核心)"
        ],
        "即時進度與數據結論 / 市場預期": [
            "✅ 已公布：實際值 -4.2 (優於預期 -7.5)，製造業築底回溫。",
            "⏳ 今日焦點：市場緊盯對大宗商品與通膨的最新鷹鴿態度。",
            "⏳ 觀察中：原油走勢將直接牽動卡脖子傳統能源的網格邊界。",
            "🔮 重大焦點：將釋放下半年降息終點利率的最新政策密碼。",
            "🔮 重大焦點：預期年增率維持 2.6%，若低於預期將利多科技股。"
        ]
    }
    calendar_df = pd.DataFrame(calendar_data)
    st.dataframe(calendar_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ==============================================================================
# ✨ 第二層：AGI 2027 敘事與 SALP 聰明錢觀測站 (內化版)
# ==============================================================================
st.markdown("### 🧠 AGI 2027 敘事與 SALP (13F) 聰明錢觀測站")
salp_col1, salp_col2 = st.columns([1, 1.8])

with salp_col1:
    st.markdown("##### 🔋 AGI 算力進度與物理瓶頸預警")
    st.metric(label="兆元美元集群 (Trillion-dollar Cluster) 投資進度", value="約 35%", delta="四大 CSP 資本支出持續上修", delta_color="normal")
    st.progress(0.35)
    st.info("💡 **SALP 核心觀點內化**：當前 AI 發展的最大物理限制是「天然氣產量」與「變壓器交付時間」。別與趨勢直線爭論，AI 必須插電，實體電力層將是未來的硬資產。")

with salp_col2:
    st.markdown("##### 🏦 SALP 基金四大敘事層級持倉與對沖追蹤表")
    salp_data = {
        "敘事層級 (Layers)": ["⚡ 電力層 (Power)", "☁️ AI 雲端 (AI Cloud)", "🌐 光通訊 (Photonics)", "🖥️ 運算層 (Compute)"],
        "代表性標的": ["BE, TE, CEG, VST", "CRWV, CORZ, IREN", "GLW, COHR, LITE", "NVDA, SMH, TSM"],
        "SALP 13F 籌碼動向": ["📈 長期做多 (Long)", "📈 持續加倉 (Long)", "🔍 戰略佈局 (Long)", "🛡️ 大量買入賣權 (Put) 避險"],
        "內化決策視角 (Why?)": [
            "AI 的終極瓶頸，實體基礎設施具備最強防禦力與剛需。",
            "GPU 即服務，礦工轉型 HPC 具備立即落地的現金流紅利。",
            "解決資料中心內部龐大數據傳輸延遲的網路剛需。",
            "留意估值擁擠！聰明錢透過買入『名目價值』的賣權來防止 AI 泡沫破裂。"
        ]
    }
    st.dataframe(pd.DataFrame(salp_data), use_container_width=True, hide_index=True)

st.markdown("---")

# ==============================================================================
# 3. 內建核心產業與供應鏈地圖
# ==============================================================================
INITIAL_SECTOR_MAP = {
    # 核心基本觀察
    "2330.TW": "半導體晶圓代工",
    "0050.TW": "市值型大盤",
    "2851.TW": "金融再保險",
    "5607.TW": "航空航運物流",
    
    # 基礎設備
    "NEE": "電網設備基建", "GEV": "電網設備基建", "ETN": "電網設備與基建", "PWR": "電網設備基建",
    "VRT": "機房液冷散熱", "MOD": "機房液冷散熱", "3017.TW": "機房液冷散熱",
    "CEG": "核能天然氣發電", "VST": "核能天然氣發電",
    "ENPH": "綠能與微電網", "SEDG": "綠能與微電網",
    
    # 核心晶片設計與代工
    "SOXX": "AI晶片與設計", "XSD": "AI晶片與設計",
    "NVDA": "AI晶片與設計", "AVGO": "AI晶片與設計", "AMD": "AI晶片與設計",
    "QCOM": "AI晶片與設計", "MRVL": "AI晶片與設計", "TXN": "AI晶片與設計", 
    "ADI": "AI晶片與設計", "ON": "AI晶片與設計", "MPWR": "AI晶片與設計", 
    "NVTS": "AI晶片與設計", "2454.TW": "AI晶片與設計",
    
    # 記憶體與儲存
    "DRAM": "記憶體與儲存", "MU": "記憶體與儲存", "SNDK": "記憶體與儲存", 
    "RMBS": "記憶體與儲存", "SITM": "記憶體與儲存",
    
    # 硬體製程與網通
    "TSM": "晶圓代工製程", "ASML": "晶圓代工製程", "AMAT": "晶圓代工製程", 
    "LRCX": "晶圓代工製程", "FORM": "晶圓代工製程", "INTC": "晶圓代工製程", 
    "SNPS": "晶圓代工製程", "TSEM": "晶圓代工製程", "AXTI": "晶圓代工製程", 
    "SIMO": "晶圓代工製程", "ALAB": "晶圓代工製程", "SMH": "晶圓代工製程",
    "CSCO": "光通訊網通硬體", "ANET": "光通訊網通硬體", "GLW": "光通訊網通硬體",
    "COHR": "光通訊網通硬體", "LITE": "光通訊網通硬體", "AAOI": "光通訊網通硬體", 
    "FN": "光通訊網通硬體", "CIEN": "光通訊網通硬體", "NOK": "光通訊網通硬體", "CBRS": "光通訊網通硬體",
    
    # 軟體平台與科技巨頭
    "QQQ": "AI巨頭與軟體", "MAGS": "AI巨頭與軟體",
    "MSFT": "AI巨頭與軟體", "AAPL": "AI巨頭與軟體", "GOOGL": "AI巨頭與軟體", 
    "AMZN": "AI巨頭與軟體", "META": "AI巨頭與軟體", "PLTR": "AI巨頭與軟體", 
    "NOW": "AI巨頭與軟體", "ORCL": "AI巨頭與軟體", "APP": "AI巨頭與軟體", 
    "NET": "AI巨頭與軟體", "CRWV": "AI巨頭與軟體", "2317.TW": "AI巨頭與軟體", "2382.TW": "AI巨頭與軟體",
    
    # 國防航太
    "ARKX": "航太太空國防", "NASA": "航太太空國防", "LMT": "航太太空國防", 
    "RTX": "航太太空國防", "BA": "航太太空國防", "RDW": "航太太空國防", 
    "RKLB": "航太太空國防", "ASTS": "航太太空國防", "ONDS": "航太太空國防",
    
    # 傳統資源與其餘板塊
    "XOM": "傳統能源礦產", "OXY": "傳統能源礦產", "EQT": "傳統能源礦產",
    "LLY": "生技醫療科技", "TEM": "生技醫療科技", "GRAL": "生技醫療科技", "ILMN": "生技醫療科技",
    "JPM": "金融與資產管理", "GS": "金融與資產管理", "BLK": "金融與資產管理", 
    "BX": "金融與資產管理", "SOFI": "金融與資產管理", "HOOD": "金融與資產管理", "SEI": "金融與資產管理",
    "TSLA": "智能車與新能源", "BYDDF": "智能車與新能源", "MSTR": "數位資產與科技", 
    "BRK-B": "綜合控股投資", "GLD": "綜合控股投資", "SHLD": "綜合控股投資", "NBIS": "綜合控股投資"
}

if "sector_map" not in st.session_state:
    st.session_state.sector_map = INITIAL_SECTOR_MAP.copy()

st.sidebar.header("⚙️ 實時清單與自訂網格")

with st.sidebar.expander("➕ 新增觀察股票", expanded=False):
    add_ticker = st.text_input("輸入代碼 (美股如: NVDA / 台股如: 2317.TW)").strip().upper()
    add_sector = st.selectbox("產業分類", sorted(list(set(st.session_state.sector_map.values()))))
    if st.button("確認新增"):
        if add_ticker:
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

with st.spinner("正在提煉五等核心 ACTION 決策與計算三大模型公允價值..."):
    for ticker in active_tickers:
        try:
            ticker_sector = st.session_state.sector_map.get(ticker, "未分類")
            if selected_sector_filter != "全部顯示" and ticker_sector != selected_sector_filter:
                continue

            is_tw = ".TW" in ticker or ".TWO" in ticker
            currency_symbol = "NT$ " if is_tw else "$ "
            
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date)
            if df.empty or len(df) < 220:
                continue
            
            # 📊 公允價值運算
            info = stock.info if stock.info else {}
            vals = []
            eps = info.get('forwardEps') or info.get('trailingEps')
            hist_pe = info.get('trailingPE') or info.get('forwardPE')
            if eps and hist_pe and eps > 0 and hist_pe > 0:
                vals.append(eps * hist_pe)
                
            growth = info.get('earningsGrowth')
            if eps and growth and eps > 0 and growth > 0:
                vals.append(eps * (growth * 100) * 1.0) 
                
            dps = info.get('dividendRate')
            div_yield = info.get('dividendYield')
            if dps and div_yield and dps > 0 and div_yield > 0:
                vals.append(dps / div_yield)
                
            fair_value_str = "數據不足"
            if vals:
                if len(vals) == 3:
                    vals.sort()
                    median = vals[1]
                    if median > 0:
                        filtered = [v for v in vals if abs(v - median) / median <= 0.5]
                    else:
                        filtered = vals
                    if not filtered: filtered = vals  
                else:
                    filtered = vals
                min_fv = min(filtered)
                max_fv = max(filtered)
                fair_value_str = f"{currency_symbol}{min_fv:.1f}" if min_fv == max_fv else f"{currency_symbol}{min_fv:.1f} ~ {max_fv:.1f}"

            # 指標運算
            high_low = df['High'] - df['Low']
            tr = pd.concat([high_low, (df['High'] - df['Close'].shift(1)).abs(), (df['Low'] - df['Close'].shift(1)).abs()], axis=1).max(axis=1)
            df['ATR'] = tr.rolling(window=atr_period).mean()
            df['MA20'] = df['Close'].rolling(window=21).mean()
            df['MA200'] = df['Close'].rolling(window=200).mean()
            df['MA20_actual'] = df['Close'].rolling(window=20).mean()
            df['STD20'] = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['MA20_actual'] + (2 * df['STD20'])
            
            current_price = float(df.iloc[-1]['Close'])  
            yesterday_close = float(df.iloc[-2]['Close'])      
            ma20_center = float(df.iloc[-1]['MA20_actual'])
            latest_atr = float(df.iloc[-1]['ATR'])
            
            # 移動停利
            highest_20d = float(df['High'].rolling(window=20).max().iloc[-1])
            trailing_stop_price = highest_20d - (2 * latest_atr)
            trailing_stop_str = f"{currency_symbol}{trailing_stop_price:.1f}"

            low_absorb_price = ma20_center - (latest_atr * atr_multiplier)
            high_toss_price = ma20_center + (latest_atr * atr_multiplier)
            
            market_state = "⚪ 觀望"
            final_action = "⚪ 觀望"
            reason_str = "未觸及任何策略臨界點。"
            latest = df.iloc[-1]
            
            if current_price >= latest['MA20'] and latest['MA20'] >= latest['MA200']:
                market_state = "📈 多頭波段 (會漲)"
                if current_price <= low_absorb_price: 
                    final_action = "🔥 強力買入"
                    reason_str = f"跌破 MA20 網格下限 (-{atr_multiplier:.1f}x ATR)，黃金埋伏機會！"
                elif abs(current_price - latest['MA20'])/latest['MA20'] <= 0.02: 
                    final_action = "🟢 買入"
                    reason_str = "拉回到關鍵 MA20 支撐區，符合穩定建倉邏輯。"
                elif current_price >= high_toss_price or current_price >= latest['BB_Upper']: 
                    final_action = "🔴 賣出"
                    reason_str = f"短線噴發過熱，衝破 MA20 網格上限，波段高拋。"
                else:
                    final_action = "⚪ 觀望"
                    reason_str = f"多頭結構健全，低吸位 {currency_symbol}{low_absorb_price:.1f}，未到請安心持股。"
                    
            elif current_price < latest['MA20'] and current_price < latest['MA200']:
                market_state = "📉 空頭結構 (會跌)"
                if yesterday_close >= latest['MA20'] and current_price < latest['MA20']: 
                    final_action = "🚨 強力賣出"
                    reason_str = "剛破 MA20 決策線，趨勢轉空，拒絕接飛刀。"
                elif current_price >= high_toss_price: 
                    final_action = "🔴 賣出"
                    reason_str = f"空頭反彈觸及 MA20 網格上限，逃命高拋點。"
                elif current_price <= low_absorb_price: 
                    final_action = "🟢 買入"
                    reason_str = f"空頭下跌破 MA20 網格下限，極小倉位短線試探。"
                else:
                    final_action = "⚪ 觀望"
                    reason_str = "空頭下跌結構中，堅決保持空倉觀望。"
                    
            else:
                market_state = "↕️ 箱型震盪 (會震盪)"
                if current_price <= low_absorb_price * 1.005 and current_price >= low_absorb_price * 0.995: 
                    final_action = "🔥 強力買入"
                    reason_str = f"精準觸及 MA20 網格下限，網格低吸。"
                elif current_price >= high_toss_price * 0.995 and current_price <= high_toss_price * 1.005: 
                    final_action = "🚨 強力賣出"
                    reason_str = f"精準觸及 MA20 網格上限，網格高拋。"
                else:
                    final_action = "⚪ 觀望"
                    reason_str = f"箱型中樞。低吸點 {currency_symbol}{low_absorb_price:.1f} | 高拋點 {currency_symbol}{high_toss_price:.1f}。"

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
        except Exception:
            pass

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

st.header("🔍 個股動態決策軌道與核心基本面")
selected_stock = st.selectbox("選擇個股查看決策軌道：", sorted(active_tickers))

if selected_stock:
    try:
        stock_detail = yf.Ticker(selected_stock)
        df_detail = stock_detail.history(start=start_date)
        
        if not df_detail.empty and len(df_detail) > 200:
            df_detail['MA20_plot'] = df_detail['Close'].rolling(window=21).mean()
            df_detail['MA200'] = df_detail['Close'].rolling(window=200).mean()
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df_detail.index, open=df_detail['Open'], high=df_detail['High'], low=df_detail['Low'], close=df_detail['Close'], name='K線'))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA20_plot'], name='MA20 趨勢決策線', line=dict(color='orange', width=2.5)))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA200'], name='200MA 長期生命線', line=dict(color='crimson', width=3)))
            
            fig.update_layout(xaxis_rangeslider_visible=False, yaxis_title="價格", height=400, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
            info = stock_detail.info if stock_detail.info else {}
            
            # ==============================================================================
            # ✨ 基本面防空鎖升級：營收年增率、季度 Capex、PE
            # ==============================================================================
            
            # 1. 營收年增率 YoY
            rev_growth = info.get('revenueGrowth')
            rev_growth_str = f"{rev_growth * 100:.1f}%" if rev_growth is not None else "無數據"
                
            # 2. 季度資本支出 Capex (強化防空鎖：先找季報，再找年報，模糊搜尋確保不漏接)
            capex_str = "無數據"
            try:
                cf = stock_detail.quarterly_cashflow
                if cf is None or cf.empty:
                    cf = stock_detail.cashflow  # 降級抓年報
                
                if cf is not None and not cf.empty:
                    matching_keys = [k for k in cf.index if 'Capital Expenditure' in str(k) or 'capital_expenditures' in str(k).lower()]
                    if matching_keys:
                        latest_capex = cf.loc[matching_keys[0]].dropna().iloc[0]
                        if pd.notna(latest_capex) and latest_capex != 0:
                            capex_str = f"{abs(latest_capex) / 1000000:.1f} 百萬"
            except Exception:
                pass
                
            # 3. 當前估值 PE Ratio
            pe_ratio = info.get('trailingPE') or info.get('forwardPE')
            pe_str = f"{pe_ratio:.1f}" if pe_ratio else "無數據"
            
            col_f1, col_f2, col_f3 = st.columns(3)
            col_f1.metric("營收年增率 (YoY)", rev_growth_str)
            col_f2.metric("最新資本支出 (Capex)", capex_str, help="反映企業對 AI、算力集群與基礎設施的投入力道")
            col_f3.metric("當前估值 (PE Ratio)", pe_str)
                
            st.markdown("---")
            # ==============================================================================
            # ✨ 新聞防空鎖升級
            # ==============================================================================
            try:
                news_list = stock_detail.news
                if news_list and isinstance(news_list, list) and len(news_list) > 0:
                    st.subheader("📰 最新市場消息")
                    for article in news_list[:3]:
                        title = article.get('title', '無標題')
                        link = article.get('link', '#')
                        publisher = article.get('publisher', '未知')
                        st.markdown(f"**[{title}]({link})** (來源: {publisher})")
                else:
                    st.info("暫無最新消息")
            except Exception: 
                st.info("新聞抓取受限")
                
    except Exception as e:
        st.error(f"分析載入失敗: {e}")

# ==============================================================================
# ⏳ 策略回測績效驗證 (實時動態 Demo)
# ==============================================================================
st.markdown("---")
st.header("⏳ 策略回測績效驗證 (實時動態 Demo)")
st.markdown("透過時光機回到過去任意一天，檢驗若當下依照系統**「🔥 強力買入 / 🟢 買入」**燈號建倉，持有至今的真實報酬率。")

backtest_col, _ = st.columns([1, 3])
with backtest_col:
    # 預設為一個月前
    default_date = datetime.now().date() - timedelta(days=30)
    backtest_date = st.date_input("📅 選擇模擬建倉日期：", value=default_date)

bt_date_str = backtest_date.strftime('%Y-%m-%d')
backtest_results = []

with st.spinner("正在回溯歷史訊號與計算當前回報率..."):
    for ticker in active_tickers:
        try:
            # 多抓一點歷史資料確保均線與 ATR 能計算
            df_bt = yf.Ticker(ticker).history(start=(backtest_date - timedelta(days=300)).strftime('%Y-%m-%d'))
            if df_bt.empty: continue
            
            # 切片出回測日(含)之前的數據
            df_past = df_bt.loc[:bt_date_str]
            if len(df_past) < 25: continue
            
            # 計算回測當下的指標
            hl = df_past['High'] - df_past['Low']
            h_pc = (df_past['High'] - df_past['Close'].shift(1)).abs()
            l_pc = (df_past['Low'] - df_past['Close'].shift(1)).abs()
            tr = pd.concat([hl, h_pc, l_pc], axis=1).max(axis=1)
            past_atr = tr.rolling(window=atr_period).mean().iloc[-1]
            
            past_ma20 = df_past['Close'].rolling(window=20).mean().iloc[-1]
            past_ma200 = df_past['Close'].rolling(window=200).mean().iloc[-1] if len(df_past) >= 200 else past_ma20
            
            past_close = df_past['Close'].iloc[-1]
            low_b = past_ma20 - (past_atr * atr_multiplier)
            
            # 重現回測當日的判斷邏輯
            if past_close >= past_ma20 and past_ma20 >= past_ma200: 
                # 給予 2% 容錯，或是跌破網格下限
                if past_close <= low_b * 1.02: 
                    signal = "🔥 強力買入" if past_close <= low_b else "🟢 買入"
                    
                    # 取得目前最新價格來計算報酬
                    latest_price = df_bt['Close'].iloc[-1]
                    return_pct = ((latest_price - past_close) / past_close) * 100
                    
                    currency = "NT$ " if ".TW" in ticker else "$ "
                    backtest_results.append({
                        "代碼": ticker,
                        "建倉日期": df_past.index[-1].strftime('%Y-%m-%d'),
                        "當時訊號": signal,
                        "買入價": f"{currency}{past_close:.1f}",
                        "最新價": f"{currency}{latest_price:.1f}",
                        "累積報酬率": f"{return_pct:.1f}%"
                    })
        except Exception:
            pass

if backtest_results:
    df_bt_results = pd.DataFrame(backtest_results)
    # 將報酬率轉回數字排序
    df_bt_results['sort_val'] = df_bt_results['累積報酬率'].str.replace('%', '').astype(float)
    df_bt_results = df_bt_results.sort_values(by='sort_val', ascending=False).drop('sort_val', axis=1)
    
    st.dataframe(df_bt_results, use_container_width=True, hide_index=True)
    avg_return = df_bt_results['累積報酬率'].str.replace('%', '').astype(float).mean()
    
    if avg_return > 0:
        st.success(f"📈 假設於 {bt_date_str} 依照系統燈號無腦買入，至今平均報酬率為：**{avg_return:.1f}%**")
    else:
        st.warning(f"📉 假設於 {bt_date_str} 依照系統燈號無腦買入，至今平均報酬率為：**{avg_return:.1f}%**")
else:
    st.info(f"在 {bt_date_str} 當天，觀察名單內並無任何標的觸發買入燈號。這代表當時沒有跌到甜點位，請嘗試選擇其他日期！")
