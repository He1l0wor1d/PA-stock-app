import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 網頁基本設定
st.set_page_config(layout="wide", page_title="美股多指標共振與即時行動警告系統")
st.title("🦅 美股產業群聚、內部人籌碼與卡脖子趨勢儀表板")

# 2. 內建 2026 最新核心產業與「卡脖子」供應鏈地圖
INITIAL_SECTOR_MAP = {
    # 2026 核心卡脖子：電力基建、液冷與綠能技術
    "GEV": "⚡ 電網設備與基建 (卡脖子核心)", 
    "ETN": "⚡ 電網設備與基建 (卡脖子核心)", 
    "PWR": "⚡ 電網線路工程 (卡脖子核心)",
    "VRT": "❄️ 機房液冷與散熱 (卡脖子核心)", 
    "MOD": "❄️ 機房液冷與散熱 (卡脖子核心)",
    "CEG": "☢️ 獨立核能/天然氣發電", 
    "VST": "☢️ 獨立核能/天然氣發電",
    "ENPH": "☀️ 綠能逆變器與微電網", 
    "SEDG": "☀️ 綠能逆變器與微電網",
    
    # AI 核心晶片、記憶體與網通
    "NVDA": "AI 晶片 / 半導體設計", "AVGO": "AI 晶片 / 半導體設計", "QCOM": "AI晶片 / 半導體設計", 
    "MRVL": "AI 晶片 / 半導體設計", "TXN": "AI 晶片 / 半導體設計", "ADI": "AI 晶片 / 半導體設計", 
    "ON": "AI 晶片 / 半導體設計", "MPWR": "AI 晶片 / 半導體設計", "NVTS": "AI 晶片 / 半導體設計",
    "MU": "記憶體與儲存 (HBM/DRAM)", "SNDK": "記憶體與儲存 (HBM/DRAM)", "RMBS": "記憶體與儲存 (HBM/DRAM)", 
    "DRAM": "記憶體與儲存 (HBM/DRAM)", "SITM": "記憶體與儲存 (HBM/DRAM)",
    "COHR": "光通訊與網通硬體", "LITE": "光通訊與網通硬體", "AAOI": "光通訊與網通硬體", 
    "FN": "光通訊與網通硬體", "CIEN": "光通訊與網通硬體", "NOK": "光通訊與網通硬體", 
    "CBRS": "光通訊與網通硬體", "ANET": "光通訊與網通硬體",
    
    # 晶圓代工與軟體巨頭
    "TSM": "晶圓代工與設備製程", "INTC": "晶圓代工與設備製程", "SNPS": "晶圓代工與設備製程", 
    "TSEM": "晶圓代工與設備製程", "AXTI": "晶圓代工與設備製程", "SIMO": "晶圓代工與設備製程", 
    "ALAB": "晶圓代工與設備製程", "ASML": "晶圓代工與設備製程",
    "META": "AI 巨頭 / 軟體平台", "AMZN": "AI 巨頭 / 軟體平台", "MSFT": "AI 巨頭 / 軟體平台", 
    "AAPL": "AI 巨頭 / 軟體平台", "GOOGL": "AI 巨頭 / 軟體平台", "PLTR": "AI 巨頭 / 軟體平台", 
    "NOW": "AI 巨頭 / 軟體平台", "ORCL": "AI 巨頭 / 軟體平台", "APP": "AI 巨頭 / 軟體平台", 
    "NET": "AI 巨頭 / 軟體平台", "CRWV": "AI 巨頭 / 軟體平台",
    
    # 其他原有美股分類
    "RDW": "航太、太空與國防", "RKLB": "航太、太空與國防", "ASTS": "航太、太空與國防", "BA": "航太、太空與國防", "ONDS": "航太、太空與國防",
    "OXY": "傳統能源與礦產", "EQT": "傳統能源與礦產",
    "TEM": "生技與醫療科技", "GRAL": "生技與醫療科技", "ILMN": "生技與醫療科技",
    "SOFI": "金融科技與資產管理", "HOOD": "金融科技與資產管理", "GS": "金融科技與資產管理", "BLK": "金融科技與資產管理", "BX": "金融科技與資產管理", "SEI": "金融科技與資產管理",
    "TSLA": "智能車與新能源", "MSTR": "比特幣與微策略科技", "BRK-B": "價值投資綜合控股 (波克夏)", "SHLD": "其他綜合/特殊題材", "NBIS": "其他綜合/特殊題材",
    "QQQ": "指數與主題型 ETF", "MAGS": "指數與主題型 ETF", "SOXX": "指數與主題型 ETF", "SMH": "指數與主題型 ETF", "XSD": "指數與主題型 ETF", "GLD": "指數與主題型 ETF"
}

