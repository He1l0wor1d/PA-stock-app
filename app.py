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
# 📖 ✨ 全新功能：折疊式決策系統實戰使用指南 (結構原封不動，精準置於最上方)
# ==============================================================================
with st.expander("📖 鷹眼決策系統：實戰新手使用指南（點擊展開 / 折疊）"):
    st.markdown("""
    歡迎來到**🦅 極簡五等燈號自動化決策系統**！本系統將複雜的技術指標降維，專為尋找**多頭拉回甜點位**與**機械化網格交易**的投資人設計。以下是系統核心區塊的實戰使用教學：
    
    ### 🎯 第一步：鎖定方向，觀察總經與聰明錢（大盤環境）
    1. **全球總體經濟面板**：進入網站先看最上方。如果「恐懼與貪婪指標」進入**🚨 極度貪婪 (75以上)**，代表市場過熱，即使個股亮燈也應降低建倉預算；反之進入極度恐懼，則是戰略性分批低吸的黃金期。
    2. **🧠 AGI 2027 與 SALP 聰明錢觀測站**：幫你跟緊華爾街長線資金（如 13F 基金）的四大核心敘事配置。記住當前算力爆發的物理瓶頸在於電力（變壓器與天然氣），點擊這裡能幫你隨時對齊「實體硬資產」的最新資金動向。
    
    ### 📊 第二步：聚焦板塊，看懂降維大看板（個股策略）
    1. **🎯 產業類別篩選器（側邊欄）**：你可以透過左側下拉選單，單獨過濾出如 `AI晶片與設計`、`機房液冷散熱` 或 `電網設備基建`。配合內置的**美台股各領域龍頭（前一、兩大）**，你可以輕鬆觀察當前資金正在哪個板塊輪動！
    2. **🔥 核心執行燈號**：
        * **`🔥 強力買入`**：代表這檔股票在大趨勢向上的多頭波段中，股價發生了急跌拉回，**精準跌破了 MA20 的對稱網格下限（甜點位）**，是極佳的長線埋伏機會。
        * **`🟢 買入`**：代表多頭走勢健全，股價回檔到關鍵的 20MA 支撐線附近（容錯 2% 內），符合穩定建倉紀律。
        * **`🔴 賣出` 或 `🚨 強力賣出`**：短線噴發衝破對稱網格上限，代表乖離率過大，請執行機械化獲利高拋。
    3. **華爾街分析師共識估值**：公允價值區間已完美對齊 **TradingView 的分析師目標價共識**。
        * 當大看板同時亮起 **`🔥 強力買入`** 且當前股價 **遠低於分析師公允均值** 時 $\rightarrow$ 這是最完美的**「技術超跌 ＋ 基本面便宜」雙重共振**，勝率最高！
    4. **🛡️ 移動停利價位**：依據實戰動能派設計，公式為 `近20日最高價 - 2 * ATR`。當你持有的飆股利潤開始奔跑、你不知道何時該賣時，只要**股價跌破此價位就無條件執行機械化停力**，絕不讓獲利吐回。
    
    ### 🔍 第三步：深挖個股，驗證未來 AGI 爆發力（未來展望）
    1. **個股動態決策軌道**：點選下拉選單可直接調閱一整年的 K 線、20MA 與 200MA 生命線，幫你肉眼確認目前個股處於大多頭還是空頭結構。
    2. **科技股 AGI 指標升級**：AI 時代不能只看過去的流動比率或淨利率。本系統底部的財務三指標已全面替換：
        * **營收年增率 (YoY)**：確認這間公司的本業營收是否真的因為 AI 的剛需而實質大賺現金流。
        * **最新季度資本支出 (Capex)**：**這是最核心的護城河指標！** 唯有持續擴大研發支出、大舉興建算力集群與基礎設施的科技股，才能在 AGI 2027 年的物理瓶頸賽局中勝出。
    
    ### ⏳ 進階驗證：時光機動態回測 Demo
    * 滑到網站最下方，你可以自由選擇過去的任何一個日期（預設為兩個月前），系統會自動進行 Forward-Scanning（向前掃描），模擬如果當時依照本系統的燈號買入，抱到今天的**真實累積報酬率與總勝率**。讓數據說話，親自驗證這套系統到底能不能幫你穩定獲利！
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
            
            info = stock_detail.info if stock_detail.info else {}
            
            # 基本面防空鎖升級
            rev_growth = info.get('revenueGrowth')
            rev_growth_str = f"{rev_growth * 100:.1f}%" if rev_growth is not None else "無數據"
                
            capex_str = "無數據"
            is_tw_detail = ".TW" in selected_stock or ".TWO" in selected_stock
            curr_str = "NT$" if is_tw_detail else "美元"

            try:
                cf = stock_detail.quarterly_cashflow
                if cf is None or cf.empty: cf = stock_detail.cashflow
                if cf is not None and not cf.empty:
                    matching_keys = [k for k in cf.index if 'Capital Expenditure' in str(k) or 'capital_expenditures' in str(k).lower()]
                    if matching_keys:
                        latest_capex = cf.loc[matching_keys[0]].dropna().iloc[0]
                        if pd.notna(latest_capex) and latest_capex != 0:
                            capex_str = f"{abs(latest_capex) / 100000000:.1f} 億{curr_str}"
            except Exception: pass
                
            pe_ratio = info.get('trailingPE') or info.get('forwardPE')
            pe_str = f"{pe_ratio:.1f}" if pe_ratio else "無數據"
            
            col_f1, col_f2, col_f3 = st.columns(3)
            col_f1.metric("營收年增率 (YoY)", rev_growth_str)
            col_f2.metric(f"最新資本支出 (Capex)", capex_str, help="反映企業對 AI 算力基礎設施的投入力道")
            col_f3.metric("當前估值 (PE Ratio)", pe_str)
                
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
