# nifty_engine/ui/app.py

import streamlit as st
import pandas as pd
import time
import os
import json
from nifty_engine.core.market_engine import SmartMoney, Greeks, GEX, OptionsAnalyzer, MarketMoodIndex
from nifty_engine.strategies.manager import StrategyManager
from nifty_engine.data.database import Database
from nifty_engine.core.movers import NiftyMovers
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="OpenAlgo Nifty Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- Custom Styling (OpenAlgo Inspired) ---
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main-header {
        font-size: 24px;
        font-weight: bold;
        color: #1e293b;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
    }
    .status-online { color: #10b981; font-weight: bold; }
    .status-offline { color: #ef4444; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'db' not in st.session_state:
    st.session_state.db = Database()
if 'strategy_manager' not in st.session_state:
    st.session_state.strategy_manager = StrategyManager(st.session_state.db)
    st.session_state.strategy_manager.load_strategies()
if 'movers' not in st.session_state:
    st.session_state.movers = NiftyMovers()

def main():
    # --- Sidebar Navigation ---
    with st.sidebar:
        st.image("https://openalgo.in/assets/img/logo.png", width=150) # Mock logo or text
        st.title("OpenAlgo v3")
        st.divider()
        menu = st.radio("Navigation", ["Dashboard", "Strategies", "Option Chain", "Rules Engine", "Settings"])

        st.divider()
        engine_running = st.session_state.db.get_config("engine_running", "OFF") == "ON"
        status_text = "ONLINE" if engine_running else "OFFLINE"
        status_class = "status-online" if engine_running else "status-offline"
        st.markdown(f"System Status: <span class='{status_class}'>{status_text}</span>", unsafe_allow_html=True)

        kill_switch = st.session_state.db.get_config("kill_switch", "OFF") == "ON"
        if kill_switch:
            if st.button("🔓 RESET KILL SWITCH", type="primary", use_container_width=True):
                st.session_state.db.set_config("kill_switch", "OFF")
                st.rerun()
        else:
            if st.button("🔴 EMERGENCY STOP", type="secondary", use_container_width=True):
                st.session_state.strategy_manager.stop_all()
                st.rerun()

    if menu == "Dashboard":
        render_dashboard()
    elif menu == "Strategies":
        render_strategies()
    elif menu == "Option Chain":
        render_option_chain()
    elif menu == "Rules Engine":
        render_rules()

def render_dashboard():
    st.markdown("<div class='main-header'>Dashboard Summary</div>", unsafe_allow_html=True)

    # Summary Metrics
    c1, c2, c3, c4 = st.columns(4)
    chart_df = st.session_state.db.get_last_candles("NIFTY", limit=1)
    spot = chart_df['close'].iloc[-1] if not chart_df.empty else 24500

    with c1:
        st.markdown(f"<div class='metric-card'><b>NIFTY 50</b><br><h2 style='margin:0;'>₹{spot}</h2><span style='color:green;'>+1.2%</span></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><b>Active Strategies</b><br><h2 style='margin:0;'>{sum(1 for s in st.session_state.strategy_manager.strategies.values() if s.enabled)}</h2><span>Running</span></div>", unsafe_allow_html=True)
    with c3:
        mmi = MarketMoodIndex.calculate(1.15, 45, 1.2, 1)
        regime = MarketMoodIndex.get_regime(mmi)
        st.markdown(f"<div class='metric-card'><b>Market Mood (MMI)</b><br><h2 style='margin:0;'>{mmi}</h2><span>{regime}</span></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric-card'><b>A/D Ratio</b><br><h2 style='margin:0;'>1.85</h2><span style='color:green;'>Bullish Bias</span></div>", unsafe_allow_html=True)

    st.divider()

    col_chart, col_movers = st.columns([2, 1])
    with col_chart:
        st.subheader("Nifty Intraday Chart")
        chart_df_full = st.session_state.db.get_last_candles("NIFTY", limit=100)
        if not chart_df_full.empty:
            fig = go.Figure(data=[go.Candlestick(x=chart_df_full['timestamp'],
                            open=chart_df_full['open'],
                            high=chart_df_full['high'],
                            low=chart_df_full['low'],
                            close=chart_df_full['close'])])
            fig.update_layout(template="plotly_white", height=400, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

    with col_movers:
        st.subheader("Top Contributors")
        # Pulling from Knowledge Base weights
        weights = st.session_state.movers.weights
        top_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:5]

        # Simulating live changes for visualization
        for symbol, weight in top_weights:
            # Fake change for UI demo
            sim_change = 0.5 if symbol in ["RELIANCE", "HDFCBANK"] else -0.2
            impact = (sim_change * weight)
            color = "green" if impact > 0 else "red"
            st.markdown(f"**{symbol}**: <span style='color:{color};'>{impact:+.2f} pts (W: {weight}%)</span>", unsafe_allow_html=True)

def render_strategies():
    st.markdown("<div class='main-header'>Strategy Management</div>", unsafe_allow_html=True)

    # Upload New
    with st.expander("➕ Deploy New Strategy"):
        uploaded_file = st.file_uploader("Upload .py file", type="py")
        if uploaded_file:
            save_path = os.path.join("nifty_engine/strategies", uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("Uploaded!")
            st.session_state.strategy_manager.load_strategies()

    # Table View
    st.subheader("Deployed Strategies")
    strategies = st.session_state.strategy_manager.strategies

    if not strategies:
        st.info("No strategies deployed.")
        return

    # Header
    cols = st.columns([2, 1, 1, 1, 1])
    cols[0].write("**Strategy Name**")
    cols[1].write("**Instrument**")
    cols[2].write("**Timeframe**")
    cols[3].write("**Status**")
    cols[4].write("**Actions**")

    for name, strategy in strategies.items():
        st.divider()
        c = st.columns([2, 1, 1, 1, 1])
        c[0].write(f"**{name}**")
        c[1].write(", ".join(getattr(strategy, 'instruments', ['NIFTY'])))
        c[2].write(getattr(strategy, 'timeframe', '1m'))

        status_db = st.session_state.db.get_config(f"strategy_{name}", "OFF")
        status_color = "green" if status_db == "ON" else "gray"
        c[3].write(f":{status_color}[{status_db}]")

        # Action buttons
        with c[4]:
            if status_db == "OFF":
                if st.button("▶️", key=f"start_{name}", help="Start Strategy"):
                    st.session_state.strategy_manager.enable_strategy(name)
                    st.rerun()
            else:
                if st.button("⏸️", key=f"stop_{name}", help="Stop Strategy"):
                    st.session_state.strategy_manager.disable_strategy(name)
                    st.rerun()

            if st.button("🗑️", key=f"del_{name}", help="Delete"):
                st.session_state.strategy_manager.delete_strategy(name)
                st.rerun()

def render_option_chain():
    st.markdown("<div class='main-header'>Advanced Option Chain</div>", unsafe_allow_html=True)

    # Quick Summary
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total PCR", "1.15", "0.02")
    with c2:
        st.metric("Max Pain", "24,500", "0")
    with c3:
        st.metric("Straddle Price (ATM)", "185.40", "-2.10")

    st.divider()

    # Dummy Table with better layout
    data = {
        "OI (Call)": ["120k", "250k", "180k", "90k", "45k"],
        "Delta (C)": [0.91, 0.75, 0.52, 0.31, 0.15],
        "LTP (CE)": [245.2, 160.5, 85.4, 42.1, 18.2],
        "Strike": [24300, 24400, 24500, 24600, 24700],
        "LTP (PE)": [12.1, 35.4, 100.2, 175.6, 260.1],
        "Delta (P)": [-0.09, -0.25, -0.48, -0.69, -0.85],
        "OI (Put)": ["35k", "85k", "210k", "150k", "110k"]
    }
    df = pd.DataFrame(data)

    # Highlight ATM
    def highlight_atm(s):
        return ['background-color: #e2e8f0' if s.Strike == 24500 else '' for _ in s]

    st.dataframe(df.style.apply(highlight_atm, axis=1), use_container_width=True)

    st.write("### Gamma Exposure (GEX) Profile")
    st.info("Negative GEX below 24,400 | Positive GEX above 24,600")

def render_rules():
    st.markdown("<div class='main-header'>Market Rules Engine</div>", unsafe_allow_html=True)
    kb_path = "nifty_engine/data/knowledge_base.json"
    if os.path.exists(kb_path):
        with open(kb_path, 'r') as f:
            kb_data = json.load(f)

        st.write("### Deterministic Knowledge")
        rules = kb_data.get("market_rules", {})
        for r, d in rules.items():
            st.success(f"**{r}**: {d}")

        st.write("### Impact Behaviors")
        st.json(kb_data.get("impact_behavior", []))

if __name__ == "__main__":
    main()