# 3. 實時動態增減股票邏輯 (使用 Session State 快取)
if "sector_map" not in st.session_state:
    st.session_state.sector_map = INITIAL_SECTOR_MAP.copy()

st.sidebar.header("⚙️ 實時管理股票名單")

# 功能 A：即時動態手動新增
with st.sidebar.expander("➕ 新增股票至觀察清單", expanded=False):
    add_ticker = st.text_input("輸入美股代碼 (例如: VRT, SMCI)").strip().upper()
    add_sector = st.selectbox("選擇或指定其產業分類", sorted(list(set(st.session_state.sector_map.values()))))
    if st.button("確認新增"):
        if add_ticker:
            st.session_state.sector_map[add_ticker] = add_sector
            st.toast(f"成功新增 {add_ticker} 進入清單！")
            st.rerun()

# 功能 B：一鍵移除與篩選清單
all_current_tickers = sorted(list(st.session_state.sector_map.keys()))
active_tickers = st.sidebar.multiselect(
    "💡 目前觀察清單 (點選 X 可直接刪除股票)", 
    options=all_current_tickers,
    default=all_current_tickers
)

# 策略參數配置
st.sidebar.header("📊 交易策略設定")
atr_period = st.sidebar.slider("ATR 計算天數", 5, 22, 14)
entry_multiplier = st.sidebar.slider("進場拉回 ATR 倍數", 0.5, 2.0, 1.0, 0.1)
stop_multiplier = st.sidebar.slider("停損防守 ATR 倍數", 1.5, 4.0, 2.0, 0.1)
days_back = st.sidebar.number_input("追蹤歷史天數", value=180, min_value=60)
start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

# 4. 內建網頁的技術趨勢導讀專區
with st.expander("💡 華爾街最新 AI 基礎建設『卡脖子 (Choke Points)』前沿趨勢導讀", expanded=True):
    st.markdown("""
    * **電網與變壓器荒 (Grid Interconnection)**：全美近半數資料中心因電力短缺與变压器交期拉長(拉長至5年)而卡關。**核心看點**：`GEV`, `ETN`, `PWR`，以及手握核電與天然氣的獨立發電商 `CEG`, `VST`。
    * **高密度液冷轉折點 (Thermal Liquid Cooling)**：新世代 GPU 晶片功耗飆破物理極限，傳統氣冷全面強制轉向液冷。**核心看點**：全球液冷龍頭 `VRT`、散熱黑馬 `MOD`。
    * **分散式綠能微電網 (BYOP)**：科技巨頭為達成淨零碳排並跳過爆滿的傳統電網，開始推動機房自我綠能發電。**核心看點**：微型逆變器大廠 `ENPH`, `SEDG`。
    """)

# 核心數據儲存器
summary_data = []
action_alerts = []

