import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# 1. 網頁基本設定
st.set_page_config(layout="wide", page_title="AGI 2027 決策導航系統")
st.title("🦅 美股+台股『極簡五等燈號』自動化決策系統")
st.markdown("本系統整合 **AGI 2027 物理瓶頸敘事**、**華爾街三模型估值** 與 **台股動能籌碼分析框架**。")

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
    st.metric(label=f"大盤情緒: {fg_status}", value=f"{fg_value} / 100")
    st.progress(fg_value / 100)

with macro_col2:
    st.markdown("##### 📊 席勒本益比 (Shiller PE)")
    shiller_pe = 31.5  
    st.metric(label="S&P 500 CAPE Ratio", value=f"{shiller_pe:.1f}", delta="高於歷史均值 84%", delta_color="inverse")
    st.caption("歷史均值: 17.1 | >30 代表長線估值昂貴。")

with macro_col3:
    st.markdown("##### 📅 本週關鍵財經數據行事曆")
    calendar_data = {
        "公佈日期": ["05/18 (一)", "05/21 (四)", "05/22 (五)"],
        "關鍵數據 / 財經大事項目": ["紐約聯儲製造業指數", "Fed 貨幣政策會議紀要", "美國 4 月核心 PCE 指數"],
        "即時進度與數據結論": ["✅ 實際值 -4.2 (優於預期)", "🔮 預期釋放利率路徑密碼", "🔮 市場預期年增率 2.6%"]
    }
    st.dataframe(pd.DataFrame(calendar_data), use_container_width=True, hide_index=True)

st.markdown("---")

# ==============================================================================
# ✨ 第二層：AGI 2027 敘事與 SALP (13F) 聰明錢觀測站
# ==============================================================================
st.markdown("### 🧠 AGI 2027 敘事與 SALP 聰明錢觀測站")
salp_col1, salp_col2 = st.columns([1, 1.8])

with salp_col1:
    st.markdown("##### 🔋 AGI 算力進度與物理瓶頸預警")
    st.metric(label="兆元美元集群 (Trillion-dollar Cluster) 投資進度", value="約 35%", delta="Capex 持續上修", delta_color="normal")
    st.progress(0.35)
    st.info("💡 **物理瓶頸提醒**：AGI 的真實限制是天然氣產量與變壓器交付時間。AI 必須插電，電力層是硬資產。")

with salp_col2:
    st.markdown("##### 🏦 SALP 基金四大敘事層級持倉與對沖")
    salp_data = {
        "敘事層級": ["⚡ 電力層 (Power)", "☁️ AI 雲端 (AI Cloud)", "🌐 光通訊 (Photonics)", "🖥️ 運算層 (Compute)"],
        "SALP 籌碼動向": ["📈 長期做多", "📈 持續加倉", "🔍 戰略佈局", "🛡️ 大量買入 Put 避險"],
        "內化觀點": ["最強防禦力與剛需", "現金流紅利立即落地", "解決內部傳輸延遲", "留意估值擁擠與泡沫"]
    }
    st.dataframe(pd.DataFrame(salp_data), use_container_width=True, hide_index=True)

st.markdown("---")

# ==============================================================================
# 3. 內建核心產業地圖
# ==============================================================================
INITIAL_SECTOR_MAP = {
    "2330.TW": "🇹🇼 半導體龍頭", "2851.TW": "🇹🇼 金融再保險", "5607.TW": "🇹🇼 航空物流", "0050.TW": "🇹🇼 市值型ETF",
    "GEV": "⚡ 電網設備", "VRT": "❄️ 機房液冷", "NVDA": "🖥️ 運算核心", "MU": "🧠 記憶體", "BE": "🔋 燃料電池"
}

if "sector_map" not in st.session_state:
    st.session_state.sector_map = INITIAL_SECTOR_MAP.copy()

# 側邊欄自訂功能
with st.sidebar.expander("➕ 新增觀察股票", expanded=False):
    add_ticker = st.text_input("輸入代碼 (美股如: NVDA / 台股如: 2317.TW)").strip().upper()
    add_sector = st.selectbox("產業分類", sorted(list(set(st.session_state.sector_map.values()))))
    if st.button("確認新增"):
        if add_ticker:
            st.session_state.sector_map[add_ticker] = add_sector
            st.rerun()

all_current_tickers = sorted(list(st.session_state.sector_map.keys()))
active_tickers = st.sidebar.multiselect("💡 觀察名單管理 (點 X 刪除)", options=all_current_tickers, default=all_current_tickers)
atr_multiplier = st.sidebar.slider("自訂對稱網格 ATR 倍數 (x)", 0.5, 3.0, 1.4, 0.1)

