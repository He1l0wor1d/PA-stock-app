import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# 1. 網頁基本設定
st.set_page_config(layout="wide", page_title="Henry & 雙軌降維五等決策系統")
st.title("🦅 美股+台股『極簡五等燈號』自動化決策系統")
st.markdown("本系統已將繁雜指標降維，將多空結構簡化為**三大狀態**，並嚴格限制為 **五個標準 Action 等級**。")

# 2. 內建核心產業與「卡脖子」供應鏈地圖 (台美股綜合)
INITIAL_SECTOR_MAP = {
    "2330.TW": "🇹🇼 台股 - 半導體晶圓代工 (全球核心)", "2851.TW": "🇹🇼 台股 - 金融再保險",
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

# 實時增減股票
with st.sidebar.expander("➕ 新增觀察股票", expanded=False):
    add_ticker = st.text_input("輸入代碼 (美股如: NVDA / 台股如: 2317.TW)").strip().upper()
    add_sector = st.selectbox("產業分類", sorted(list(set(st.session_state.sector_map.values()))))
    if st.button("確認新增"):
        if add_ticker:
            st.session_state.sector_map[add_ticker] = add_sector
            st.rerun()

all_current_tickers = sorted(list(st.session_state.sector_map.keys()))
active_tickers = st.sidebar.multiselect("💡 觀察名單管理 (點 X 刪除)", options=all_current_tickers, default=all_current_tickers)

# ATR 自訂網格參數
st.sidebar.header("📊 ATR 網格參數 (自訂高拋低吸)")
atr_period = st.sidebar.slider("ATR 計算天數", 5, 22, 14)
entry_multiplier = st.sidebar.slider("低吸買進 ATR 倍數", 0.5, 3.5, 1.5, 0.1)
exit_multiplier = st.sidebar.slider("高拋賣出 ATR 倍數", 0.5, 3.5, 1.5, 0.1)

start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

summary_data = []
action_alerts = []

# 五等標準排序映射 (讓強烈買進排最前，強烈賣出排最後，中間夾觀望)
action_rank = {"🔥 強力買入": 0, "🟢 買入": 1, "⚪ 觀望": 2, "🔴 賣出": 3, "🚨 強力賣出": 4}

with st.spinner("正在提煉五等核心 ACTION 決策中..."):
    for ticker in active_tickers:
        try:
            is_tw = ".TW" in ticker or ".TWO" in ticker
            currency_symbol = "NT$ " if is_tw else "$ "
            
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date)
            if df.empty or len(df) < 220:
                continue
                
            # 幕後運算核心指標
            high_low = df['High'] - df['Low']
            high_cp = (df['High'] - df['Close'].shift(1)).abs()
            low_cp = (df['Low'] - df['Close'].shift(1)).abs()
            tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
            df['ATR'] = tr.rolling(window=atr_period).mean()
            
            df['MA21'] = df['Close'].rolling(window=21).mean()
            df['MA200'] = df['Close'].rolling(window=200).mean()
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['STD20'] = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['MA20'] + (2 * df['STD20'])
            df['BB_Lower'] = df['MA20'] - (2 * df['STD20'])
            
            delta = df['Close'].diff()
            gain = (delta.clip(lower=0)).rolling(window=14).mean()
            loss = (-delta.clip(upper=0)).rolling(window=14).mean()
            rs = gain / loss.replace(0, 0.00001)
            df['RSI_14'] = 100 - (100 / (1 + rs))

            latest = df.iloc[-1]
            prev = df.iloc[-2]
            current_price = float(latest['Close'])
            prev_close = float(prev['Close'])
            prev_atr = float(prev['ATR'])
            
            # 網格定價
            low_absorb_price = prev_close - (prev_atr * entry_multiplier)
            high_toss_price = prev_close + (prev_atr * exit_multiplier)
            
            # 默認初始狀態
            market_state = "⚪ 觀望"
            final_action = "⚪ 觀望"
            reason_str = "未觸及任何策略臨界點。"

            # ==========================================
            # 🧠 核心降維邏輯：對齊五等決策紅綠燈
            # ==========================================
            
            # 軌道一：趨勢會漲 (Price 在 21MA 與 200MA 生命線之上)
            if current_price >= latest['MA21'] and latest['MA21'] >= latest['MA200']:
                market_state = "📈 多頭波段 (會漲)"
                if current_price <= low_absorb_price:
                    final_action = "🔥 強力買入"
                    reason_str = "多頭趨勢股極致拉回到網格低吸上限以下，屬於勝率極高的『低點埋伏點』。"
                elif abs(current_price - latest['MA21'])/latest['MA21'] <= 0.02:
                    final_action = "🟢 買入"
                    reason_str = "多頭波段回檔至 21MA 決策線重要支撐區，符合『右側低點埋伏』。"
                elif current_price >= latest['BB_Upper']:
                    final_action = "🔴 賣出"
                    reason_str = "短線多頭噴發嚴重超買、觸及布林上軌，波段『高拋』鎖定利潤。"
                else:
                    final_action = "⚪ 觀望"
                    reason_str = "多頭結構健全穩定，未達極佳埋伏位，持股者請安心抱牢。"
                    
            # 軌道二：趨勢會跌 (Price 跌破生命線與決策線)
            elif current_price < latest['MA21'] and current_price < latest['MA200']:
                market_state = "📉 空頭結構 (會跌)"
                if prev_close >= latest['MA21'] and current_price < latest['MA21']:
                    final_action = "🚨 強力賣出"
                    reason_str = "今日正式跌破 21MA 決策線，多轉空結構確立，請果斷離場、拒絕接飛刀。"
                elif current_price >= high_toss_price:
                    final_action = "🔴 賣出"
                    reason_str = "空頭結構下無量反彈至 ATR 網格上限，屬於弱勢逃命高拋點。"
                elif latest['RSI_14'] < 28:
                    final_action = "🟢 買入"
                    reason_str = "空頭結構下出現極端恐慌超賣 (RSI<28)，短線具備超跌反彈空間，限極小倉位試探。"
                else:
                    final_action = "⚪ 觀望"
                    reason_str = "空頭 Grinding 下跌中，屬於『不碰族群』，堅決保持空倉觀望。"
                    
            # 軌道三：趨勢會震盪 (夾在均線群中間，無明顯方向)
            else:
                market_state = "↕️ 箱型震盪 (會震盪)"
                if current_price <= low_absorb_price:
                    final_action = "🔥 強力買入"
                    reason_str = "精準觸及您自訂的 ATR 箱型下限，網格低吸買入紀律觸發。"
                elif current_price <= low_absorb_price * 1.015:
                    final_action = "🟢 買入"
                    reason_str = "股價已逼近 ATR 網格低吸區 (1.5%以內)，左側分批低吸埋伏。"
                elif current_price >= high_toss_price:
                    final_action = "🚨 強力賣出"
                    reason_str = "精準突破您自訂的 ATR 箱型上限，網格高拋賣出紀律觸發。"
                elif current_price >= high_toss_price * 0.985:
                    final_action = "🔴 賣出"
                    reason_str = "股價已逼近 ATR 網格高拋區 (1.5%以內)，波段分批高拋落袋。"
                else:
                    final_action = "⚪ 觀望"
                    reason_str = "處於箱型網格平衡中樞，無須頻繁操作，靜待邊界警報。"

            # 只要不是觀望，就推送至今日即時行動
            if final_action != "⚪ 觀望":
                action_alerts.append({
                    "代碼": ticker,
                    "綜合建議 (ACTION)": final_action,
                    "市場狀態": market_state,
                    "最新收盤價": f"{currency_symbol}{current_price:.2f}",
                    "精簡決策原因": reason_str
                })

            summary_data.append({
                "產業領域": st.session_state.sector_map.get(ticker, "未分類"),
                "代碼": ticker,
                "最新收盤價": f"{currency_symbol}{current_price:.2f}",
                "市場狀態": market_state,
                "綜合建議 (ACTION)": final_action,
                "自訂低吸買點": f"{currency_symbol}{low_absorb_price:.2f}",
                "自訂高拋賣點": f"{currency_symbol}{high_toss_price:.2f}",
                "精簡決策原因": reason_str
            })
        except Exception:
            pass

