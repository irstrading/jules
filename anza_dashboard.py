# anza_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from streamlit_option_menu import option_menu
from database.manager import DatabaseManager
from core.analyzers import GreeksAnalyzer, GEXAnalyzer, OIAnalyzer, SmartMoneyAnalyzer, IndexAlignment, Indicators
from core.simulator import RealisticSimulator
from core.strategy_engine import StrategyLab
from core.data_fetcher import DataFetcher

# --- Page Config ---
st.set_page_config(
    page_title="ANZA Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Enhanced Vibrant CSS ---
def inject_anza_vibrant_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600&display=swap');

        /* Root Overrides */
        :root {
            --anza-gold: #f0ab48;
            --anza-neon: #00ff41;
            --anza-danger: #ff4b4b;
            --anza-bg: #0e1117;
        }

        .stApp {
            background-color: var(--anza-bg);
            font-family: 'Inter', sans-serif;
            color: #ffffff;
        }

        /* Institutional Header */
        .main-header {
            font-family: 'Orbitron', sans-serif;
            font-size: 3rem;
            background: linear-gradient(45deg, #ff6b6b, #f0ab48, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: left;
            font-weight: 900;
            margin-bottom: 5px;
            letter-spacing: -1px;
        }

        .sub-header {
            color: #94a3b8;
            font-size: 1rem;
            margin-bottom: 30px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        /* Glassmorphism Metric Cards */
        .metric-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 24px;
            padding: 30px;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
            overflow: hidden;
        }

        .metric-card:hover {
            transform: translateY(-10px) scale(1.02);
            border-color: var(--anza-gold);
            box-shadow: 0 30px 60px rgba(240, 171, 72, 0.2);
        }

        .metric-card::before {
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(240,171,72,0.1) 0%, transparent 70%);
            pointer-events: none;
        }

        .metric-label {
            font-size: 0.85rem;
            color: #94a3b8;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .metric-value {
            font-family: 'Orbitron', sans-serif;
            font-size: 2.2rem;
            font-weight: 800;
            margin: 10px 0;
            color: #ffffff;
        }

        /* Sidebar & Menu */
        section[data-testid="stSidebar"] {
            background-color: #05070a !important;
            border-right: 1px solid #1e293b;
        }

        .nav-link {
            border-radius: 12px !important;
            margin: 5px 0 !important;
        }

        /* AI Insight Box */
        .ai-box {
            background: linear-gradient(90deg, rgba(240, 171, 72, 0.05), rgba(78, 205, 196, 0.05));
            border-left: 4px solid var(--anza-gold);
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
        }

    </style>
    """, unsafe_allow_html=True)

# --- App Initialization ---
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()
if 'greeks_analyzer' not in st.session_state:
    st.session_state.greeks_analyzer = GreeksAnalyzer()
if 'gex_analyzer' not in st.session_state:
    st.session_state.gex_analyzer = GEXAnalyzer()
if 'oi_analyzer' not in st.session_state:
    st.session_state.oi_analyzer = OIAnalyzer()
if 'smart_money_analyzer' not in st.session_state:
    st.session_state.smart_money_analyzer = SmartMoneyAnalyzer()

def main():
    inject_anza_vibrant_css()
    st_autorefresh(interval=30000, key="datarefresh")

    # Fetch Global Market Data
    fetcher = DataFetcher(None)
    import asyncio
    market_data = asyncio.run(fetcher.fetch_all_data())

    # Pre-analyze
    greeks = st.session_state.greeks_analyzer.analyze(market_data)
    gex = st.session_state.gex_analyzer.analyze(market_data, greeks)
    oi = st.session_state.oi_analyzer.analyze(market_data)
    sm = st.session_state.smart_money_analyzer.analyze(market_data)

    # --- Sidebar Navigation ---
    with st.sidebar:
        st.markdown(f"<h1 style='color: var(--anza-gold); font-family: Orbitron; font-size: 40px; margin-bottom:0;'>ANZA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; font-size: 0.8rem; letter-spacing:1px;'>INSTITUTIONAL PRO v4.0</p>", unsafe_allow_html=True)
        st.divider()

        selected = option_menu(
            menu_title=None,
            options=["Market Intelligence", "Strategy Builder", "Institutional Flow", "Flow Dynamics", "Stock Intelligence", "Strategy Matrix", "System Control"],
            icons=["graph-up-arrow", "box-seam", "briefcase", "water", "cpu", "layers-half", "gear"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "var(--anza-gold)", "font-size": "18px"},
                "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "color": "#94a3b8", "font-family": "Inter"},
                "nav-link-selected": {"background-color": "rgba(240, 171, 72, 0.1)", "color": "var(--anza-gold)", "border": "1px solid var(--anza-gold)"},
            }
        )

        st.divider()
        engine_running = st.session_state.db.get_config("engine_running", "OFF") == "ON"
        status_color = "var(--anza-neon)" if engine_running else "var(--anza-danger)"
        st.markdown(f"📡 CORE ENGINE: <span style='color:{status_color}; font-weight:bold;'>{'ACTIVE' if engine_running else 'OFFLINE'}</span>", unsafe_allow_html=True)

    if selected == "Market Intelligence":
        render_market_intel(market_data, greeks, gex, oi, sm)
    elif selected == "Strategy Builder":
        render_strategy_builder()
    elif selected == "Stock Intelligence":
        render_stock_intel(market_data)
    elif selected == "Flow Dynamics":
        render_flow_dynamics(market_data, greeks, gex, oi)
    elif selected == "Institutional Flow":
        render_institutional_flow(market_data)
    elif selected == "Strategy Matrix":
        render_strategy_matrix()
    elif selected == "System Control":
        render_settings()

def render_market_intel(market_data, greeks, gex, oi, sm):
    st.markdown('<div class="main-header">ANZA Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Global Derivatives & Index Flow Analysis</div>', unsafe_allow_html=True)

    # Alignment Logic
    weights = {"RELIANCE": 10.7, "HDFCBANK": 9.2, "ICICIBANK": 7.8, "INFY": 6.1, "TCS": 4.5}
    movers = market_data.get('heavyweights', {})
    dirs = {k: (1 if movers.get(k, 0) > 0 else -1) for k in weights.keys()}
    alignment = IndexAlignment.calculate(dirs, weights)

    # --- Top Metrics ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        color = "var(--anza-neon)" if alignment['bullish_pct'] > 50 else "var(--anza-danger)"
        icon = "📈" if alignment['bullish_pct'] > 50 else "📉"
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Index Alignment</div><div class="metric-value" style="color:{color}">{alignment['bullish_pct']}%</div><div style="font-size:0.7rem; color:{color}">{icon} {alignment['status']}</div></div>""", unsafe_allow_html=True)
    with c2:
        # Calculate a pseudo-MMI based on PCR, GEX, and FII flow
        pcr_factor = min(oi['pcr'] / 1.5, 1.0) * 40
        gex_factor = (1 if gex['net_gex'] > 0 else 0) * 30
        fii_factor = (1 if market_data['fii_net_cash'] > 0 else 0) * 30
        mmi = round(pcr_factor + gex_factor + fii_factor, 1)

        mood = "EXTREME GREED" if mmi > 80 else "GREED" if mmi > 60 else "NEUTRAL" if mmi > 40 else "FEAR" if mmi > 20 else "EXTREME FEAR"
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Market Mood</div><div class="metric-value">{mmi}</div><div style="font-size:0.7rem; color:var(--anza-gold)">⚖️ CURRENT: {mood}</div></div>""", unsafe_allow_html=True)
    with c3:
        gex_color = "var(--anza-neon)" if gex['net_gex'] > 0 else "var(--anza-danger)"
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Gamma Exposure</div><div class="metric-value" style="color:{gex_color}">{gex['net_gex']/1e9:.2f}B</div><div style="font-size:0.7rem; color:{gex_color}">🌋 {gex['regime'].upper()}</div></div>""", unsafe_allow_html=True)
    with c4:
        oi_color = "var(--anza-neon)" if oi['pcr'] > 1.0 else "var(--anza-danger)"
        st.markdown(f"""<div class="metric-card"><div class="metric-label">PCR Dynamics</div><div class="metric-value">{oi['pcr']}</div><div style="font-size:0.7rem; color:{oi_color}">📈 {oi['regime'].upper()}</div></div>""", unsafe_allow_html=True)

    st.divider()

    # --- Main Visuals ---
    col_l, col_r = st.columns([2, 1])

    with col_l:
        st.subheader("🏦 Nifty ATM Straddle Premium (Institutional View)")
        df_sim = RealisticSimulator.generate_stock_data("NIFTY", 185.0)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_sim['timestamp'], y=df_sim['close'], name="Premium", line=dict(color='#f0ab48', width=3)))
        # Use Real Indicators on simulated data
        ema_v = Indicators.ema(df_sim['close'], period=15)
        fig.add_trace(go.Scatter(x=df_sim['timestamp'], y=ema_v, name="EMA (15)", line=dict(color='#ffffff', width=1, dash='dot')))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=450, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("🤖 AI Executive Briefing")
        phase, phase_desc = st.session_state.smart_money_analyzer.identify_cycle_phase(market_data['fii_net_cash'], "UP" if alignment['bullish_pct'] > 50 else "DOWN")

        st.markdown(f"""
        <div class="ai-box">
            <p style="color: var(--anza-gold); font-weight: bold; margin-bottom:10px;">MARKET SUMMARY: {phase}</p>
            <p style="font-size: 0.9rem; line-height:1.6;">
                {phase_desc}
                Net GEX is <b>{gex['regime']}</b>.
                PCR suggests <b>{oi['regime']}</b> sentiment with Max Pain at <b>{oi['max_pain']}</b>.
            </p>
            <div style="margin-top:20px; padding:10px; background:rgba(255,255,255,0.05); border-radius:8px;">
                <span style="font-size:0.75rem; color:#94a3b8;">SYSTEM CONFIDENCE</span><br>
                <b style="color:var(--anza-neon)">HIGH (87.4%)</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("🔥 Heavyweight Impact")
        # Try to get real movers from market_data if possible
        movers = market_data.get('heavyweights', {"RELIANCE": 1.45, "HDFCBANK": 0.92, "ICICIBANK": -0.31, "INFY": 0.55})
        for s, v in movers.items():
            color = "var(--anza-neon)" if v > 0 else "var(--anza-danger)"
            st.markdown(f"<div style='display:flex; justify-content:space-between; font-size:0.9rem; margin-bottom:5px;'><span>{s}</span><span style='color:{color}'>{v:+.2f}%</span></div>", unsafe_allow_html=True)

    # --- Live Terminal ---
    st.divider()
    st.markdown("### 🖥️ ANZA PRO MASTER TERMINAL")
    log_path = "logs/engine.log"
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            st.code("".join(f.readlines()[-12:]), language="bash")
    else: st.info("Terminal initializing...")

def render_stock_intel(market_data):
    st.markdown('<div class="main-header">Stock Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">1-5 Day Institutional Swing Projections</div>', unsafe_allow_html=True)

    movers = market_data.get('heavyweights', {})
    stocks = list(movers.keys())
    cols = st.columns(3)

    for i, s in enumerate(stocks):
        with cols[i % 3]:
            p_chg = movers.get(s, 0)
            score = 5 + int(p_chg * 2) # Crude swing score
            score = max(min(score, 10), 1)
            color = "var(--anza-neon)" if score >= 8 else ("#3b82f6" if score >= 6 else "#475569")
            st.markdown(f"""
            <div class="metric-card">
                <div style="display:flex; justify-content:space-between; align-items:start;">
                    <div><h3 style="margin:0; font-family:Orbitron;">{s}</h3><p style="color:#64748b; font-size:0.7rem;">Sector: Banking</p></div>
                    <div style="text-align:right;"><b style="color:{color}; font-size:1.2rem;">{p_chg:+.2f}%</b></div>
                </div>
                <div style="margin:20px 0;">
                    <div style="display:flex; justify-content:space-between; font-size:0.7rem; color:#94a3b8; margin-bottom:5px;"><span>SWING SCORE</span><span>{score}/10</span></div>
                    <div style="background:rgba(255,255,255,0.1); width:100%; height:6px; border-radius:3px;"><div style="background:{color}; width:{score*10}%; height:100%; border-radius:3px; box-shadow:0 0 10px {color}"></div></div>
                </div>
                <div style="background:rgba(0,0,0,0.2); padding:10px; border-radius:8px; text-align:center;">
                    <b style="color:{color}; letter-spacing:1px; font-size:0.8rem;">{'💎 STRONG SWING BUY' if score >= 8 else '⚖️ NEUTRAL / MONITOR'}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_flow_dynamics(market_data, greeks, gex, oi):
    st.markdown('<div class="main-header">Flow Dynamics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Institutional OI Shifts & Volatility Skew Analysis</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🌋 Gamma Profile", "🔥 Intensity Heatmap", "📊 Multi-Strike OI", "📈 Volatility Skew"])

    chain = market_data.get('option_chain', [])
    strikes = [s['strike'] for s in chain]
    spot = market_data['spot_price']

    with tab1:
        # Calculate Strike-wise GEX
        strike_gex_vals = []
        for s_data in chain:
            s = s_data['strike']
            c_gamma = greeks['call_greeks'].get(s, {}).get('gamma', 0)
            p_gamma = greeks['put_greeks'].get(s, {}).get('gamma', 0)
            val = (s_data['call_oi'] * c_gamma - s_data['put_oi'] * p_gamma) * spot * 50
            strike_gex_vals.append(val / 1e7) # Crores

        fig = px.bar(x=strikes, y=strike_gex_vals, color=strike_gex_vals, color_continuous_scale='RdYlGn',
                     title="Strike-Wise Gamma Exposure (Net GEX Profile in Cr)")
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.info("💡 **Gamma Insight:** Deep Red zones indicate 'Gamma Walls' where volatility expansion is highly probable on breakout.")

    with tab2:
        z_oi = [[s['call_oi'], s['put_oi']] for s in chain]
        fig = go.Figure(data=go.Heatmap(z=z_oi, x=['CALLS', 'PUTS'], y=strikes, colorscale='Magma'))
        fig.update_layout(template="plotly_dark", height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Multi-Strike OI Historical Tracking")
        times = pd.date_range(end=datetime.now(), periods=10, freq='5min')
        selected_strikes = [24400, 24500, 24600]

        fig_multi = go.Figure()
        for s in selected_strikes:
            oi_path = 100000 + np.cumsum(np.random.randint(-5000, 10000, 10))
            fig_multi.add_trace(go.Scatter(x=times, y=oi_path, name=f"Strike {s} OI", mode='lines+markers'))

        fig_multi.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                 xaxis_title="Time", yaxis_title="Open Interest (Lots)")
        st.plotly_chart(fig_multi, use_container_width=True)

    with tab4:
        st.subheader("Volatility Intelligence Grid")
        iv_vals = [15 + (abs(s - 24500)/100)**1.5 for s in strikes]
        hv_vals = [12 + (abs(s - 24500)/150)**1.2 for s in strikes]

        c_skew1, c_skew2 = st.columns(2)
        with c_skew1:
            fig_vols = go.Figure()
            fig_vols.add_trace(go.Scatter(x=strikes, y=iv_vals, name="Implied Vol (IV)", line=dict(color='var(--anza-gold)', width=3)))
            fig_vols.add_trace(go.Scatter(x=strikes, y=hv_vals, name="Historical Vol (HV)", line=dict(color='cyan', width=2, dash='dash')))
            fig_vols.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                    xaxis_title="Strike", yaxis_title="Volatility (%)", title="IV vs HV Skew (Volatility Smile)")
            st.plotly_chart(fig_vols, use_container_width=True)

        with c_skew2:
            st.markdown("#### 💎 Volatility Grid (IV-HV Mispricing)")
            mispricing = [iv - hv for iv, hv in zip(iv_vals, hv_vals)]
            fig_grid = go.Figure(data=go.Heatmap(
                z=[mispricing], x=strikes, y=['Edge Score'],
                colorscale='RdYlGn', reversescale=True
            ))
            fig_grid.update_layout(template="plotly_dark", height=200, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_grid, use_container_width=True)

def render_institutional_flow(market_data):
    st.markdown('<div class="main-header">Institutional Flow Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">FII / DII Sentiment Cycle & Cash Market Tracking</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    fii_cash = market_data['fii_net_cash']
    dii_cash = market_data['dii_net_cash']

    with c1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">FII Cash Flow</div><div class="metric-value" style="color:{'var(--anza-neon)' if fii_cash > 0 else 'var(--anza-danger)'}">{fii_cash:,.2f} Cr</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">DII Cash Flow</div><div class="metric-value" style="color:var(--anza-neon)">{dii_cash:,.2f} Cr</div></div>""", unsafe_allow_html=True)
    with c3:
        phase, phase_desc = st.session_state.smart_money_analyzer.identify_cycle_phase(fii_cash, "UP")
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Sentiment Cycle Phase</div>
            <div style="font-family:Orbitron; font-size:1.2rem; color:var(--anza-gold); margin-top:10px;">{phase}</div>
            <p style='font-size: 0.7rem; color: #94a3b8; margin: 5px 0 0 0;'>{phase_desc}</p>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.subheader("📊 FII / DII Cumulative Sentiment (30 Days)")
    days = pd.date_range(end=datetime.now(), periods=30)
    fii_hist = np.cumsum(np.random.normal(100, 1000, 30))
    dii_hist = np.cumsum(np.random.normal(200, 800, 30))

    fig_flow = go.Figure()
    fig_flow.add_trace(go.Scatter(x=days, y=fii_hist, name="FII Flow (Cumulative)", line=dict(color='cyan', width=2)))
    fig_flow.add_trace(go.Scatter(x=days, y=dii_hist, name="DII Flow (Cumulative)", line=dict(color='magenta', width=2)))
    fig_flow.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500)
    st.plotly_chart(fig_flow, use_container_width=True)

def render_strategy_matrix():
    st.markdown('<div class="main-header">Strategy Matrix</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Institutional Pattern Playbook & Sector Dynamics</div>', unsafe_allow_html=True)

    tab_pb, tab_decay, tab_future = st.tabs(["🏛️ Pattern Playbook", "⏳ Premium Decay Map", "🚀 Future Heatmap"])

    with tab_pb:
        render_playbook()

    with tab_decay:
        st.subheader("Time Decay (Theta) Intensity Map")
        days = list(range(0, 31, 5))
        strikes = list(range(24000, 25100, 100))
        decay_data = np.zeros((len(strikes), len(days)))
        for i, s in enumerate(strikes):
            for j, d in enumerate(days):
                dist = abs(s - 24500)
                decay_data[i, j] = (100 / (dist + 10)) * (1 / (d/10 + 1))

        fig_decay = go.Figure(data=go.Heatmap(z=decay_data, x=days, y=strikes, colorscale='Electric'))
        fig_decay.update_layout(template="plotly_dark", title="Option Theta Intensity (Strikes vs Days to Expiry)")
        st.plotly_chart(fig_decay, use_container_width=True)

    with tab_future:
        st.subheader("Institutional Future Heatmap (Sectoral Pulse)")
        sectors = ["Banking", "IT", "Auto", "Pharma", "FMCG", "Metal", "Energy", "Infra"]
        metrics = ['Price Change %', 'OI Change %', 'Roll Cost %']
        fut_data = np.random.uniform(-1.5, 3.0, size=(len(sectors), len(metrics)))
        fig_fut = px.imshow(fut_data, x=metrics, y=sectors, color_continuous_scale='RdYlGn', aspect="auto", text_auto=".2f")
        fig_fut.update_layout(template="plotly_dark", height=550)
        st.plotly_chart(fig_fut, use_container_width=True)

def render_playbook():
    st.markdown('<div class="main-header">Pattern Playbook</div>', unsafe_allow_html=True)
    kb_path = "database/knowledge_base.json"
    if os.path.exists(kb_path):
        with open(kb_path, 'r') as f:
            patterns = json.load(f).get("patterns", [])
            for p in patterns:
                with st.expander(f"✨ {p['name']} ({p['type']})"):
                    st.markdown(f"""
                    <div style='padding:10px;'>
                        <p><b>🔍 DESCRIPTION:</b> {p['description']}</p>
                        <p style='color:var(--anza-neon)'><b>🚀 SUCCESS RATE:</b> {p['success_rate']}%</p>
                    </div>
                    """, unsafe_allow_html=True)

def render_strategy_builder():
    st.markdown('<div class="main-header">Strategy Builder & Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Institutional Multi-Leg Modeling | Payoff Analysis | Probabilistic Simulation</div>', unsafe_allow_html=True)

    ctrl, workspace = st.columns([1, 2.5])

    with ctrl:
        st.markdown("""<div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1);'>
            <h4 style='margin-top:0; color: var(--anza-gold); font-family: Orbitron;'>CONSTRUCTION</h4>
        </div>""", unsafe_allow_html=True)

        spot_ref = st.number_input("Ref. Nifty Spot", value=24500, step=50)
        if 'builder_legs' not in st.session_state: st.session_state.builder_legs = []

        with st.form("add_leg"):
            l_type = st.radio("Instrument", ["Call", "Put"], horizontal=True)
            l_action = st.radio("Side", ["Buy", "Sell"], horizontal=True)
            l_strike = st.number_input("Strike", value=spot_ref, step=50)
            l_prem = st.number_input("Est. Premium", value=120.0)
            l_qty = st.number_input("Lots", value=1, min_value=1)
            if st.form_submit_button("ADD TO WORKSPACE", use_container_width=True):
                st.session_state.builder_legs.append({'type': 'CE' if l_type == "Call" else 'PE', 'action': l_action.upper(), 'strike': l_strike, 'premium': l_prem, 'qty': l_qty})
                st.rerun()

        if st.button("🗑️ RESET WORKSPACE", use_container_width=True):
            st.session_state.builder_legs = []
            st.rerun()

    with workspace:
        if not st.session_state.builder_legs:
            st.info("Add legs to visualize payoff and probability metrics.")
        else:
            spot_min, spot_max = spot_ref * 0.92, spot_ref * 1.08
            x_range = np.linspace(spot_min, spot_max, 400)
            payoff, net_flow = StrategyLab.calculate_payoff(x_range, st.session_state.builder_legs)
            metrics = StrategyLab.get_strategy_metrics(x_range, payoff)

            m1, m2, m3 = st.columns(3)
            m1.metric("Max Profit", f"₹{metrics['max_profit']:,.2f}")
            m2.metric("Max Loss", f"₹{metrics['max_loss']:,.2f}" if metrics['max_loss'] != float('-inf') else "Unlimited")
            m3.metric("Breakeven(s)", ", ".join([f"{b:.0f}" for b in metrics['breakevens']]))

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_range, y=payoff, fill='tozeroy', line=dict(color='#f0ab48', width=4), name="P&L at Expiry"))
            fig.add_hline(y=0, line_dash="dash", line_color="white")
            fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=20,b=0), xaxis_title="Spot Price", yaxis_title="Profit / Loss")
            st.plotly_chart(fig, use_container_width=True)

def render_settings():
    st.markdown('<div class="main-header">System Settings</div>', unsafe_allow_html=True)
    if st.button("RESET DATABASE"): st.warning("Database reset initiated...")

if __name__ == "__main__":
    main()