with st.spinner("正在即時計算四大指標與篩選緊急行動訊號..."):
    for ticker in active_tickers:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date)
            if df.empty or len(df) < 35:
                continue
                
            # 核心指標計算 (ATR, RSI, MACD, Bollinger Bands, KD)
            high_low = df['High'] - df['Low']
            high_cp = (df['High'] - df['Close'].shift(1)).abs()
            low_cp = (df['Low'] - df['Close'].shift(1)).abs()
            tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
            df['ATR'] = tr.rolling(window=atr_period).mean()
            
            delta = df['Close'].diff()
            gain = (delta.clip(lower=0)).rolling(window=14).mean()
            loss = (-delta.clip(upper=0)).rolling(window=14).mean()
            rs = gain / loss.replace(0, 0.00001)
            df['RSI'] = 100 - (100 / (1 + rs))
            
            df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA12'] - df['EMA26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['STD20'] = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['MA20'] + (2 * df['STD20'])
            df['BB_Lower'] = df['MA20'] - (2 * df['STD20'])
            
            df['L9'] = df['Low'].rolling(window=9).min()
            df['H9'] = df['High'].rolling(window=9).max()
            df['RSV'] = 100 * ((df['Close'] - df['L9']) / (df['H9'] - df['L9']).replace(0, 0.00001))
            df['K'] = df['RSV'].ewm(alpha=1/3, adjust=False).mean()
            df['D'] = df['K'].ewm(alpha=1/3, adjust=False).mean()
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            current_price = float(latest['Close'])
            atr_val = float(latest['ATR'])
            
            suggested_entry = current_price - (atr_val * entry_multiplier)
            suggested_stop = current_price - (atr_val * stop_multiplier)
            
            # 各大欄位獨立狀態判定
            rsi_val = latest['RSI']
            rsi_status = "超賣 🟢" if rsi_val < 35 else ("超買 🔴" if rsi_val > 70 else "中性 ⚪")
            
            macd_status = "中性 ⚪"
            if prev['MACD'] <= prev['MACD_Signal'] and latest['MACD'] > latest['MACD_Signal']: macd_status = "金叉 🚀"
            elif prev['MACD'] >= prev['MACD_Signal'] and latest['MACD'] < latest['MACD_Signal']: macd_status = "死叉 🚨"
                
            kd_status = "中性 ⚪"
            if prev['K'] <= prev['D'] and latest['K'] > latest['D']: kd_status = "金叉 📈" if latest['K'] < 30 else "交叉 🟢"
            elif prev['K'] >= prev['D'] and latest['K'] < latest['D']: kd_status = "死叉 📉" if latest['K'] > 70 else "交叉 🔴"
                
            bb_status = "中性 ⚪"
            if current_price <= latest['BB_Lower']: bb_status = "觸及下軌 🛡️"
            elif current_price >= latest['BB_Upper']: bb_status = "突破上軌 ⚡"
                
            # 共振抄底指數計算
            resonance_score = 0
            if rsi_val < 38: resonance_score += 1
            if bb_status == "觸及下軌 🛡️": resonance_score += 1
            if "金叉" in kd_status or latest['K'] < 25: resonance_score += 1
            if "金叉" in macd_status: resonance_score += 1
            
            action_needed = "⏳ 觀望"
            
            # 行動提示大分流
            if resonance_score >= 3:
                action_needed = "🔥 強烈共振抄底點！"
                action_alerts.append({"代碼": ticker, "型態類型": "🔥 完美共振抄底", "即時收盤價": f"${current_price:.2f}", "關鍵原因": f"KD/MACD/RSI/布林出現 {resonance_score} 項指標低檔共振！"})
            elif abs(current_price - suggested_entry) / current_price <= 0.015:
                action_needed = "🎯 進入拉回買進區"
                action_alerts.append({"代碼": ticker, "型態類型": "🎯 ATR 拉回埋伏點", "即時收盤價": f"${current_price:.2f}", "關鍵原因": "股價已拉回到『最新價 - 1倍ATR』的黃金買進位附近！"})
            elif current_price <= suggested_stop * 1.015:
                action_needed = "🚨 觸及防守停損線"
                action_alerts.append({"代碼": ticker, "型態類型": "🚨 風險防守極限", "即時收盤價": f"${current_price:.2f}", "關鍵原因": "股價已逼近『ATR停損線』，請注意控制曝險。"})
            elif current_price >= latest['BB_Upper'] and (latest['MACD'] > latest['MACD_Signal']):
                action_needed = "🚀 強勢突破暴漲點"
                action_alerts.append({"代碼": ticker, "型態類型": "🚀 噴發暴漲提示", "即時收盤價": f"${current_price:.2f}", "關鍵原因": "股價強勢帶量突破布林上軌，MACD同步看多，容易發動連續軋空！"})

            summary_data.append({
                "產業領域": st.session_state.sector_map.get(ticker, "未分類"),
                "代碼": ticker,
                "最新收盤價": f"${current_price:.2f}",
                "RSI狀態": rsi_status,
                "MACD訊號": macd_status,
                "KD狀態": kd_status,
                "布林通道": bb_status,
                "共振分數": f"{resonance_score}/4",
                "每日建議行動": action_needed,
                "防守停損位": f"${suggested_stop:.2f}"
            })
        except Exception:
            pass

