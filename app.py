import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# 1. 網頁基本設定
st.set_page_config(layout="wide", page_title="美股+台股指標趨勢、網格波段與Henry戰法綜合導航系統")
st.title("🦅 美股+台股指標網格 vs Henry戰法雙系統終極儀表板")
st.markdown("本系統全面相容**原有雙軌量化清單**與**Henry秒懂美股核心戰法**，助您多維度確認資金交叉共振點。")

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

st.sidebar.header("⚙️ 實時管理股票名單")

with st.sidebar.expander("➕ 新增股票至觀察清單", expanded=False):
    add_ticker = st.text_input("輸入代碼 (美股如: VRT / 台股如: 2317.TW)").strip().upper()
    add_sector = st.selectbox("選擇或指定其產業分類", sorted(list(set(st.session_state.sector_map.values()))))
    if st.button("確認新增"):
        if add_ticker:
            st.session_state.sector_map[add_ticker] = add_sector
            st.toast(f"成功新增 {add_ticker} 進入清單！")
            st.rerun()

all_current_tickers = sorted(list(st.session_state.sector_map.keys()))
active_tickers = st.sidebar.multiselect("💡 目前觀察清單 (點選 X 可直接刪除)", options=all_current_tickers, default=all_current_tickers)

# 策略參數配置
st.sidebar.header("📊 波動率與網格參數設定")
atr_period = st.sidebar.slider("ATR 計算天數", 5, 22, 14)
entry_multiplier = st.sidebar.slider("低吸買進 ATR 倍數", 0.5, 2.5, 1.0, 0.1)
exit_multiplier = st.sidebar.slider("高拋賣出 ATR 倍數", 0.5, 2.5, 1.5, 0.1)

# 強制拉長歷史追蹤範圍以計算精確的 200MA 生命線
start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

# 數據容器
summary_data = []
action_alerts = []

# 標準排序映射
rank_map = {"🔥 強烈買進": 0, "🟢 買進": 1, "⚪ 觀望": 2, "🔴 賣出": 3, "🚨 強烈賣出": 4}

