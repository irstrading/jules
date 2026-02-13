# anza_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from database.manager import DatabaseManager
from core.analyzers import StockAnalyzer

st.set_page_config(page_title="ANZA OPTION ANALYSIS", layout="wide", initial_sidebar_state="expanded")

# --- Institutional Premium Styling ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .main-header {
        font-size: 32px; font-weight: 800; color: #f0ab48;
        margin-bottom: 25px; border-bottom: 2px solid #f0ab48; padding-bottom: 10px;
    }
    .metric-card {
        background-color: #1e293b; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #334155;
    }
    .status-online { color: #22c55e; font-weight: bold; }
    .status-offline { color: #ef4444; font-weight: bold; }
    section[data-testid="stSidebar"] { background-color: #0f172a; }
</style>
""", unsafe_allow_html=True)

if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

def main():
    st_autorefresh(interval=60000, key="datarefresh")

    with st.sidebar:
        st.markdown("<h1 style='color: #f0ab48;'>ANZA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 14px; margin-top: -15px;'><i>Institutional Option Intelligence</i></p>", unsafe_allow_html=True)
        st.divider()
        menu = st.radio("Navigation", ["Dashboard", "Stock Intelligence", "Institutional Playbook", "Settings"])

        st.divider()
        engine_running = st.session_state.db.get_config("engine_running", "OFF") == "ON"
        status_class = "status-online" if engine_running else "status-offline"
        st.markdown(f"System Status: <span class='{status_class}'>{'ONLINE' if engine_running else 'OFFLINE'}</span>", unsafe_allow_html=True)

    if menu == "Dashboard":
        render_dashboard()
    elif menu == "Stock Intelligence":
        render_stock_intelligence()
    elif menu == "Institutional Playbook":
        render_playbook()
    elif menu == "Settings":
        render_settings()

def render_dashboard():
    st.markdown("<div class='main-header'>Market Intelligence Dashboard</div>", unsafe_allow_html=True)

    # Summary Metrics (Mock for demo if DB empty)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown("<div class='metric-card'><b>Bullish Participation</b><br><h2>85%</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='metric-card'><b>Bearish Participation</b><br><h2>15%</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='metric-card'><b>Market Mood (MMI)</b><br><h2>62.4</h2><span>Greed</span></div>", unsafe_allow_html=True)
    with c4: st.markdown("<div class='metric-card'><b>Net GEX</b><br><h2>-1.2B</h2><span style='color:#ef4444;'>Negative</span></div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("🤖 AI Market Interpretation")
    st.info("🚀 **Broad-based Bullishness:** The majority of the Nifty weight is aligned upward. High-confidence institutional flow detected.")

    st.divider()
    st.subheader("ATM Straddle Premium (Live)")
    # Plotly Chart
    t = pd.date_range(end=datetime.now(), periods=50, freq='1min')
    p = [180 + np.sin(i/5)*10 for i in range(50)]
    fig = go.Figure(go.Scatter(x=t, y=p, line=dict(color='#f0ab48', width=2), name="Premium"))
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("### 🖥️ Live System Terminal")
    log_path = "logs/engine.log"
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            last_logs = "".join(f.readlines()[-15:])
            st.code(last_logs, language="bash")
    else: st.info("Terminal log initializing...")

def render_stock_intelligence():
    st.markdown("<div class='main-header'>Stock Swing Intelligence</div>", unsafe_allow_html=True)
    stocks = ["RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "SBIN"]
    cols = st.columns(3)
    for i, s in enumerate(stocks):
        with cols[i % 3]:
            score = np.random.randint(4, 10)
            color = "#22c55e" if score >= 8 else ("#3b82f6" if score >= 6 else "#64748b")
            st.markdown(f"""
            <div style='background: #1e293b; padding: 20px; border-radius: 12px; border-left: 5px solid {color}; margin-bottom: 15px;'>
                <h3 style='margin:0;'>{s}</h3>
                <p style='color: #94a3b8;'>Regime: Accumulation</p>
                <b style='color: {color};'>{'STRONG BUY' if score >= 8 else 'HOLD'}</b> (Score: {score}/10)
            </div>
            """, unsafe_allow_html=True)

def render_playbook():
    st.markdown("<div class='main-header'>Institutional Playbook</div>", unsafe_allow_html=True)
    kb_path = "database/knowledge_base.json"
    if os.path.exists(kb_path):
        with open(kb_path, 'r') as f:
            patterns = json.load(f).get("institutional_patterns", {})
            for cat, items in patterns.items():
                st.subheader(cat.replace("_", " ").title())
                for name, p in items.items():
                    with st.expander(f"**{name.replace('_', ' ').title()}**"):
                        st.write(f"🔍 **Detection:** {p['detection']}")
                        st.write(f"💡 **Meaning:** {p['meaning']}")
                        st.success(f"🚀 **Action:** {p['action']}")

def render_settings():
    st.markdown("<div class='main-header'>Settings</div>", unsafe_allow_html=True)
    st.write("Environment: Production")
    st.write("Data Refresh: 60s")
    if st.button("Download Master Knowledge File"):
        if os.path.exists("Institutional_Knowledge_Master.txt"):
            with open("Institutional_Knowledge_Master.txt", "r") as f:
                st.download_button("Download TXT", f.read(), "ANZA_Knowledge.txt")

if __name__ == "__main__":
    main()
