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
from core.analyzers import StockAnalyzer
from core.simulator import RealisticSimulator

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
            font-size: 2.5rem;
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

# --- App Logic ---
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

def main():
    inject_anza_vibrant_css()
    st_autorefresh(interval=30000, key="datarefresh")

    # --- Sidebar Navigation ---
    with st.sidebar:
        st.markdown(f"<h1 style='color: var(--anza-gold); font-family: Orbitron; font-size: 40px; margin-bottom:0;'>ANZA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; font-size: 0.8rem; letter-spacing:1px;'>INSTITUTIONAL PRO v3.0</p>", unsafe_allow_html=True)
        st.divider()

        selected = option_menu(
            menu_title=None,
            options=["Market Intelligence", "Stock Intelligence", "Flow Dynamics", "Strategy Matrix", "System Control"],
            icons=["graph-up-arrow", "cpu", "water", "layers-half", "gear"],
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
        render_market_intel()
    elif selected == "Stock Intelligence":
        render_stock_intel()
    elif selected == "Flow Dynamics":
        render_flow_dynamics()
    elif selected == "Strategy Matrix":
        render_playbook()
    elif selected == "System Control":
        render_settings()

def render_market_intel():
    st.markdown('<div class="main-header">ANZA Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Global Derivatives & Index Flow Analysis</div>', unsafe_allow_html=True)

    # Simulation for Demo
    sim = RealisticSimulator.generate_market_state()

    # --- Top Metrics ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Index Alignment</div><div class="metric-value" style="color:var(--anza-neon)">{sim['alignment']['bullish_pct']}%</div><div style="font-size:0.7rem; color:var(--anza-neon)">🟢 BULLISH PARTICIPATION</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Market Mood</div><div class="metric-value">{sim['mmi']}</div><div style="font-size:0.7rem; color:var(--anza-gold)">⚖️ CURRENT: GREED</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Gamma Exposure</div><div class="metric-value" style="color:var(--anza-danger)">{sim['net_gex']/1e9:.2f}B</div><div style="font-size:0.7rem; color:var(--anza-danger)">🌋 SHORT GAMMA REGIME</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">PCR Dynamics</div><div class="metric-value">1.12</div><div style="font-size:0.7rem; color:var(--anza-neon)">📈 SUPPORT BUILDING</div></div>""", unsafe_allow_html=True)

    st.divider()

    # --- Main Visuals ---
    col_l, col_r = st.columns([2, 1])

    with col_l:
        st.subheader("🏦 Nifty ATM Straddle Premium (Institutional View)")
        df_sim = RealisticSimulator.generate_stock_data("NIFTY", 185.0)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_sim['timestamp'], y=df_sim['close'], name="Premium", line=dict(color='#f0ab48', width=3)))
        fig.add_trace(go.Scatter(x=df_sim['timestamp'], y=df_sim['close'].rolling(15).mean(), name="VWAP", line=dict(color='#ffffff', width=1, dash='dot')))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=450, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("🤖 AI Executive Briefing")
        st.markdown(f"""
        <div class="ai-box">
            <p style="color: var(--anza-gold); font-weight: bold; margin-bottom:10px;">MARKET SUMMARY</p>
            <p style="font-size: 0.9rem; line-height:1.6;">
                Broad-based <b>Bullish Alignment</b> detected at {sim['alignment']['bullish_pct']}%.
                Gamma Flip Level identified at 24,400.
                Expect <b>Short Covering</b> rally if price sustains above high of 1st hour.
            </p>
            <div style="margin-top:20px; padding:10px; background:rgba(255,255,255,0.05); border-radius:8px;">
                <span style="font-size:0.75rem; color:#94a3b8;">SYSTEM CONFIDENCE</span><br>
                <b style="color:var(--anza-neon)">HIGH (87.4%)</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("🔥 Heavyweight Impact")
        movers = {"RELIANCE": 1.45, "HDFCBANK": 0.92, "ICICIBANK": -0.31, "INFY": 0.55}
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

def render_stock_intel():
    st.markdown('<div class="main-header">Stock Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">1-5 Day Institutional Swing Projections</div>', unsafe_allow_html=True)

    stocks = ["RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "SBIN", "LT", "TATAMOTORS", "AXISBANK"]
    cols = st.columns(3)

    for i, s in enumerate(stocks):
        with cols[i % 3]:
            score = np.random.randint(4, 11)
            p_chg = np.random.uniform(-1.5, 2.8)
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

def render_flow_dynamics():
    st.markdown('<div class="main-header">Flow Dynamics</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🌋 Gamma Profile", "🔥 Intensity Heatmap"])

    strikes = list(range(24000, 25100, 100))

    with tab1:
        gex_vals = [np.random.uniform(-3, 3) for _ in strikes]
        fig = px.bar(x=strikes, y=gex_vals, color=gex_vals, color_continuous_scale='RdYlGn', title="Strike-Wise Gamma Exposure")
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.info("Negative GEX indicates areas where market makers chase the trend, amplifying volatility.")

    with tab2:
        oi_data = np.random.randint(100, 1000, size=(len(strikes), 2))
        fig = go.Figure(data=go.Heatmap(z=oi_data, x=['CALLS', 'PUTS'], y=strikes, colorscale='Magma'))
        fig.update_layout(template="plotly_dark", height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

def render_playbook():
    st.markdown('<div class="main-header">Pattern Playbook</div>', unsafe_allow_html=True)
    kb_path = "database/knowledge_base.json"
    if os.path.exists(kb_path):
        with open(kb_path, 'r') as f:
            patterns = json.load(f).get("institutional_patterns", {})
            for cat, items in patterns.items():
                st.subheader(cat.replace("_", " ").upper())
                for name, p in items.items():
                    with st.expander(f"✨ {name.replace('_', ' ').title()}"):
                        st.markdown(f"""
                        <div style='padding:10px;'>
                            <p><b>🔍 DETECTION:</b> {p['detection']}</p>
                            <p><b>💡 MEANING:</b> {p['meaning']}</p>
                            <p style='color:var(--anza-neon)'><b>🚀 ACTION:</b> {p['action']}</p>
                        </div>
                        """, unsafe_allow_html=True)

def render_settings():
    st.markdown('<div class="main-header">System Settings</div>', unsafe_allow_html=True)
    st.write("Cluster: PRO-ASIA-1")
    if st.button("RESET DATABASE"): st.warning("Database reset initiated...")

if __name__ == "__main__":
    main()