# --- 介面排版輸出 ---

# 【第一層：🚨 今日核心交易行動 (Action Alerts) 】
st.header("🚨 今日核心執行 ACTION 面板")
if action_alerts:
    alert_df = pd.DataFrame(action_alerts)
    alert_df['sort'] = alert_df['綜合建議 (ACTION)'].map(action_rank)
    alert_df = alert_df.sort_values('sort').drop('sort', axis=1)
    st.dataframe(alert_df, use_container_width=True, hide_index=True)
else:
    st.info("🧘 報告隊長：今日 60 多隻股票中皆無個股觸發臨界點。請繼續安心保持觀望。")

st.markdown("---")

# 【第二層：📊 降維極簡總覽大清單】
st.header("📊 降維極簡大看板 (標準五等紅綠燈)")
if summary_data:
    summary_df = pd.DataFrame(summary_data)
    summary_df['sort'] = summary_df['綜合建議 (ACTION)'].map(action_rank)
    summary_df = summary_df.sort_values(by=["sort", "產業領域", "代碼"]).drop('sort', axis=1)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.markdown("---")

# 【第三層：🔍 點選個股看裸 K 與網格線】
st.header("🔍 個股動態決策軌道與核心基本面")
selected_stock = st.selectbox("選擇個股查看決策軌道：", sorted(active_tickers))

if selected_stock:
    try:
        stock_detail = yf.Ticker(selected_stock)
        df_detail = stock_detail.history(start=start_date)
        
        if not df_detail.empty and len(df_detail) > 200:
            df_detail['MA21'] = df_detail['Close'].rolling(window=21).mean()
            df_detail['MA200'] = df_detail['Close'].rolling(window=200).mean()
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df_detail.index, open=df_detail['Open'], high=df_detail['High'], low=df_detail['Low'], close=df_detail['Close'], name='K線'))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA21'], name='21MA 趨勢決策線', line=dict(color='orange', width=2.5)))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA200'], name='200MA 長期生命線', line=dict(color='crimson', width=3)))
            
            fig.update_layout(xaxis_rangeslider_visible=False, yaxis_title="價格", height=400, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
            # 基本面快照
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