# 5. 畫面呈現
st.header("🚨 今日核心交易行動 (Action Alerts)")
if action_alerts:
    alert_df = pd.DataFrame(action_alerts)
    st.dataframe(alert_df, use_container_width=True, hide_index=True)
else:
    st.info("🧘 今日名單中暫無個股觸發『共振抄底/ATR買賣點/暴漲突破』。可以繼續觀望。")

st.markdown("---")
st.header("📊 完整產業與技術指標清單")
if summary_data:
    summary_df = pd.DataFrame(summary_data).sort_values(by=["每日建議行動", "產業領域", "代碼"], ascending=[False, True, True])
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.header("🔍 個股深度催化劑通道分析")
selected_stock = st.selectbox("選擇你想查看的個股細節：", sorted(active_tickers))

if selected_stock:
    try:
        stock_detail = yf.Ticker(selected_stock)
        df_detail = stock_detail.history(start=start_date)
        if not df_detail.empty and len(df_detail) > 20:
            df_detail['MA20'] = df_detail['Close'].rolling(window=20).mean()
            df_detail['STD20'] = df_detail['Close'].rolling(window=20).std()
            df_detail['BB_Upper'] = df_detail['MA20'] + (2 * df_detail['STD20'])
            df_detail['BB_Lower'] = df_detail['MA20'] - (2 * df_detail['STD20'])
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df_detail.index, open=df_detail['Open'], high=df_detail['High'], low=df_detail['Low'], close=df_detail['Close'], name='K線'))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['BB_Upper'], name='布林上軌', line=dict(color='rgba(255, 165, 0, 0.6)', width=1.5)))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA20'], name='20MA生命線', line=dict(color='rgba(128, 128, 128, 0.5)', width=1)))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['BB_Lower'], name='布林下軌', line=dict(color='rgba(0, 191, 255, 0.6)', width=1.5)))
            fig.update_layout(xaxis_rangeslider_visible=False, yaxis_title="價格 (美元)", height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🕵️‍♂️ 公司內部人交易動向 (Insider)")
                insider_df = stock_detail.insider_transactions
                if insider_df is not None and not insider_df.empty:
                    st.dataframe(insider_df[['Start Date', 'Insider', 'Position', 'Transaction', 'Shares', 'Value']].head(6), use_container_width=True)
                else: st.write("近期無內部人大幅交易申報。")
            with col2:
                st.subheader("📰 影響股價的最新市場消息")
                news_list = stock_detail.news
                if news_list:
                    for article in news_list[:3]:
                        st.markdown(f"**[{article.get('title', '無標題')}]({article.get('link', '#')})**")
                        st.caption(f"來源: {article.get('publisher', '未知')}")
                else: st.write("暫無即時新聞。")
    except Exception as e:
        st.error(f"分析失敗: {e}")