with st.spinner("正在跨系統同步計算指標、網格與 Henry 四大戰法..."):
    for ticker in active_tickers:
        try:
            is_tw = ".TW" in ticker or ".TWO" in ticker
            currency_symbol = "NT$ " if is_tw else "$ "
            
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date)
            if df.empty or len(df) < 220: # 確保天數大於200天以正確計算 200MA
                continue
                
            # ==========================================
            # 1. 舊系統指標計算
            # ==========================================
            high_low = df['High'] - df['Low']
            high_cp = (df['High'] - df['Close'].shift(1)).abs()
            low_cp = (df['Low'] - df['Close'].shift(1)).abs()
            tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
            df['ATR'] = tr.rolling(window=atr_period).mean()
            
            delta = df['Close'].diff()
            gain = (delta.clip(lower=0)).rolling(window=14).mean()
            loss = (-delta.clip(upper=0)).rolling(window=14).mean()
            rs = gain / loss.replace(0, 0.00001)
            df['RSI_14'] = 100 - (100 / (1 + rs))
            
            df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD_12_26'] = df['EMA12'] - df['EMA26']
            df['MACD_Sig_9'] = df['MACD_12_26'].ewm(span=9, adjust=False).mean()
            
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['STD20'] = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['MA20'] + (2 * df['STD20'])
            df['BB_Lower'] = df['MA20'] - (2 * df['STD20'])
            
            df['L9'] = df['Low'].rolling(window=9).min()
            df['H9'] = df['High'].rolling(window=9).max()
            df['RSV'] = 100 * ((df['Close'] - df['L9']) / (df['H9'] - df['L9']).replace(0, 0.00001))
            df['K'] = df['RSV'].ewm(alpha=1/3, adjust=False).mean()
            df['D'] = df['K'].ewm(alpha=1/3, adjust=False).mean()
            df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()

            # ==========================================
            # 2. 新增 Henry 指標運算
            # ==========================================
            df['MA5'] = df['Close'].rolling(window=5).mean()
            df['MA21'] = df['Close'].rolling(window=21).mean()
            df['MA25'] = df['Close'].rolling(window=25).mean()
            df['MA200'] = df['Close'].rolling(window=200).mean()
            
            df['Vol_MA5'] = df['Volume'].rolling(window=5).mean()
            df['Vol_MA60'] = df['Volume'].rolling(window=60).mean()
            
            df['EMA5'] = df['Close'].ewm(span=5, adjust=False).mean()
            df['EMA34'] = df['Close'].ewm(span=34, adjust=False).mean()
            df['MACD_Inst'] = df['EMA5'] - df['EMA34']
            df['MACD_Inst_Sig'] = df['MACD_Inst'].ewm(span=5, adjust=False).mean()
            df['MACD_Inst_Hist'] = df['MACD_Inst'] - df['MACD_Inst_Sig']

            latest = df.iloc[-1]
            prev = df.iloc[-2]
            current_price = float(latest['Close'])
            prev_close = float(prev['Close'])
            prev_atr = float(prev['ATR'])
            
            low_absorb_price = prev_close - (prev_atr * entry_multiplier)
            high_toss_price = prev_close + (prev_atr * exit_multiplier)
            
            # --- 舊系統 5等燈號判定邏輯 ---
            bullish_score, bearish_score = 0, 0
            if latest['RSI_14'] < 36: bullish_score += 1
            if current_price <= latest['BB_Lower']: bullish_score += 1
            if prev['K'] <= prev['D'] and latest['K'] > latest['D']: bullish_score += 1
            if prev['MACD_12_26'] <= prev['MACD_Sig_9'] and latest['MACD_12_26'] > latest['MACD_Sig_9']: bullish_score += 1
            
            if latest['RSI_14'] > 66: bearish_score += 1
            if current_price >= latest['BB_Upper']: bearish_score += 1
            if prev['K'] >= prev['D'] and latest['K'] < latest['D']: bearish_score += 1
            if prev['MACD_12_26'] >= prev['MACD_Sig_9'] and latest['MACD_12_26'] < latest['MACD_Sig_9']: bearish_score += 1
            
            volume_spike = latest['Volume'] > (latest['Vol_MA20'] * 1.5)
            
            old_ind_status = "⚪ 觀望"
            if bullish_score >= 3 or (bullish_score >= 2 and volume_spike): old_ind_status = "🔥 強烈買進"
            elif bullish_score >= 1: old_ind_status = "🟢 買進"
            elif bearish_score >= 3 or (bearish_score >= 2 and volume_spike): old_ind_status = "🚨 強烈賣出"
            elif bearish_score >= 1: old_ind_status = "🔴 賣出"

            old_atr_status = "⚪ 觀望"
            if current_price <= low_absorb_price: old_atr_status = "🔥 強烈買進"
            elif current_price <= low_absorb_price * 1.015: old_atr_status = "🟢 買進"
            elif current_price >= high_toss_price: old_atr_status = "🚨 強烈賣出"
            elif current_price >= high_toss_price * 0.985: old_atr_status = "🔴 賣出"

            # --- Henry 戰法判定邏輯 ---
            # 2133 波段決策
            buy_2133 = latest['Close'] >= latest['MA21'] * 1.03 or (df['Close'].tail(3) > df['MA21'].tail(3)).all()
            sell_2133 = latest['Close'] <= latest['MA21'] * 0.97 or (df['Close'].tail(3) < df['MA21'].tail(3)).all()
            henry_2133 = "🟢 買進" if buy_2133 else ("🔴 賣出" if sell_2133 else "⚪ 觀望")

            # 2560 量價共振
            p_above_ma25 = latest['Close'] > latest['MA25']
            had_low_volume = (df['Volume'].tail(10) < df['Vol_MA60'].tail(10)).any()
            vol_ma5_up = latest['Vol_MA5'] > prev['Vol_MA5']
            vol_binding = abs(latest['Vol_MA5'] - latest['Vol_MA60']) / latest['Vol_MA60'] < 0.12
            henry_2560 = "🔥 觸發共振" if (p_above_ma25 and had_low_volume and vol_ma5_up and vol_binding) else "⚪ 觀望"

            # 機構 MACD 型態識別
            henry_macd_shape = "⚪ 常態"
            if latest['MACD_Inst'] > 0 and latest['MACD_Inst_Sig'] > 0:
                if latest['MACD_Inst_Hist'] > prev['MACD_Inst_Hist'] and prev['MACD_Inst_Hist'] <= df['MACD_Inst_Hist'].iloc[-3]:
                    henry_macd_shape = "🌟 佛手向上"
            if prev['MACD_Inst'] <= prev['MACD_Inst_Sig'] and latest['MACD_Inst'] > latest['MACD_Inst_Sig'] and latest['MACD_Inst'] < 0:
                henry_macd_shape = "🦆 小鴨出水"

            # 只要任何一方觸發關鍵訊號，送入警告面板
            if "買進" in old_ind_status or "買進" in old_atr_status or henry_2133 == "🟢 買進" or henry_2560 == "🔥 觸發共振" or "🌟" in henry_macd_shape or "🦆" in henry_macd_shape:
                action_alerts.append({
                    "代碼": ticker, "舊指標決策": old_ind_status, "舊網格決策": old_atr_status,
                    "Henry 2133": henry_2133, "Henry 2560": henry_2560, "機構MACD型態": henry_macd_shape,
                    "最新價": f"{currency_symbol}{current_price:.2f}"
                })

            summary_data.append({
                "產業領域": st.session_state.sector_map.get(ticker, "未分類"), "代碼": ticker, "最新收盤價": f"{currency_symbol}{current_price:.2f}",
                "舊指標決策": old_ind_status, "舊網格決策": old_atr_status, "Henry 2133": henry_2133, "Henry 2560": henry_2560, "機構MACD型態": henry_macd_shape,
                "建議低吸價": f"{currency_symbol}{low_absorb_price:.2f}", "建議高拋價": f"{currency_symbol}{high_toss_price:.2f}"
            })
        except Exception:
            pass

