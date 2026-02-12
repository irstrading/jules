# nifty_engine/ui/app.py

import streamlit as st
import pandas as pd
import time
import os
from nifty_engine.core.market_engine import SmartMoney, Greeks, GEX
from nifty_engine.strategies.manager import StrategyManager
from nifty_engine.data.database import Database
import plotly.graph_objects as go

st.set_page_config(page_title="Nifty Engine Dashboard", layout="wide")

# Initialize Session State
if 'db' not in st.session_state:
    st.session_state.db = Database()
if 'strategy_manager' not in st.session_state:
    st.session_state.strategy_manager = StrategyManager(st.session_state.db)
    st.session_state.strategy_manager.load_strategies()

def main():
    st.title("🚀 Nifty Advanced Algo Dashboard")

    # Sync status from DB
    st.session_state.strategy_manager.sync_with_db()
    kill_switch_active = st.session_state.db.get_config("kill_switch", "OFF") == "ON"
    engine_running = st.session_state.db.get_config("engine_running", "OFF") == "ON"

    # Sidebar: Control Panel
    st.sidebar.header("🕹️ Control Panel")

    if kill_switch_active:
        st.sidebar.error("🚨 EMERGENCY STOP ACTIVE")
        if st.sidebar.button("🔓 RESET KILL SWITCH", use_container_width=True):
            st.session_state.db.set_config("kill_switch", "OFF")
            st.rerun()
    else:
        if st.sidebar.button("🔴 EMERGENCY STOP", use_container_width=True):
            st.session_state.strategy_manager.stop_all()
            st.rerun()

    status_color = "green" if engine_running else "red"
    st.sidebar.markdown(f"**Engine Status:** :{status_color}[{'RUNNING' if engine_running else 'STOPPED'}]")

    # --- Strategy Management ---
    st.sidebar.divider()
    st.sidebar.subheader("📂 Strategy Management")

    uploaded_file = st.sidebar.file_uploader("Upload New Strategy (.py)", type="py")
    if uploaded_file is not None:
        save_path = os.path.join("nifty_engine/strategies", uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.sidebar.success(f"Uploaded {uploaded_file.name}")
        st.session_state.strategy_manager.load_strategies()
        st.rerun()

    st.sidebar.write("### Active Strategies")
    for name, strategy in st.session_state.strategy_manager.strategies.items():
        col1, col2 = st.sidebar.columns([3, 1])
        col1.write(name)

        # Read status from DB for this strategy
        current_status = st.session_state.db.get_config(f"strategy_{name}", "OFF")

        if current_status == "ON":
            if col2.button("OFF", key=f"off_{name}"):
                st.session_state.strategy_manager.disable_strategy(name)
                st.rerun()
        else:
            if col2.button("ON", key=f"on_{name}", disabled=kill_switch_active):
                st.session_state.strategy_manager.enable_strategy(name)
                st.rerun()

    # --- Main Dashboard Metrics ---
    m1, m2, m3, m4 = st.columns(4)

    # Fetch real data if available
    chart_df = st.session_state.db.get_last_candles("NIFTY", limit=100)

    if not chart_df.empty:
        spot_price = chart_df['close'].iloc[-1]
        price_change = spot_price - chart_df['close'].iloc[0]
        # Example OI and Greeks (In production, fetch from DB/API)
        pcr = SmartMoney.calculate_pcr(1000000, 1200000)
        sentiment = SmartMoney.analyze_sentiment(price_change, -15000)
        gex_val = GEX.calculate_strike_gex(5000, 4000, 0.0005, 0.0004, spot_price)
    else:
        spot_price = 0
        pcr = 0
        sentiment = "N/A"
        gex_val = 0

    m1.metric("Nifty Spot", f"₹{spot_price}")
    m2.metric("Put-Call Ratio (PCR)", pcr)
    m3.metric("Market Sentiment", sentiment)
    m4.metric("Net Gamma Exposure", f"{gex_val:.2f} Cr")

    # --- Charts ---
    st.divider()
    col_chart, col_alerts = st.columns([2, 1])

    with col_chart:
        st.subheader("📊 Price & OI Analysis")
        if not chart_df.empty:
            fig = go.Figure(data=[go.Candlestick(x=chart_df['timestamp'],
                            open=chart_df['open'],
                            high=chart_df['high'],
                            low=chart_df['low'],
                            close=chart_df['close'])])
            fig.update_layout(xaxis_rangeslider_visible=False, height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No market data in database. Engine might be offline or warming up.")

    with col_alerts:
        st.subheader("🔔 Recent Signals")
        alerts_df = st.session_state.db.get_recent_alerts(limit=20)
        if not alerts_df.empty:
            for _, alert in alerts_df.iterrows():
                st.info(f"**{alert['strategy_name']}** ({alert['timestamp']}): {alert['message']}")
        else:
            st.write("No signals yet.")

    # Auto-refresh
    time.sleep(5)
    st.rerun()

if __name__ == "__main__":
    main()
