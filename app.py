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
            "✅ 已公布：實際值 -4.2 (優於預期 -7.5)，製造業築底回溫。",
            "⏳ 今日焦點：市場緊盯對大宗商品與通膨的最新鷹鴿態度。",
            "⏳ 觀察中：原油走勢將直接牽動卡脖子傳統能源的網格邊界。",
            "🔮 重大焦點：將釋放 2026 下半年降息終點利率的最新政策密碼。",
            "🔮 重大焦點：預期年增率維持 2.6%，若低於預期將利多科技股。"
        ]
    }
    st.dataframe(pd.DataFrame(calendar_data), use_container_width=True, hide_index=True)

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
# 3. 內建核心產業與「卡脖子」供應鏈地圖 (核心標的已置頂)
# ==============================================================================
INITIAL_SECTOR_MAP = {
    # 🌟 置頂核心觀察標的
    "2330.TW": "🇹🇼 台股 - 半導體晶圓代工 (全球核心)",
    "2851.TW": "🇹🇼 台股 - 金融再保險",
    "5607.TW": "🇹🇼 台股 - 航空航運與物流",
    "0050.TW": "🇹🇼 台股 - 市值型 ETF (元大台灣50)",
    
    # ⚡ 電網設備與基建
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

st.sidebar.header("📊 對稱網格參數設定")
atr_period = st.sidebar.slider("ATR 計算天數", 5, 22, 14)
atr_multiplier = st.sidebar.slider("自訂網格 ATR 倍數 (x)", 0.5, 2.5, 1.4, 0.1, help="將以 MA20 為中心對稱向外擴展 x * ATR")

start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

summary_data = []
action_alerts = []

action_rank = {"🔥 強力買入": 0, "🟢 買入": 1, "⚪ 觀望": 2, "🔴 賣出": 3, "🚨 強力賣出": 4}

with st.spinner("正在提煉五等核心 ACTION 決策與計算三大模型公允價值..."):
    for ticker in active_tickers:
        try:
            is_tw = ".TW" in ticker or ".TWO" in ticker
            currency_symbol = "NT$ " if is_tw else "$ "
            
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date)
            if df.empty or len(df) < 220:
                continue
            
            # ==========================================
            # ✨ 新增模組：公允價值運算 (三模型綜合評估)
            # ==========================================
            info = stock.info
            vals = []
            
            eps = info.get('forwardEps') or info.get('trailingEps')
            
            # 1. 本益比估價法
            hist_pe = info.get('trailingPE') or info.get('forwardPE')
            if eps and hist_pe and eps > 0 and hist_pe > 0:
                vals.append(eps * hist_pe)
                
            # 2. PEG 成長法
            growth = info.get('earningsGrowth')
            if eps and growth and eps > 0 and growth > 0:
                growth_rate = growth * 100  # 轉換小數點為整數%計算
                vals.append(eps * growth_rate * 1.0) # Target PEG = 1
                
            # 3. 股息折現法
            dps = info.get('dividendRate')
            div_yield = info.get('dividendYield')
            if dps and div_yield and dps > 0 and div_yield > 0:
                vals.append(dps / div_yield)
                
            fair_value_str = "數據不足"
            if vals:
                # 剔除超過 50% 偏差的極端值
                if len(vals) == 3:
                    vals.sort()
                    median = vals[1]
                    if median > 0:
                        filtered = [v for v in vals if abs(v - median) / median <= 0.5]
                    else:
                        filtered = vals
                    if not filtered: filtered = vals  # 若全數發散，則不予剔除
                else:
                    filtered = vals
                    
                min_fv = min(filtered)
                max_fv = max(filtered)
                
                if min_fv == max_fv:
                    fair_value_str = f"{currency_symbol}{min_fv:.2f}"
                else:
                    fair_value_str = f"{currency_symbol}{min_fv:.2f} ~ {max_fv:.2f}"

            # 幕後運算技術指標
            high_low = df['High'] - df['Low']
            high_cp = (df['High'] - df['Close'].shift(1)).abs()
            low_cp = (df['Low'] - df['Close'].shift(1)).abs()
            tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
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
            
            # 網格計算
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
                    reason_str = f"多頭強勢股拉回過深，跌破 MA20 對稱網格下限 (-{atr_multiplier}x ATR)，黃金埋伏機會！"
                elif abs(current_price - latest['MA20'])/latest['MA20'] <= 0.02:
                    final_action = "🟢 買入"
                    reason_str = "多頭波段拉回到關鍵 MA20 決策線重要支撐區，符合穩定建倉邏輯。"
                elif current_price >= high_toss_price or current_price >= latest['BB_Upper']:
                    final_action = "🔴 賣出"
                    reason_str = f"短線噴發過熱，已衝破 MA20 對稱網格上限 (+{atr_multiplier}x ATR)，波段高拋。"
                else:
                    final_action = "⚪ 觀望"
                    reason_str = f"多頭結構健全，已為您計算最新 MA20 低吸位 {currency_symbol}{low_absorb_price:.2f}，未到請安心持股。"
                    
            elif current_price < latest['MA20'] and current_price < latest['MA200']:
                market_state = "📉 空頭結構 (會跌)"
                if yesterday_close >= latest['MA20'] and current_price < latest['MA20']:
                    final_action = "🚨 強力賣出"
                    reason_str = "剛破 MA20 決策線，趨勢轉空，請果斷執行防守離場紀律，拒絕接飛刀。"
                elif current_price >= high_toss_price:
                    final_action = "🔴 賣出"
                    reason_str = f"空頭弱勢反彈觸及 MA20 對稱網格上限 (+{atr_multiplier}x ATR)，屬於紀律性逃命高拋點。"
                elif current_price <= low_absorb_price:
                    final_action = "🟢 買入"
                    reason_str = f"空頭結構下跌破 MA20 網格下限 (-{atr_multiplier}x ATR)，限極小倉位短線試探反彈。"
                else:
                    final_action = "⚪ 觀望"
                    reason_str = "空頭下跌結構中，屬於『不碰族群』，堅決保持空倉觀望。"
                    
            else:
                market_state = "↕️ 箱型震盪 (會震盪)"
                if current_price <= low_absorb_price * 1.005 and current_price >= low_absorb_price * 0.995:
                    final_action = "🔥 強力買入"
                    reason_str = f"精準觸及 MA20 對稱網格下限 (-{atr_multiplier}x ATR)，網格低吸買入。"
                elif current_price >= high_toss_price * 0.995 and current_price <= high_toss_price * 1.005:
                    final_action = "🚨 強力賣出"
                    reason_str = f"精準觸及 MA20 對稱網格上限 (+{atr_multiplier}x ATR)，網格高拋賣出。"
                else:
                    final_action = "⚪ 觀望"
                    reason_str = f"處於箱型震盪中樞。最新 MA20 對稱網格：低吸買點 {currency_symbol}{low_absorb_price:.2f} | 高拋賣點 {currency_symbol}{high_toss_price:.2f}。"

            if final_action != "⚪ 觀望":
                action_alerts.append({
                    "代碼": ticker,
                    "綜合建議": final_action,
                    "市場狀態": market_state,
                    "當前股價": f"{currency_symbol}{current_price:.2f}",
                    "公允價值區間": fair_value_str, # 新增公允價值欄位
                    "昨日收盤價": f"{currency_symbol}{yesterday_close:.2f}",
                    "MA20": f"{currency_symbol}{ma20_center:.2f}",
                    "精簡決策原因": reason_str
                })

            summary_data.append({
                "產業領域": st.session_state.sector_map.get(ticker, "未分類"),
                "代碼": ticker,
                "當前股價": f"{currency_symbol}{current_price:.2f}",
                "公允價值區間": fair_value_str, # 新增公允價值欄位
                "昨收盤價": f"{currency_symbol}{yesterday_close:.2f}",
                "MA20": f"{currency_symbol}{ma20_center:.2f}",
                "市場狀態": market_state,
                "綜合建議": final_action,
                "買點": f"{currency_symbol}{low_absorb_price:.2f}",
                "賣點": f"{currency_symbol}{high_toss_price:.2f}",
                "精簡決策原因": reason_str
            })
        except Exception:
            pass

