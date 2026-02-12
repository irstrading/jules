# nifty_engine/ui/app.py

import streamlit as st
import pandas as pd
import time
import os
import json
from nifty_engine.core.market_engine import SmartMoney, Greeks, GEX, OptionsAnalyzer
from nifty_engine.strategies.manager import StrategyManager
from nifty_engine.data.database import Database
from nifty_engine.core.movers import NiftyMovers
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Stocker Advanced Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for "Stocker" Look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #3e4150;
    }
    .ticker-wrapper {
        background: #1e2130;
        color: #fff;
        padding: 10px 0;
        overflow: hidden;
        white-space: nowrap;
        border-bottom: 2px solid #3e4150;
        margin-bottom: 20px;
    }
    .ticker {
        display: inline-block;
        animation: marquee 30s linear infinite;
    }
    @keyframes marquee {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .ticker-item {
        display: inline-block;
        margin-right: 50px;
        font-weight: bold;
    }
    .price-up { color: #00ff00; }
    .price-down { color: #ff4b4b; }
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

def get_dummy_movers():
    # In production, these would be fetched from live data
    return [
        {"symbol": "RELIANCE", "change": 1.2, "impact": 11.04},
        {"symbol": "HDFCBANK", "change": -0.5, "impact": -5.75},
        {"symbol": "ICICIBANK", "change": 0.8, "impact": 6.24},
        {"symbol": "INFY", "change": 1.5, "impact": 8.25},
        {"symbol": "TCS", "change": -0.2, "impact": -0.74}
    ]

def main():
    # --- Top Scrolling Ticker ---
    movers_data = get_dummy_movers()
    ticker_html = '<div class="ticker-wrapper"><div class="ticker">'
    for m in movers_data:
        color_class = "price-up" if m['change'] > 0 else "price-down"
        arrow = "▲" if m['change'] > 0 else "▼"
        ticker_html += f'<span class="ticker-item">{m["symbol"]} <span class="{color_class}">{m["change"]}% {arrow}</span></span>'
    ticker_html += '</div></div>'
    st.markdown(ticker_html, unsafe_allow_html=True)

    # --- Header ---
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.title("📈 Stocker Pro: Nifty Engine")
    with c2:
        kill_switch_active = st.session_state.db.get_config("kill_switch", "OFF") == "ON"
        if kill_switch_active:
            if st.button("🔓 RESET KILL SWITCH", type="primary", use_container_width=True):
                st.session_state.db.set_config("kill_switch", "OFF")
                st.rerun()
        else:
            if st.button("🔴 EMERGENCY STOP", type="secondary", use_container_width=True):
                st.session_state.strategy_manager.stop_all()
                st.rerun()
    with c3:
        st.write(f"**Last Update:** {datetime.now().strftime('%H:%M:%S')}")

    # --- Tabs ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "🚀 Strategy Center", "🔍 OI Analyzer", "⚖️ Straddle Chart", "🏗️ Knowledge Base"])

    with tab1:
        col_main, col_side = st.columns([3, 1])

        with col_main:
            # Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            chart_df = st.session_state.db.get_last_candles("NIFTY", limit=100)
            spot = chart_df['close'].iloc[-1] if not chart_df.empty else 24500
            m1.metric("NIFTY 50", f"₹{spot}", "1.2%")
            m2.metric("Market PCR", "1.15", "Bullish")
            m3.metric("Sentiment", "Long Buildup")
            m4.metric("Net GEX", "45.2 Cr")

            # Main Chart
            if not chart_df.empty:
                fig = go.Figure(data=[go.Candlestick(x=chart_df['timestamp'],
                                open=chart_df['open'],
                                high=chart_df['high'],
                                low=chart_df['low'],
                                close=chart_df['close'])])
                fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig, use_container_width=True)

        with col_side:
            st.subheader("🔥 Top Movers")
            for m in movers_data:
                col_s, col_i = st.columns([2, 1])
                color = "green" if m['impact'] > 0 else "red"
                col_s.write(f"**{m['symbol']}**")
                col_i.write(f":{color}[{m['impact']:+.2f}]")

            st.divider()
            st.subheader("🏙️ Sector Watch")
            sectors = {"Banking": 0.8, "IT": 1.2, "FMCG": -0.3, "Auto": 0.5}
            for s, p in sectors.items():
                st.progress((p + 2) / 4, text=f"{s}: {p}%")

    with tab2:
        st.subheader("📂 Strategy Management")

        # Upload
        with st.expander("➕ Upload New Strategy"):
            uploaded_file = st.file_uploader("Choose a Python file", type="py")
            if uploaded_file:
                save_path = os.path.join("nifty_engine/strategies", uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Strategy {uploaded_file.name} uploaded successfully!")
                st.session_state.strategy_manager.load_strategies()

        # List & Manage
        strategies = st.session_state.strategy_manager.strategies
        for name, strategy in strategies.items():
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                c1.write(f"### {name}")
                c1.write(f"Symbol: {strategy.symbol} | Enabled: {strategy.enabled}")

                status_db = st.session_state.db.get_config(f"strategy_{name}", "OFF")
                if status_db == "ON":
                    if c2.button("Deactivate", key=f"deact_{name}", use_container_width=True):
                        st.session_state.strategy_manager.disable_strategy(name)
                        st.rerun()
                else:
                    if c2.button("Activate", key=f"act_{name}", use_container_width=True, type="primary"):
                        st.session_state.strategy_manager.enable_strategy(name)
                        st.rerun()

                if c3.button("Edit Code", key=f"edit_{name}", use_container_width=True):
                    st.session_state[f"editing_{name}"] = True

                if c4.button("Delete", key=f"del_{name}", use_container_width=True):
                    st.session_state.strategy_manager.delete_strategy(name)
                    st.rerun()

                if st.session_state.get(f"editing_{name}", False):
                    filename = f"{name.lower().replace(' ', '_')}.py"
                    filepath = os.path.join("nifty_engine/strategies", filename)
                    if os.path.exists(filepath):
                        with open(filepath, 'r') as f:
                            code = f.read()
                        new_code = st.text_area("Code Editor", value=code, height=300, key=f"area_{name}")
                        if st.button("Save Changes", key=f"save_{name}"):
                            st.session_state.strategy_manager.update_strategy_code(name, new_code)
                            st.session_state[f"editing_{name}"] = False
                            st.success("Code updated!")
                            st.rerun()

    with tab3:
        st.subheader("📊 Open Interest Analyzer")
        strikes = [24400, 24450, 24500, 24550, 24600]
        call_oi = [120000, 150000, 250000, 180000, 140000]
        put_oi = [180000, 220000, 210000, 110000, 80000]

        fig_oi = go.Figure()
        fig_oi.add_trace(go.Bar(x=strikes, y=call_oi, name='Call OI', marker_color='red'))
        fig_oi.add_trace(go.Bar(x=strikes, y=put_oi, name='Put OI', marker_color='green'))
        fig_oi.update_layout(barmode='group', template="plotly_dark", title="Strike-wise OI Accumulation")
        st.plotly_chart(fig_oi, use_container_width=True)

    with tab4:
        st.subheader("⚖️ At-The-Money Straddle")
        # Dummy straddle data
        times = pd.date_range(start="09:15", end="15:30", freq="5min")
        prices = [450 - (i*0.2) + (i*0.01)**2 for i in range(len(times))]

        fig_straddle = go.Figure()
        fig_straddle.add_trace(go.Scatter(x=times, y=prices, mode='lines', name='Straddle Premium'))
        fig_straddle.update_layout(template="plotly_dark", title="24500 Straddle Price Trend")
        st.plotly_chart(fig_straddle, use_container_width=True)

    with tab5:
        st.subheader("🧠 System Knowledge")
        kb_path = "nifty_engine/data/knowledge_base.json"
        if os.path.exists(kb_path):
            with open(kb_path, 'r') as f:
                kb_data = json.load(f)
            st.json(kb_data)

        st.subheader("📝 Market Impact Rules")
        rules = kb_data.get("market_rules", {})
        for r, d in rules.items():
            st.info(f"**{r}:** {d}")

    # Auto-refresh
    time.sleep(10)
    st.rerun()

if __name__ == "__main__":
    main()
