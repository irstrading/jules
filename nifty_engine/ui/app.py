# nifty_engine/ui/app.py

import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import json
from nifty_engine.core.market_engine import SmartMoney, Greeks, GEX, OptionsAnalyzer, MarketMoodIndex, IndexAlignment
from nifty_engine.core.indicators import Indicators
from streamlit_autorefresh import st_autorefresh
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
    # Auto-refresh every 2 minutes (120,000 milliseconds)
    st_autorefresh(interval=120000, key="datarefresh")

    # --- Sidebar Navigation ---
    with st.sidebar:
        st.image("https://openalgo.in/assets/img/logo.png", width=150) # Mock logo or text
        st.title("OpenAlgo v3")
        st.divider()
        menu = st.radio("Navigation", ["Dashboard", "Stock Intelligence", "Option Chain", "Strategy Builder", "Rules Engine", "Algo Study Center", "Settings"])

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
    elif menu == "Option Chain":
        render_option_chain()
    elif menu == "Stock Intelligence":
        render_stock_intelligence()
    elif menu == "Strategy Builder":
        render_strategy_builder()
    elif menu == "Rules Engine":
        render_rules()
    elif menu == "Algo Study Center":
        render_study_center()
    elif menu == "Settings":
        render_settings()

def render_dashboard():
    st.markdown("<div class='main-header'>Market Intelligence Dashboard</div>", unsafe_allow_html=True)

    # Read Real Market State from DB
    market_state_json = st.session_state.db.get_config("market_state")
    if market_state_json:
        market_state = json.loads(market_state_json)
        alignment = market_state.get("alignment", {"status": "Waiting for Data...", "bullish_pct": 0, "bearish_pct": 0})
        stock_states = market_state.get("stock_states", {})
    else:
        alignment = {"status": "Waiting for Data...", "bullish_pct": 0, "bearish_pct": 0}
        stock_states = {}

    # Alignment Alert
    if "Strong" in alignment['status']:
        color = "#10b981" if "Bullish" in alignment['status'] else "#ef4444"
        st.success(f"### 🎯 Market Alignment: {alignment['status']}")
    else:
        st.warning(f"### ⚖️ Market Alignment: {alignment['status']}")

    # AI Insights Section
    with st.expander("🤖 **AI Market Interpretation** (OpenAlgo Intelligence)", expanded=True):
        from nifty_engine.core.ai_insights import AIInsights
        ai = AIInsights()
        # MMI calculation for logic
        mmi_val = MarketMoodIndex.calculate(1.15, 45, 1.2, 1)
        insights = ai.generate_narrative({'alignment': alignment, 'mmi': mmi_val, 'stock_states': stock_states})
        for insight in insights:
            st.write(insight)

    # Summary Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='metric-card'><b>Bullish Participation</b><br><h2 style='color:#10b981; margin:0;'>{alignment['bullish_pct']}%</h2></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><b>Bearish Participation</b><br><h2 style='color:#ef4444; margin:0;'>{alignment['bearish_pct']}%</h2></div>", unsafe_allow_html=True)
    with c3:
        mmi = MarketMoodIndex.calculate(1.15, 45, 1.2, 1)
        regime = MarketMoodIndex.get_regime(mmi)
        st.markdown(f"<div class='metric-card'><b>Market Mood (MMI)</b><br><h2 style='margin:0;'>{mmi}</h2><span>{regime}</span></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric-card'><b>Total Market Weight</b><br><h2 style='margin:0;'>100%</h2><span>Tracked</span></div>", unsafe_allow_html=True)

    st.divider()

    col_chart, col_movers = st.columns([2, 1])
    with col_chart:
        st.subheader("ATM Straddle Chart (Combined Premium)")

        # Fetch Real Straddle Data from DB
        df_straddle = st.session_state.db.get_last_candles("NIFTY_STRADDLE", limit=100)

        if df_straddle.empty:
            st.info("Waiting for Live Straddle Data... (Syncing from Angel One)")
            # Fallback for visual demo if DB is empty
            timestamps = pd.date_range(end=datetime.now(), periods=100, freq='1min')
            prices = [150 + (i * 0.5) + (np.random.randn() * 2) for i in range(100)]
            df_straddle = pd.DataFrame({'timestamp': timestamps, 'close': prices})

        # Calculate VWAP (Cumulative Average as requested)
        df_straddle['vwap'] = Indicators.cumulative_average(df_straddle['close'])

        fig = go.Figure()
        # Straddle Premium Line
        fig.add_trace(go.Scatter(x=df_straddle['timestamp'], y=df_straddle['close'],
                                 name='Straddle Price', line=dict(color='#2563eb', width=2)))
        # VWAP Line
        fig.add_trace(go.Scatter(x=df_straddle['timestamp'], y=df_straddle['vwap'],
                                 name='Straddle VWAP', line=dict(color='#000000', width=1.5, dash='dash')))

        fig.update_layout(template="plotly_white", height=450, margin=dict(l=0, r=0, t=0, b=0),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)

        st.caption("Chart updates every 2 minutes automatically.")

    with col_movers:
        st.subheader("Weightage Movers")
        weights = st.session_state.movers.weights
        top_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:10]

        for symbol, weight in top_weights:
            state = stock_states.get(symbol, {})
            lp = state.get('lp', 0)
            pc = state.get('pc', 0)

            direction = 0
            if lp > pc: direction = 1
            elif lp < pc: direction = -1

            color = "#10b981" if direction == 1 else ("#ef4444" if direction == -1 else "#64748b")
            arrow = "▲" if direction == 1 else ("▼" if direction == -1 else "▬")
            st.markdown(f"**{symbol}** ({weight}%): <span style='color:{color};'>{arrow}</span>", unsafe_allow_html=True)