# ==========================================
# 前端畫面排版 (UI Layout 大融合)
# ==========================================

# 【第一層：🚨 今日核心交易行動警告區】
st.header("🚨 今日綜合核心交易行動面板 (Action Panel)")
if action_alerts:
    alert_df = pd.DataFrame(action_alerts)
    st.dataframe(alert_df, use_container_width=True, hide_index=True)
else:
    st.info("🧘 今日各大系統均無特殊交易提示，請繼續安心保持觀望。")

st.markdown("---")

# 【第二層：📊 完整產業雙系統量化大清單】
st.header("📊 雙系統綜合量化大清單 (指標、網格、Henry戰法支援)")
if summary_data:
    summary_df = pd.DataFrame(summary_data)
    summary_df['sort_1'] = summary_df['舊指標決策'].map(rank_map)
    summary_df['sort_2'] = summary_df['舊網格決策'].map(rank_map)
    summary_df['final_sort'] = summary_df[['sort_1', 'sort_2']].min(axis=1)
    summary_df = summary_df.sort_values(by=["final_sort", "產業領域", "代碼"]).drop(['sort_1', 'sort_2', 'final_sort'], axis=1)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.markdown("---")

# 【第三層：🔍 個股深度雙軌通道與 Henry 指標大視覺化】
st.header("🔍 個股深度技術面、基本面與籌碼催化劑分析")
selected_stock = st.selectbox("選擇你想查看的個股細節：", sorted(active_tickers))