start_date = (datetime.now() - timedelta(days=450)).strftime('%Y-%m-%d')

summary_data = []
action_alerts = []
action_rank = {"🔥 強力買入": 0, "🟢 買入": 1, "⚪ 觀望": 2, "🔴 賣出": 3, "🚨 強力賣出": 4}

with st.spinner("正在進行動能籌碼診斷與公允價值運算..."):
    for ticker in active_tickers:
        try:
            is_tw = ".TW" in ticker or ".TWO" in ticker
            curr_sym = "NT$" if is_tw else "$"
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date)
            if df.empty or len(df) < 40: continue

            # --- 公允價值運算 (三模型防空鎖) ---
            info = stock.info if stock.info else {}
            eps = info.get('forwardEps') or info.get('trailingEps')
            pe = info.get('trailingPE') or info.get('forwardPE')
            growth = info.get('earningsGrowth')
            dps = info.get('dividendRate')
            div_y = info.get('dividendYield')
            
            vals = []
            if eps and pe and eps > 0 and pe > 0: 
                vals.append(eps * pe)
            if eps and growth and eps > 0 and growth > 0: 
                vals.append(eps * (growth * 100) * 1.0)
            if dps and div_y and dps > 0 and div_y > 0: 
                vals.append(dps / div_y)
            
            if vals:
                vals.sort()
                # 防呆：如果算出多個模型，執行剔除發散值邏輯
                if len(vals) == 3:
                    median_v = vals[1]
                    if median_v > 0:
                        filtered = [v for v in vals if abs(v - median_v) / median_v <= 0.5]
                    else: filtered = vals
                    if not filtered: filtered = vals
                else:
                    filtered = vals
                min_fv, max_fv = round(min(filtered), 1), round(max(filtered), 1)
                fv_str = f"{curr_sym}{min_fv}" if min_fv == max_fv else f"{curr_sym}{min_fv} ~ {max_fv}"
            else: 
                fv_str = "數據不足"

            # --- 動能交易與技術指標運算 ---
            # 1. MACD 零軸判斷
            ema12 = df['Close'].ewm(span=12, adjust=False).mean()
            ema26 = df['Close'].ewm(span=26, adjust=False).mean()
            macd = ema12 - ema26
            macd_status = "🟢 零軸以上" if macd.iloc[-1] > 0 else "🔴 零軸以下"
            
            # 2. 均線扣底預測 (安全鎖：確保長度大於 20)
            ma20 = df['Close'].rolling(window=20).mean()
            if len(df) >= 21:
                kou_di_val = df['Close'].iloc[-20]
                ma20_slope = "增強" if df['Close'].iloc[-1] > kou_di_val else "轉弱"
            else:
                ma20_slope = "計算中"
            
            # 3. OBV 趨勢
            direction = df['Close'].diff()
            direction.iloc[0] = 0
            direction_sign = np.sign(direction)
            obv = (direction_sign * df['Volume']).cumsum()
            obv_trend = "📈 資金吸貨" if obv.iloc[-1] > obv.iloc[-5] else "📉 資金流出"
            
            # 4. ATR 與網格中心點
            high_low = df['High'] - df['Low']
            tr = pd.concat([high_low, (df['High']-df['Close'].shift(1)).abs(), (df['Low']-df['Close'].shift(1)).abs()], axis=1).max(axis=1)
            atr = tr.rolling(window=14).mean().iloc[-1]
            
            curr_p = round(df['Close'].iloc[-1], 1)
            yesterday_close = round(df['Close'].iloc[-2], 1)
            ma20_curr = round(ma20.iloc[-1], 1)
            
            low_b = round(ma20_curr - (atr * atr_multiplier), 1)
            high_b = round(ma20_curr + (atr * atr_multiplier), 1)

            # --- 綜合動能評級 ---
            score = 0
            if macd.iloc[-1] > 0: score += 1
            if len(df) >= 21 and df['Close'].iloc[-1] > kou_di_val: score += 1
            if obv.iloc[-1] > obv.iloc[-10]: score += 1
            ratings = {3: "極強", 2: "偏強", 1: "中立", 0: "偏弱"}
            momentum_rating = ratings.get(score, "極弱")

            # --- 最終 Action 燈號判定 ---
            final_action = "⚪ 觀望"
            if curr_p <= low_b: final_action = "🔥 強力買入"
            elif curr_p >= high_b: final_action = "🚨 強力賣出"

            summary_data.append({
                "產業領域": st.session_state.sector_map.get(ticker, "未分類"),
                "代碼": ticker,
                "當前股價": f"{curr_sym}{curr_p}",
                "公允價值區間": fv_str,
                "昨收盤價": f"{curr_sym}{yesterday_close}",
                "MA20": f"{curr_sym}{ma20_curr}",
                "動能評級": momentum_rating,
                "MACD": macd_status,
                "20MA扣底": ma20_slope,
                "資金流(OBV)": obv_trend,
                "買點": f"{curr_sym}{low_b}",
                "賣點": f"{curr_sym}{high_b}",
                "綜合建議": final_action
            })
        except Exception as e:
            pass # 核心防空鎖：單檔股票出錯直接跳過，絕不弄垮整個網站

