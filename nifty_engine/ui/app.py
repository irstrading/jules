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
if 'strategy_manager' not in st.session_state:
    st.session_state.strategy_manager = StrategyManager()
    st.session_state.strategy_manager.load_strategies()
if 'running' not in st.session_state:
    st.session_state.running = False
if 'db' not in st.session_state:
    st.session_state.db = Database()

def main():
    st.title("🚀 Nifty Advanced Algo Dashboard")

    # Sidebar: Control Panel
    st.sidebar.header("🕹️ Control Panel")

    if st.sidebar.button("🔴 EMERGENCY STOP", use_container_width=True):
        st.session_state.strategy_manager.stop_all()
        st.session_state.running = False
        st.error("ALL STRATEGIES STOPPED!")

    status_color = "green" if st.session_state.running else "red"
    st.sidebar.markdown(f"**Status:** :{status_color}[{'RUNNING' if st.session_state.running else 'STOPPED'}]")

    if not st.session_state.running:
        if st.sidebar.button("▶️ START ENGINE"):
            st.session_state.running = True
            st.rerun()
    else:
        if st.sidebar.button("⏸️ PAUSE ENGINE"):
            st.session_state.running = False
            st.rerun()

    # --- Strategy Management ---
    st.sidebar.divider()
    st.sidebar.subheader("📂 Strategy Management")

    uploaded_file = st.sidebar.file_uploader("Upload New Strategy (.py)", type="py")
    if uploaded_file is not None:
        with open(os.path.join("nifty_engine/strategies", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.sidebar.success(f"Uploaded {uploaded_file.name}")
        st.session_state.strategy_manager.load_strategies()

    st.sidebar.write("### Active Strategies")
    for name, strategy in st.session_state.strategy_manager.strategies.items():
        col1, col2 = st.sidebar.columns([3, 1])
        col1.write(name)
        if strategy.enabled:
            if col2.button("OFF", key=f"off_{name}"):
                st.session_state.strategy_manager.disable_strategy(name)
                st.rerun()
        else:
            if col2.button("ON", key=f"on_{name}"):
                st.session_state.strategy_manager.enable_strategy(name)
                st.rerun()

    # --- Main Dashboard Metrics ---
    m1, m2, m3, m4 = st.columns(4)

    # Placeholder data for demonstration
    spot_price = 24500
    pcr = SmartMoney.calculate_pcr(1000000, 1200000)
    sentiment = SmartMoney.analyze_sentiment(50, -15000)
    gex_val = GEX.calculate_strike_gex(5000, 4000, 0.0005, 0.0004, spot_price)

    m1.metric("Nifty Spot", f"₹{spot_price}", "+0.25%")
    m2.metric("Put-Call Ratio (PCR)", pcr, "Bullish" if pcr > 1 else "Bearish")
    m3.metric("Market Sentiment", sentiment)
    m4.metric("Net Gamma Exposure", f"{gex_val:.2f} Cr")

    # --- Charts ---
    st.divider()
    col_chart, col_alerts = st.columns([2, 1])

    with col_chart:
        st.subheader("📊 Price & OI Analysis")
        # Simulate some data for the chart
        chart_df = st.session_state.db.get_last_candles("NIFTY", limit=50)
        if chart_df.empty:
            # Create dummy data for visualization if DB is empty
            dates = pd.date_range(end=pd.Timestamp.now(), periods=50, freq='min')
            chart_df = pd.DataFrame({
                'timestamp': dates,
                'open': [24500 + i for i in range(50)],
                'high': [24505 + i for i in range(50)],
                'low': [24495 + i for i in range(50)],
                'close': [24502 + i for i in range(50)],
                'volume': [1000 for _ in range(50)]
            })

        fig = go.Figure(data=[go.Candlestick(x=chart_df['timestamp'],
                        open=chart_df['open'],
                        high=chart_df['high'],
                        low=chart_df['low'],
                        close=chart_df['close'])])
        fig.update_layout(title="Nifty 1-Minute Chart", xaxis_rangeslider_visible=False, height=500)
        st.plotly_chart(fig, use_container_width=True)

    with col_alerts:
        st.subheader("🔔 Recent Signals")
        alerts_df = st.session_state.db.get_recent_alerts(limit=20)
        if not alerts_df.empty:
            for _, alert in alerts_df.iterrows():
                st.info(f"**{alert['strategy_name']}** ({alert['timestamp']}): {alert['message']}")
        else:
            st.write("No signals yet.")

    # --- Background Loop simulation if running ---
    if st.session_state.running:
        # In a real app, this would be handled by a separate process/thread
        # but for Streamlit we can do a simple loop or use a background runner
        st.empty()
        # time.sleep(1)
        # st.rerun()

if __name__ == "__main__":
    main()