if selected_stock:
    try:
        is_tw = ".TW" in selected_stock or ".TWO" in selected_stock
        currency_label = "新台幣" if is_tw else "美元"
        
        stock_detail = yf.Ticker(selected_stock)
        # 用於畫圖的詳細數據重新抓取
        df_detail = stock_detail.history(start=start_date)
        
        if not df_detail.empty and len(df_detail) > 200:
            # 重新計算繪圖用均線與布林
            df_detail['MA21'] = df_detail['Close'].rolling(window=21).mean()
            df_detail['MA200'] = df_detail['Close'].rolling(window=200).mean()
            df_detail['MA20'] = df_detail['Close'].rolling(window=20).mean()
            df_detail['STD20'] = df_detail['Close'].rolling(window=20).std()
            df_detail['BB_Upper'] = df_detail['MA20'] + (2 * df_detail['STD20'])
            df_detail['BB_Lower'] = df_detail['MA20'] - (2 * df_detail['STD20'])
            
            # Henry 均量與機構 MACD
            df_detail['Vol_MA5'] = df_detail['Volume'].rolling(window=5).mean()
            df_detail['Vol_MA60'] = df_detail['Volume'].rolling(window=60).mean()
            df_detail['EMA5'] = df_detail['Close'].ewm(span=5, adjust=False).mean()
            df_detail['EMA34'] = df_detail['Close'].ewm(span=34, adjust=False).mean()
            df_detail['MACD_Inst'] = df_detail['EMA5'] - df_detail['EMA34']
            df_detail['MACD_Inst_Sig'] = df_detail['MACD_Inst'].ewm(span=5, adjust=False).mean()
            df_detail['MACD_Inst_Hist'] = df_detail['MACD_Inst'] - df_detail['MACD_Inst_Sig']
            
            # 💡 建立 Henry 規格之三列聯動高階圖表
            fig = make_subplots(
                rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, 
                row_heights=[0.5, 0.2, 0.3],
                subplot_titles=("K線主圖 (融合舊布林下軌支撐 + Henry 21MA決策線/200MA生命線)", "2560 戰法量能監控 (5日與60日均量線)", "Henry 機構級 MACD (5, 34, 5) 能量潮")
            )
            
            # 主圖
            fig.add_trace(go.Candlestick(x=df_detail.index, open=df_detail['Open'], high=df_detail['High'], low=df_detail['Low'], close=df_detail['Close'], name='K線'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['BB_Upper'], name='舊系統布林上軌', line=dict(color='rgba(255,165,0,0.4)', width=1.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['BB_Lower'], name='舊系統布林下軌', line=dict(color='rgba(0,191,255,0.4)', width=1.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA21'], name='Henry 21MA 決策線', line=dict(color='orange', width=2.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA200'], name='⚠️ Henry 200MA 生命線', line=dict(color='crimson', width=3.5)), row=1, col=1)
            
            # 副圖一
            fig.add_trace(go.Bar(x=df_detail.index, y=df_detail['Volume'], name='成交量', marker_color='rgba(128,128,128,0.5)'), row=2, col=1)
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['Vol_MA5'], name='5日均量線', line=dict(color='orange', width=1.5)), row=2, col=1)
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['Vol_MA60'], name='60日均量地量線', line=dict(color='purple', width=2)), row=2, col=1)
            
            # 副圖二
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MACD_Inst'], name='機構快線', line=dict(color='dodgerblue', width=1.5)), row=3, col=1)
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MACD_Inst_Sig'], name='機構慢線', line=dict(color='tomato', width=1.5)), row=3, col=1)
            colors = ['rgba(235, 71, 71, 0.7)' if val >= 0 else 'rgba(71, 235, 115, 0.7)' for val in df_detail['MACD_Inst_Hist']]
            fig.add_trace(go.Bar(x=df_detail.index, y=df_detail['MACD_Inst_Hist'], name='能量柱', marker_color=colors), row=3, col=1)
            
            fig.update_layout(height=800, xaxis_rangeslider_visible=False, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
            # 💡 Henry 3+1 潛力股財務基本面看板
            st.subheader("🧱 Henry 3+1 潛力股核心基本面診斷")
            info = stock_detail.info
            if info:
                col_f1, col_f2, col_f3 = st.columns(3)
                net_margin = info.get('netIncomeToCommon', 0) / info.get('totalRevenue', 1) if info.get('netIncomeToCommon') else 0
                current_ratio = info.get('currentRatio', 0)
                pe_ratio = info.get('trailingPE', "無資料")
                
                col_f1.metric("公司淨利率 (Net Profit Margin)", f"{net_margin * 100:.2f}%")
                col_f2.metric("流動比率 (Current Ratio)", f"{current_ratio:.2f}", "✅ 安全" if current_ratio > 1.5 else "⚠️ 偏低")
                col_f3.metric("當前 PE 估值 (Trailing P/E)", f"{pe_ratio}")
                st.info("💡 **【第 +1 項指標提示 — 企業護城河 (Moat)】**：量化數據僅代表歷史成績，建倉前請務必自行評估其技術代際壁壘（如 TSMC 的晶圓領先地位）與品牌轉換成本。")
            else:
                st.write("該個股（如台股或部分標的）暫無線上 info 財務數據。")
                
            # 舊系統籌碼與新聞
            st.markdown("---")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.subheader("🕵️‍♂️ 公司內部人交易動向 (Insider)")
                if is_tw: st.info("台股籌碼請參閱公開資訊觀測站。")
                else:
                    try:
                        insider_df = stock_detail.insider_transactions
                        if insider_df is not None and not insider_df.empty:
                            st.dataframe(insider_df[['Start Date', 'Insider', 'Position', 'Transaction', 'Shares', 'Value']].head(6), use_container_width=True)
                        else: st.write("近期無內部人大幅交易申報。")
                    except Exception: st.write("無法調閱美股內部人數據。")
            with col_d2:
                st.subheader("📰 影響股價的最新市場消息")
                try:
                    news_list = stock_detail.news
                    if news_list:
                        for article in news_list[:3]:
                            st.markdown(f"**[{article.get('title', '無標題')}]({article.get('link', '#')})**")
                            st.caption(f"來源: {article.get('publisher', '未知')}")
                except Exception: st.write("暫時無法獲取實時新聞。")
    except Exception as e:
        st.error(f"深度分析載入失敗: {e}")