# --- 介面排版輸出 ---
st.header("📊 降維極簡大看板 (動能籌碼＋估值完全體)")
if summary_data:
    summary_df = pd.DataFrame(summary_data)
    summary_df['sort'] = summary_df['綜合建議'].map(action_rank)
    summary_df = summary_df.sort_values(by="sort").drop('sort', axis=1)
    
    # 調整欄位順序更貼合使用者習慣
    order_cols = ["產業領域", "代碼", "當前股價", "公允價值區間", "昨收盤價", "MA20", "動能評級", "MACD", "20MA扣底", "資金流(OBV)", "買點", "賣點", "綜合建議"]
    existing_cols = [c for c in order_cols if c in summary_df.columns]
    summary_df = summary_df[existing_cols]
    
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

with st.expander("💡 投資決策參考守則：如何利用「公允價值」與「動能」做共振？"):
    st.markdown("""
    * **情境 A (網格買點 + 遠低於公允價值 + 動能極強)**：**大膽買進**。技術面超跌、基本面便宜、且 MACD 守住零軸以上。
    * **情境 B (網格買點 + 估值昂貴)**：**縮小部位**。雖然價格跌到網格下限，但基本面無支撐，小心「價值陷阱」。
    * **情境 C (網格賣點 + 遠低於公允價值)**：**分批賣出，保留底倉**。技術面超漲，但基本面強勁，大戶夢想尚未實現，不宜清倉。
    * **情境 D (網格賣點 + 估值昂貴 + OBV 背離)**：**果斷清倉高拋**。大戶倒貨跡象明顯，泡沫隨時破裂。
    """)

st.markdown("---")

st.header("🔍 個股動態決策軌道與核心指標驗證")
selected_stock = st.selectbox("選擇個股查看實戰軌道：", sorted(active_tickers))

if selected_stock:
    try:
        sd = yf.Ticker(selected_stock)
        df_d = sd.history(period="1y")
        if not df_d.empty:
            df_d['MA20'] = df_d['Close'].rolling(20).mean()
            df_d['MA200'] = df_d['Close'].rolling(200).mean()
            
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
            fig.add_trace(go.Candlestick(x=df_d.index, open=df_d['Open'], high=df_d['High'], low=df_d['Low'], close=df_d['Close'], name='K線'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_d.index, y=df_d['MA20'], name='20MA', line=dict(color='orange', width=2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_d.index, y=df_d['MA200'], name='200MA', line=dict(color='crimson', width=3)), row=1, col=1)
            
            # 副圖：MACD
            ema12_d = df_d['Close'].ewm(span=12, adjust=False).mean()
            ema26_d = df_d['Close'].ewm(span=26, adjust=False).mean()
            macd_d = ema12_d - ema26_d
            fig.add_trace(go.Scatter(x=df_d.index, y=macd_d, name='MACD(零軸趨勢)', line=dict(color='dodgerblue')), row=2, col=1)
            fig.add_hline(y=0, line_dash="dash", line_color="grey", row=2, col=1)
            
            fig.update_layout(xaxis_rangeslider_visible=False, height=500, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            # 基本面指標
            info_d = sd.info if sd.info else {}
            col_f1, col_f2, col_f3 = st.columns(3)
            
            rev = info_d.get('totalRevenue', 1)
            net_inc = info_d.get('netIncomeToCommon', 0)
            net_margin = (net_inc / rev * 100) if rev and rev != 1 else 0
            
            col_f1.metric("公司淨利率", f"{net_margin:.1f}%")
            col_f2.metric("流動比率", f"{info_d.get('currentRatio', 0):.1f}", "✅ 安全" if info_d.get('currentRatio', 0) > 1.5 else "⚠️ 偏低")
            col_f3.metric("當前 PE 估值", f"{info_d.get('trailingPE', info_d.get('forwardPE', 0)):.1f}")
    except Exception as e:
        st.error(f"分析載入失敗: {e}")