def render_stock_intelligence():
    st.markdown("<div class='main-header'>Stock Swing Intelligence (1-5 Days)</div>", unsafe_allow_html=True)

    tier1 = st.session_state.movers.get_stocks_by_tier("Tier-1")

    st.write("### Tier-1 F&O Stocks (High Liquidity)")

    # Grid of Stock Analysis
    cols = st.columns(3)
    for i, symbol in enumerate(tier1):
        with cols[i % 3]:
            # Mock Data for UI
            price_change = np.random.uniform(-2, 2)
            iv_change = np.random.uniform(-5, 5)
            regime = StockAnalyzer.analyze_iv_regime(price_change, iv_change)

            # Score Calculation
            data = {
                'structure': 'BULLISH' if price_change > 0 else 'BEARISH',
                'sector_trend': 'SUPPORTIVE',
                'gex': -1,
                'iv_trend': 'RISING' if iv_change > 0 else 'FALLING',
                'vomma': 'HIGH',
                'atm_oi': 'UNWINDING'
            }
            signal, score = StockAnalyzer.calculate_swing_score(data)

            # Metric Card
            color = "#10b981" if score >= 8 else ("#3b82f6" if score >= 6 else "#64748b")
            st.markdown(f"""
            <div style='background: white; padding: 15px; border-radius: 10px; border-left: 5px solid {color}; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                <h3 style='margin:0;'>{symbol}</h3>
                <p style='margin: 5px 0; font-size: 14px; color: #64748b;'>{regime}</p>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-weight: bold; color: {color};'>{signal}</span>
                    <span style='background: #f1f5f9; padding: 2px 8px; border-radius: 5px;'>Score: {score}/10</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

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

def render_study_center():
    st.markdown("<div class='main-header'>Algo Study Center & Institutional Playbook</div>", unsafe_allow_html=True)

    kb_path = "nifty_engine/data/knowledge_base.json"
    if not os.path.exists(kb_path):
        st.error("Knowledge Base not found.")
        return

    with open(kb_path, 'r') as f:
        kb = json.load(f)

    tab_intel, tab_greeks, tab_mmi = st.tabs(["🏛️ Institutional Playbook", "📊 Option Greeks", "🧠 Market Mood"])

    with tab_intel:
        st.subheader("Institutional Pattern Library")
        patterns = kb.get("institutional_patterns", {})

        cat = st.selectbox("Select Category", list(patterns.keys()))
        if cat:
            for p_name, p_data in patterns[cat].items():
                with st.expander(f"**{p_name.replace('_', ' ').title()}** ({p_data.get('historical_success', 'N/A')} Success)"):
                    st.write(f"🔍 **Detection:** {p_data['detection']}")
                    st.write(f"💡 **Meaning:** {p_data['meaning']}")
                    st.success(f"🚀 **Action:** {p_data['action']}")
                    if 'risk' in p_data:
                        st.warning(f"⚠️ **Risk:** {p_data['risk']}")

        st.divider()
        st.subheader("Master Trading Rules")
        for rule, desc in kb.get("trading_rules", {}).items():
            st.info(f"**{rule.replace('_', ' ').upper()}**: {desc}")

    with tab_greeks:
        st.subheader("Option Greeks Cheat Sheet")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Delta", "Speed", "Price Sensitivity")
    c2.metric("Gamma", "Acceleration", "Delta Sensitivity")
    c3.metric("Theta", "Time Decay", "Daily Erosion")
    c4.metric("Vega", "Volatility", "IV Sensitivity")

def render_strategy_builder():
    st.markdown("<div class='main-header'>Advanced Strategy Builder</div>", unsafe_allow_html=True)
    st.info("Build and upload your Python strategies. Changes are applied instantly.")

    # 1. Strategy List & Status
    st.session_state.strategy_manager.load_strategies()
    strategies = st.session_state.strategy_manager.strategies

    if not strategies:
        st.warning("No strategies found in nifty_engine/strategies/")
    else:
        for name, strategy in strategies.items():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"**{name}** (Symbol: {strategy.symbol}, Timeframe: {strategy.timeframe})")

            # Use DB status
            is_on = st.session_state.db.get_config(f"strategy_{name}", "OFF") == "ON"
            if is_on:
                if c2.button("STOP", key=f"stop_{name}", use_container_width=True):
                    st.session_state.strategy_manager.disable_strategy(name)
                    st.rerun()
            else:
                if c2.button("START", key=f"start_{name}", use_container_width=True, type="primary"):
                    st.session_state.strategy_manager.enable_strategy(name)
                    st.rerun()

            if c3.button("EDIT", key=f"edit_{name}", use_container_width=True):
                st.session_state.editing_strategy = name

    st.divider()

    # 2. Strategy Editor
    editing_name = st.session_state.get("editing_strategy")
    if editing_name and editing_name in strategies:
        st.subheader(f"Editing: {editing_name}")
        strategy = strategies[editing_name]
        filename = getattr(strategy, '_filename', 'unknown.py')
        filepath = os.path.join("nifty_engine/strategies", filename)

        with open(filepath, 'r') as f:
            code = f.read()

        new_code = st.text_area("Python Code", value=code, height=400)

        c_save, c_cancel = st.columns(2)
        if c_save.button("SAVE & RELOAD", type="primary", use_container_width=True):
            st.session_state.strategy_manager.update_strategy_code(editing_name, new_code)
            st.success(f"Strategy {editing_name} updated!")
            del st.session_state.editing_strategy
            st.rerun()
        if c_cancel.button("CANCEL", use_container_width=True):
            del st.session_state.editing_strategy
            st.rerun()
    else:
        st.subheader("Upload New Strategy")
        uploaded_file = st.file_uploader("Choose a Python file", type="py")
        if uploaded_file is not None:
            filename = uploaded_file.name
            save_path = os.path.join("nifty_engine/strategies", filename)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Strategy {filename} uploaded successfully!")
            st.session_state.strategy_manager.load_strategies()
            st.rerun()

def render_rules():
    st.markdown("<div class='main-header'>Market Rules Engine</div>", unsafe_allow_html=True)

    if st.button("🔄 Rapid Refresh Knowledge"):
        from nifty_engine.core.rules_engine import RulesEngine
        re = RulesEngine()
        if re.refresh_knowledge():
            st.success("Knowledge Base Refreshed successfully from source!")

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

def render_settings():
    st.markdown("<div class='main-header'>System Settings</div>", unsafe_allow_html=True)

    st.subheader("API Credentials")
    st.info("Credentials are managed via the .env file for security.")

    st.subheader("System Performance")
    st.write("Current Refresh Interval: 2 Minutes (Optimized for low storage impact)")

    st.subheader("Data Storage")
    db_path = "nifty_data.db"
    if os.path.exists(db_path):
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        st.write(f"Database Size: {size_mb:.2f} MB")
        if st.button("Cleanup Old Data"):
            st.warning("Feature coming soon: Auto-pruning old candle data.")

if __name__ == "__main__":
    main()
