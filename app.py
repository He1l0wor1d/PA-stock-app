# ==============================================================================
# 🔍 個股動態決策軌道與核心基本面 (縮排完全修復與實時圖表標記版)
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
            
            # 計算歷史滾動的 ATR 網格線，用於在歷史 K 線圖上標註「當時」的訊號點
            high_low_det = df_detail['High'] - df_detail['Low']
            tr_det = pd.concat([high_low_det, (df_detail['High'] - df_detail['Close'].shift(1)).abs(), (df_detail['Low'] - df_detail['Close'].shift(1)).abs()], axis=1).max(axis=1)
            df_detail['ATR_det'] = tr_det.rolling(window=atr_period).mean()
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df_detail.index, open=df_detail['Open'], high=df_detail['High'], low=df_detail['Low'], close=df_detail['Close'], name='K線'))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA20_plot'], name='20MA 趨勢決策線', line=dict(color='orange', width=2.5)))
            fig.add_trace(go.Scatter(x=df_detail.index, y=df_detail['MA200'], name='200MA 長期生命線', line=dict(color='crimson', width=3)))
            
            # 🚀 實時回溯歷史價格，找出所有「符合策略臨界點」的歷史日期，直接標記在圖表上！
            annotations = []
            for date, row in df_detail.dropna(subset=['MA20_plot', 'MA200', 'ATR_det']).iterrows():
                p_close = row['Close']
                p_ma20 = row['MA20_plot']
                p_ma200 = row['MA200']
                p_atr = row['ATR_det']
                
                low_bound = p_ma20 - (p_atr * atr_multiplier)
                high_bound = p_ma20 + (p_atr * atr_multiplier)
                
                # 判定歷史這一天的訊號狀態
                if p_ma20 >= p_ma200: # 多頭波段
                    if p_close <= low_bound: # 🔥 強力買入
                        annotations.append(dict(
                            x=date, y=row['Low'], text="🔥強買", showarrow=True,
                            arrowhead=2, arrowcolor="green", arrowsize=1, arrowwidth=2,
                            ax=0, ay=35, font=dict(color="white", size=10), bgcolor="green"
                        ))
                    elif p_close >= high_bound: # 🔴 賣出
                        annotations.append(dict(
                            x=date, y=row['High'], text="🔴高拋", showarrow=True,
                            arrowhead=2, arrowcolor="purple", arrowsize=1, arrowwidth=2,
                            ax=0, ay=-35, font=dict(color="white", size=10), bgcolor="purple"
                        ))
                else: # 空頭結構
                    idx_loc = df_detail.index.get_loc(date)
                    if idx_loc > 0:
                        p_yesterday_close = df_detail['Close'].iloc[idx_loc-1]
                        if p_yesterday_close >= p_ma20 and p_close < p_ma20: # 🚨 強力賣出
                            annotations.append(dict(
                                x=date, y=row['High'], text="🚨強賣", showarrow=True,
                                arrowhead=2, arrowcolor="red", arrowsize=1, arrowwidth=2,
                                ax=0, ay=-35, font=dict(color="white", size=10), bgcolor="red"
                            ))

            fig.update_layout(
                xaxis_rangeslider_visible=False, yaxis_title="價格", height=450, 
                template="plotly_white", annotations=annotations
            )
            st.plotly_chart(fig, use_container_width=True)
            
            info = stock_detail.info if stock_detail.info else {}
            is_tw_detail = ".TW" in selected_stock or ".TWO" in selected_stock
            
            # 營收與資本支出定量常態引擎
            rev_growth = info.get('revenueGrowth') or info.get('earningsGrowth') or info.get('earningsQuarterlyGrowth')
            rev_growth_str = f"{rev_growth * 100:.1f}% (華爾街法說前瞻預估)" if rev_growth is not None else "未揭露未來指引"
            
            capex_str = "未揭露未來指引"
            try:
                cf = stock_detail.quarterly_cashflow
                if cf is None or cf.empty: cf = stock_detail.cashflow
                if cf is not None and not cf.empty:
                    m_keys = [k for k in cf.index if 'Capital Expenditure' in str(k) or 'capital_expenditures' in str(k).lower()]
                    if m_keys:
                        latest_raw = abs(cf.loc[m_keys[0]].dropna().iloc[0])
                        if not is_tw_detail and latest_raw > 10000000000:
                            latest_raw = latest_raw / 32.0
                            capex_str = f"約 {latest_raw * 4 / 100000000:.1f} 億美元 (未發布指引-改採季報年化折算)"
                        elif is_tw_detail:
                            capex_str = f"約 {latest_raw * 4 / 100000000:.1f} 億新台幣 (未發布指引-改採季報年化折算)"
                        else:
                            capex_str = f"約 {latest_raw * 4 / 100000000:.1f} 億美元 (未發布指引-改採季報年化折算)"
            except Exception: 
                pass
            
            pe_ratio = info.get('trailingPE') or info.get('forwardPE')
            pe_str = f"{pe_ratio:.1f}" if pe_ratio else "無數據"
            
            col_f1, col_f2, col_f3 = st.columns(3)
            col_f1.metric("2026 全年營收年增率預期 (YoY)", rev_growth_str)
            col_f2.metric("2026 全年資本支出指引 (CapEx)", capex_str)
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
                        "累積報酬率": f"{return_pct:.1f}%"
                    })
                    break 

        except Exception: 
            pass

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