# --- 介面排版輸出 ---
st.header("🚨 今日核心執行 ACTION 面板")
if action_alerts:
    alert_df = pd.DataFrame(action_alerts)
    alert_df['sort'] = alert_df['綜合建議'].map(action_rank)
    alert_df = alert_df.sort_values('sort').drop('sort', axis=1)
    st.dataframe(alert_df, use_container_width=True, hide_index=True)
else:
    st.info("🧘 報告隊長：今日名單中皆無個股觸發臨界點。請繼續安心保持觀望。")

st.markdown("---")

st.header("📊 降維極簡大看板 (標準五等紅綠燈)")
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
            
            info = stock_detail.info
            if info:
                col_f1, col_f2, col_f3 = st.columns(3)
                net_margin = info.get('netIncomeToCommon', 0) / info.get('totalRevenue', 1) if info.get('netIncomeToCommon') else 0
                current_ratio = info.get('currentRatio', 0)
                pe_ratio = info.get('trailingPE', "無資料")
                
                col_f1.metric("公司淨利率", f"{net_margin * 100:.2f}%")
                col_f2.metric("流動比率", f"{current_ratio:.2f}", "✅ 安全 (>1.5)" if current_ratio > 1.5 else "⚠️ 偏低")
                col_f3.metric("當前 PE 估值", f"{pe_ratio}")
                
            st.markdown("---")
            try:
                news_list = stock_detail.news
                if news_list:
                    st.subheader("📰 影響股價的最新市場消息")
                    for article in news_list[:3]:
                        st.markdown(f"**[{article.get('title', '無標題')}]({article.get('link', '#')})** (來源: {article.get('publisher', '未知')})")
            except Exception: pass
    except Exception as e:
        st.error(f"分析載入失敗: {e}")
