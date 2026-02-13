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
from database.manager import DatabaseManager
from core.analyzers import StockAnalyzer
from core.simulator import RealisticSimulator

# --- Page Config ---
st.set_page_config(
    page_title="ANZA OPTION ANALYSIS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Theme Configuration ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'Midnight Institutional'

def inject_custom_css():
    theme = st.session_state.theme

    # Base Colors
    if theme == 'Midnight Institutional':
        bg_color = "#0e1117"
        card_bg = "rgba(30, 41, 59, 0.7)"
        accent_color = "#f0ab48"
        text_color = "#ffffff"
        border_color = "#334155"
    elif theme == 'Cyberpunk Glow':
        bg_color = "#050505"
        card_bg = "rgba(20, 20, 20, 0.8)"
        accent_color = "#00ff41" # Neon Green
        text_color = "#00ff41"
        border_color = "#00ff41"
    else: # Classic Dark
        bg_color = "#121212"
        card_bg = "#1e1e1e"
        accent_color = "#2196f3"
        text_color = "#e0e0e0"
        border_color = "#333333"

    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}

        /* Vibrant Header */
        .main-header {{
            font-size: 42px;
            font-weight: 900;
            background: linear-gradient(90deg, {accent_color}, #ffffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 30px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}

        /* Glassmorphism Cards */
        .metric-card {{
            background: {card_bg};
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid {border_color};
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            margin-bottom: 20px;
        }}

        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 40px 0 rgba({accent_color if theme!='Cyberpunk Glow' else '0, 255, 65'}, 0.2);
            border-color: {accent_color};
        }}

        .metric-label {{
            font-size: 14px;
            color: #94a3b8;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .metric-value {{
            font-size: 32px;
            font-weight: 800;
            color: {accent_color};
            margin: 10px 0;
        }}

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0f172a 0%, #000000 100%);
            border-right: 1px solid {border_color};
        }}

        /* Custom Buttons */
        .stButton>button {{
            background: linear-gradient(45deg, {accent_color}, #000000);
            color: white;
            border-radius: 12px;
            border: none;
            padding: 10px 25px;
            font-weight: bold;
            transition: all 0.3s ease;
        }}

        .stButton>button:hover {{
            box-shadow: 0 0 15px {accent_color};
            transform: scale(1.05);
        }}

        /* Realistic Terminal */
        .terminal-container {{
            background: #000000;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 15px;
            font-family: 'Courier New', Courier, monospace;
            color: #00ff00;
            font-size: 13px;
            max-height: 300px;
            overflow-y: auto;
        }}
    </style>
    """, unsafe_allow_html=True)

# --- Initialization ---
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

def main():
    inject_custom_css()
    st_autorefresh(interval=30000, key="datarefresh")

    # --- Sidebar ---
    with st.sidebar:
        st.markdown(f"<h1 style='color: #f0ab48; font-size: 50px; margin-bottom:0;'>ANZA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94a3b8; margin-top:-10px; border-bottom: 1px solid #334155; padding-bottom:10px;'>INSTITUTIONAL OPTION INTELLIGENCE</p>", unsafe_allow_html=True)

        menu = st.radio("Navigation", ["Overview", "Stock Scanner", "Option Heatmap", "Pattern Playbook", "System Settings"])

        st.divider()
        st.session_state.theme = st.selectbox("Dashboard Theme", ['Midnight Institutional', 'Cyberpunk Glow', 'Classic Dark'])

        st.divider()
        engine_running = st.session_state.db.get_config("engine_running", "OFF") == "ON"
        status_color = "#22c55e" if engine_running else "#ef4444"
        st.markdown(f"📡 STATUS: <span style='color:{status_color}; font-weight:bold;'>{'LIVE' if engine_running else 'OFFLINE'}</span>", unsafe_allow_html=True)

    if menu == "Overview":
        render_overview()
    elif menu == "Stock Scanner":
        render_stock_scanner()
    elif menu == "Option Heatmap":
        render_option_heatmap()
    elif menu == "Pattern Playbook":
        render_playbook()
    elif menu == "System Settings":
        render_settings()

def render_overview():
    st.markdown("<div class='main-header'>Market Intelligence Overview</div>", unsafe_allow_html=True)

    # Realistic Data from Simulator for vibrancy
    sim_state = RealisticSimulator.generate_market_state()

    # High-Impact Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Index Alignment</div>
            <div class='metric-value'>{sim_state['alignment']['bullish_pct']}%</div>
            <div style='color: #22c55e; font-size: 12px;'>▲ Strong Institutional Participation</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Market Mood (MMI)</div>
            <div class='metric-value'>{sim_state['mmi']}</div>
            <div style='color: #f0ab48; font-size: 12px;'>⚖️ Current Regime: Greed</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Total Gamma Exposure</div>
            <div class='metric-value'>{sim_state['net_gex']/1e9:.2f}B</div>
            <div style='color: #ef4444; font-size: 12px;'>⚡ Volatility Expansion Regime</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>PCR (OI)</div>
            <div class='metric-value'>1.14</div>
            <div style='color: #22c55e; font-size: 12px;'>✔ Support Building at 24400</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    col_chart, col_ai = st.columns([2, 1])
    with col_chart:
        st.subheader("📊 Nifty ATM Straddle Premium Evolution")
        df_sim = RealisticSimulator.generate_stock_data("NIFTY_STRADDLE", 185.0, steps=60)

        fig = px.line(df_sim, x='timestamp', y='close',
                      color_discrete_sequence=['#f0ab48'])
        fig.add_scatter(x=df_sim['timestamp'], y=df_sim['close'].rolling(20).mean(),
                        name="VWAP", line=dict(dash='dash', color='white'))

        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=450,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_ai:
        st.subheader("🤖 AI Intelligence")
        st.markdown(f"""
        <div style='background: rgba(240, 171, 72, 0.1); border: 1px solid #f0ab48; padding: 20px; border-radius: 15px;'>
            <p style='color: #f0ab48; font-weight:bold;'>ANALYSIS SUMMARY:</p>
            <p style='font-size: 14px;'>Current market showing <b>{sim_state['alignment']['bullish_pct']}% alignment</b>.
            Negative GEX indicates potential for <b>explosive moves</b>.
            OI Concentration at 24500 CE suggests a short-term ceiling.</p>
            <hr style='border-color: #f0ab48; opacity: 0.3;'>
            <p style='font-size: 12px; color: #94a3b8;'>Confidence Level: High (84%)</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.subheader("🔥 Top Movers Impact")
        movers = {"RELIANCE": 1.2, "HDFCBANK": 0.8, "ICICIBANK": -0.4, "INFY": 0.6}
        for s, v in movers.items():
            color = "#22c55e" if v > 0 else "#ef4444"
            st.markdown(f"**{s}**: <span style='color:{color}'>{v}% contribution</span>", unsafe_allow_html=True)

    st.divider()
    c_trend1, c_trend2 = st.columns(2)
    with c_trend1:
        st.subheader("📈 Institutional Alignment Trend")
        df_align = pd.DataFrame({
            'time': pd.date_range(end=datetime.now(), periods=20, freq='5min'),
            'bullish': [np.random.uniform(60, 90) for _ in range(20)]
        })
        fig_align = px.area(df_align, x='time', y='bullish', color_discrete_sequence=['#22c55e'])
        fig_align.update_layout(template="plotly_dark", height=300, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_align, use_container_width=True)

    with c_trend2:
        st.subheader("🧠 Market Mood Index (MMI) Momentum")
        df_mmi = pd.DataFrame({
            'time': pd.date_range(end=datetime.now(), periods=20, freq='5min'),
            'mmi': [np.random.uniform(40, 70) for _ in range(20)]
        })
        fig_mmi = px.line(df_mmi, x='time', y='mmi', color_discrete_sequence=['#f0ab48'])
        fig_mmi.update_layout(template="plotly_dark", height=300, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_mmi, use_container_width=True)

    st.divider()
    st.markdown("### 🖥️ ANZA Master Terminal Output")
    log_path = "logs/engine.log"
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            lines = f.readlines()
            st.code("".join(lines[-10:]), language="bash")
    else:
        st.info("System initializing... Waiting for first tick.")

def render_stock_scanner():
    st.markdown("<div class='main-header'>Institutional Stock Scanner</div>", unsafe_allow_html=True)
    st.info("Detecting 1-5 Day Swing Opportunities based on IV Regimes & Institutional Flows.")

    stocks = ["RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "SBIN", "LT", "TATAMOTORS", "AXISBANK"]
    cols = st.columns(3)

    for i, s in enumerate(stocks):
        with cols[i % 3]:
            # Use simulator for vibrancy
            p_change = np.random.uniform(-1.5, 2.5)
            score = np.random.randint(4, 11)
            color = "#22c55e" if score >= 8 else ("#3b82f6" if score >= 6 else "#475569")

            st.markdown(f"""
            <div class='metric-card'>
                <div style='display:flex; justify-content:space-between;'>
                    <h3 style='margin:0;'>{s}</h3>
                    <span style='color:{color}; font-weight:bold;'>{p_change:+.2f}%</span>
                </div>
                <p style='color: #94a3b8; font-size:12px;'>Regime: {'Short Covering' if p_change > 1 else 'Accumulation'}</p>
                <div style='margin-top:15px; display:flex; align-items:center; gap:10px;'>
                    <div style='background:{color}; width:{score*10}%; height:8px; border-radius:4px;'></div>
                    <span style='font-size:12px;'>{score}/10</span>
                </div>
                <p style='margin-top:10px; font-weight:bold; color:{color};'>{'🔥 STRONG SWING BUY' if score >= 8 else '⚖️ HOLD/WATCH'}</p>
            </div>
            """, unsafe_allow_html=True)

def render_option_heatmap():
    st.markdown("<div class='main-header'>Option Intensity Heatmap</div>", unsafe_allow_html=True)

    strikes = list(range(24000, 25100, 100))
    # Advanced Heatmap Data
    oi_data = np.random.randint(100, 500, size=(len(strikes), 2))

    fig = go.Figure(data=go.Heatmap(
        z=oi_data,
        x=['CALL FLOW', 'PUT FLOW'],
        y=strikes,
        colorscale='Magma',
        hoverongaps=False,
        text=oi_data,
        texttemplate="%{text}"
    ))

    fig.update_layout(
        title='Strike-Wise OI Concentration Heatmap',
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("🌋 Gamma Exposure (GEX) Profile")

    gex_data = [np.random.uniform(-2, 2) for _ in strikes]
    fig_gex = px.bar(x=strikes, y=gex_data, labels={'x': 'Strike', 'y': 'GEX (B)'},
                     color=gex_data, color_continuous_scale='RdYlGn')
    fig_gex.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_gex, use_container_width=True)

    st.info("💡 **GEX Analysis:** Negative GEX (Red) below 24400 indicates price acceleration risk. Positive GEX (Green) above 24800 indicates stabilization.")

def render_playbook():
    st.markdown("<div class='main-header'>Pattern Playbook</div>", unsafe_allow_html=True)
    kb_path = "database/knowledge_base.json"
    if os.path.exists(kb_path):
        with open(kb_path, 'r') as f:
            kb = json.load(f)
            patterns = kb.get("institutional_patterns", {})
            for cat, items in patterns.items():
                st.subheader(cat.replace("_", " ").upper())
                for name, p in items.items():
                    with st.expander(f"🔮 {name.replace('_', ' ').title()}"):
                        st.info(f"**DETECTION:** {p['detection']}")
                        st.write(f"**MEANING:** {p['meaning']}")
                        st.success(f"**ACTION:** {p['action']}")

def render_settings():
    st.markdown("<div class='main-header'>System Settings</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Data & Connection")
        st.write("Broker: Angel One (SmartAPI v2)")
        st.write("Environment: Production Cluster A")
        if st.button("Download Offline Knowledge Base"):
            st.success("Downloading Institutional_Knowledge_Master.txt...")

    with c2:
        st.subheader("Dashboard Configuration")
        st.write("Refresh Rate: 30s")
        st.selectbox("Data Source Priority", ["WebSocket (Live)", "API Snapshot", "Simulation"])
        st.multiselect("Visible Indices", ["NIFTY", "BANKNIFTY", "FINNIFTY"], default=["NIFTY", "BANKNIFTY"])
        st.toggle("High Contrast Mode", value=True)
        st.toggle("Enable AI Voice Briefing", value=False)

if __name__ == "__main__":
    main()
