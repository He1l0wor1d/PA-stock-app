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
# 3. 內建核心產業與「卡脖子」供應鏈地圖 (✨ 融入 ETF、新增 XSD/FORM、加入龍頭股)
# ==============================================================================
INITIAL_SECTOR_MAP = {
    # 🌟 置頂核心與台股大盤觀察標的
    "2330.TW": "台股 - 半導體晶圓代工 (全球核心)",
    "0050.TW": "**【市值型 ETF】** 台股 - 市值型 ETF (元大台灣50)",
    "2851.TW": "台股 - 金融再保險",
    "5607.TW": "台股 - 航空航運與物流",
    
    # ⚡ 電網設備與基建 (已加入公用事業龍頭 NEE)
    "NEE": "電網設備與基建", "GEV": "電網設備與基建", "ETN": "電網設備與基建", "PWR": "電網設備與基建",
    # ❄️ 機房液冷與散熱 (已加入台股散熱龍頭 3017)
    "VRT": "機房液冷與散熱", "MOD": "機房液冷與散熱", "3017.TW": "機房液冷與散熱",
    # ☢️ 獨立核能/天然氣發電
    "CEG": "獨立核能與天然氣發電", "VST": "獨立核能與天然氣發電",
    # ☀️ 綠能逆變器與微電網
    "ENPH": "綠能逆變器與微電網", "SEDG": "綠能逆變器與微電網",
    
    # AI 晶片與半導體設計 (✨ 已混入半導體 ETF：SOXX、XSD)
    "SOXX": "**【半導體 ETF】** AI 晶片與半導體設計", 
    "XSD": "**【半導體等權重 ETF】** AI 晶片與半導體設計",
    "NVDA": "AI 晶片與半導體設計", "AVGO": "AI 晶片與半導體設計", "AMD": "AI 晶片與半導體設計",
    "QCOM": "AI 晶片與半導體設計", "MRVL": "AI 晶片與半導體設計", "TXN": "AI 晶片與半導體設計", 
    "ADI": "AI 晶片與半導體設計", "ON": "AI 晶片與半導體設計", "MPWR": "AI 晶片與半導體設計", 
    "NVTS": "AI 晶片與半導體設計", "2454.TW": "AI 晶片與半導體設計 (台股手機/AI晶片龍頭)",
    
    # 記憶體與儲存 (✨ 已混入儲存型 ETF：DRAM、NASA)
    "DRAM": "**【記憶體 ETF】** 記憶體與儲存",
    "MU": "記憶體與儲存", "SNDK": "記憶體與儲存", "RMBS": "記憶體與儲存", "SITM": "記憶體與儲存",
    
    # 光通訊與網通硬體 (已加入網通龍頭 CSCO)
    "CSCO": "光通訊與網通硬體", "ANET": "光通訊與網通硬體", "GLW": "光通訊與網通硬體",
    "COHR": "光通訊與網通硬體", "LITE": "光通訊與網通硬體", "AAOI": "光通訊與網通硬體", 
    "FN": "光通訊與網通硬體", "CIEN": "光通訊與網通硬體", "NOK": "光通訊與網通硬體", "CBRS": "光通訊與網通硬體",
    
    # 晶圓代工與設備製程 (✨ 已混入晶圓設備 ETF：SMH；新增 FORM，加入設備龍頭 AMAT、LRCX)
    "SMH": "**【高效能晶片 ETF】** 晶圓代工與設備製程",
    "TSM": "晶圓代工與設備製程", "ASML": "晶圓代工與設備製程", "AMAT": "晶圓代工與設備製程", 
    "LRCX": "晶圓代工與設備製程", "FORM": "晶圓代工與設備製程 (新增測試探針卡龍合)", 
    "INTC": "晶圓代工與設備製程", "SNPS": "晶圓代工與設備製程", "TSEM": "晶圓代工與設備製程", 
    "AXTI": "晶圓代工與設備製程", "SIMO": "晶圓代工與設備製程", "ALAB": "晶圓代工與設備製程",
    
    # AI 巨頭與軟體平台 (✨ 已混入科技大盤 ETF：QQQ、MAGS；加入台股硬體組裝巨頭 2317、2382)
    "QQQ": "**【納斯達克大盤 ETF】** AI 巨頭與軟體平台", 
    "MAGS": "**【科技七巨頭 ETF】** AI 巨頭與軟體平台",
    "MSFT": "AI 巨頭與軟體平台", "AAPL": "AI 巨頭與軟體平台", "NVDA": "AI 巨頭與軟體平台", 
    "GOOGL": "AI 巨頭與軟體平台", "AMZN": "AI 巨頭與軟體平台", "META": "AI 巨頭與軟體平台",
    "PLTR": "AI 巨頭與軟體平台", "NOW": "AI 巨頭與軟體平台", "ORCL": "AI 巨頭與軟體平台", 
    "APP": "AI 巨頭與軟體平台", "NET": "AI 巨頭與軟體平台", "CRWV": "AI 巨頭與軟體平台",
    "2317.TW": "AI 巨頭與軟體平台 (台股伺服器組裝龍頭)", 
    "2382.TW": "AI 巨頭與軟體平台 (台股 AI 伺服器核心)",
    
    # 航太、太空與國防 (✨ 已混入航太太空 ETF：ARKX、NASA)
    "ARKX": "**【太空探索 ETF】** 航太、太空與國防", 
    "NASA": "**【純航太衛星 ETF】** 航太、太空與國防",
    "LMT": "航太、太空與國防", "RTX": "航太、太空與國防", "BA": "航太、太空與國防",
    "RDW": "航太、太空與國防", "RKLB": "航太、太空與國防", "ASTS": "航太、太空與國防", "ONDS": "航太、太空與國防",
    
    # 傳統能源與礦產 (已加入傳統石油老大哥 XOM)
    "XOM": "傳統能源與礦產", "OXY": "傳統能源與礦產", "EQT": "傳統能源與礦產",
    # 生技與醫療科技 (已加入生技市值龍頭 LLY)
    "LLY": "生技與醫療科技", "TEM": "生技與醫療科技", "GRAL": "生技與醫療科技", "ILMN": "生技與醫療科技",
    # 金融科技與資產管理 (已加入金融權值龍頭 JPM)
    "JPM": "金融科技與資產管理", "GS": "金融科技與資產管理", "BLK": "金融科技與資產管理", 
    "BX": "金融科技與資產管理", "SOFI": "金融科技與資產管理", "HOOD": "金融科技與資產管理", "SEI": "金融科技與資產管理",
    
    # 智能車與新能源 / 其他貴金屬
    "TSLA": "智能車與新能源", "BYDDF": "智能車與新能源", "MSTR": "比特幣與微策略科技", 
    "BRK-B": "價值投資綜合控股", "GLD": "**【黃金資產 ETF】** 其他綜合與特殊題材",
    "SHLD": "其他綜合與特殊題材", "NBIS": "其他綜合與特殊題材"
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
atr_multiplier = st.sidebar.slider("自訂網格 ATR 倍數 (x)", 0.5, 2.5, 1.4, 0.1)

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
            
            # 📊 公允價值運算
            info = stock.info
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
            latest = df.iloc[-1]
            
            if current_price >= latest['MA20'] and latest['MA20'] >= latest['MA200']:
                market_state = "📈 多頭波段 (會漲)"
                if current_price <= low_absorb_price: final_action = "🔥 強力買入"
                elif abs(current_price - latest['MA20'])/latest['MA20'] <= 0.02: final_action = "🟢 買入"
                elif current_price >= high_toss_price or current_price >= latest['BB_Upper']: final_action = "🔴 賣出"
                    
            elif current_price < latest['MA20'] and current_price < latest['MA200']:
                market_state = "📉 空頭結構 (會跌)"
                if yesterday_close >= latest['MA20'] and current_price < latest['MA20']: final_action = "🚨 強力賣出"
                elif current_price >= high_toss_price: final_action = "🔴 賣出"
                elif current_price <= low_absorb_price: final_action = "🟢 買入"
                    
            else:
                market_state = "↕️ 箱型震盪 (會震盪)"
                if current_price <= low_absorb_price * 1.005 and current_price >= low_absorb_price * 0.995: final_action = "🔥 強力買入"
                elif current_price >= high_toss_price * 0.995 and current_price <= high_toss_price * 1.005: final_action = "🚨 強力賣出"

            if final_action != "⚪ 觀望":
                action_alerts.append({
                    "代碼": ticker, "綜合建議": final_action, "市場狀態": market_state, "當前股價": f"{currency_symbol}{current_price:.1f}",
                    "公允價值區間": fair_value_str, "移動停利價位": trailing_stop_str, "昨日收盤價": f"{currency_symbol}{yesterday_close:.1f}", "MA20": f"{currency_symbol}{ma20_center:.1f}"
                })

            summary_data.append({
                "產業領域": st.session_state.sector_map.get(ticker, "未分類"), "代碼": ticker, "當前股價": f"{currency_symbol}{current_price:.1f}",
                "公允價值區間": fair_value_str, "移動停利價位": trailing_stop_str, "昨收盤價": f"{currency_symbol}{yesterday_close:.1f}",
                "MA20": f"{currency_symbol}{ma20_center:.1f}", "市場狀態": market_state, "綜合建議": final_action,
                "買點": f"{currency_symbol}{low_absorb_price:.1f}", "賣點": f"{currency_symbol}{high_toss_price:.1f}"
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
            st.plotly_chart(fig, use_container_width=True)
            
            info = stock_detail.info if stock_detail.info else {}
            
            # AGI 核心基本面指標 (營收年增率、季度 Capex、PE)
            rev_growth = info.get('revenueGrowth')
            rev_growth_str = f"{rev_growth * 100:.1f}%" if rev_growth is not None else "無資料"
                
            try:
                quarterly_cashflow = stock_detail.quarterly_cashflow
                if not quarterly_cashflow.empty and 'Capital Expenditures' in quarterly_cashflow.index:
                    latest_capex = quarterly_cashflow.loc['Capital Expenditures'].iloc[0]
                    capex_str = f"{latest_capex / 1000000:.1f} 百萬"
                else: capex_str = "無季度數據"
            except Exception: capex_str = "數據抓取受限"
                
            pe_ratio = info.get('trailingPE') or info.get('forwardPE')
            pe_str = f"{pe_ratio:.1f}" if pe_ratio else "無資料"
            
            col_f1, col_f2, col_f3 = st.columns(3)
            col_f1.metric("營收年增率 (YoY)", rev_growth_str)
            col_f2.metric("最新季度資本支出 (Capex)", capex_str, help="企業對 AI 算力基礎設施的投入力道")
            col_f3.metric("當前估值 (PE Ratio)", pe_str)
                
            st.markdown("---")
            try:
                news_list = stock_detail.news
                if news_list:
                    st.subheader("📰 最新市場消息")
                    for article in news_list[:3]:
                        st.markdown(f"**[{article.get('title', '無標題')}]({article.get('link', '#')})** (來源: {article.get('publisher', '未知')})")
            except Exception: pass
    except Exception as e:
        st.error(f"分析載入失敗: {e}")
