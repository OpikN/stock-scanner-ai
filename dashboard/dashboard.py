import streamlit as st
import pandas as pd
import json
import os

from app.config import (
    DASHBOARD_TITLE,
    STRATEGY_PATH
)

import app.portfolio as portfolio

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="AI Trading Terminal",
    layout="wide"
)

# =========================
# TITLE
# =========================

st.title(DASHBOARD_TITLE)

# =========================
# LOAD DATA
# =========================

positions = portfolio.load_positions()

open_positions = portfolio.get_open_positions()

closed_positions = portfolio.get_closed_positions()

# =========================
# DEBUG
# =========================

st.write(
    f"DEBUG ROWS: `{len(positions)}`"
)

# =========================
# ACCOUNT
# =========================

st.header("💰 Account")

col1, col2, col3 = st.columns(3)

closed_equity = portfolio.get_closed_equity()

live_equity = portfolio.get_live_equity()

floating = live_equity - closed_equity

with col1:

    st.metric(
        "Closed Equity",
        f"{closed_equity:,.0f}"
    )

with col2:

    st.metric(
        "Live Equity",
        f"{live_equity:,.0f}"
    )

with col3:

    st.metric(
        "Floating PnL",
        f"{floating:,.0f}"
    )

# =========================
# AI MODE
# =========================

st.header("🧠 AI Mode")

st.write("Mode: AGGRESSIVE")

st.write("Market Regime: TRENDING")

# =========================
# STRATEGY
# =========================

st.header("🧠 AI Strategy")

if os.path.exists(STRATEGY_PATH):

    with open(
        STRATEGY_PATH,
        "r"
    ) as f:

        strategy = json.load(f)

    st.json(strategy)

else:

    st.warning(
        "Strategy file not found"
    )

# =========================
# BRAIN STATUS
# =========================

st.header("🧠 AI Brain Status")

st.write(
    "Last Optimizer Run: Active"
)

# =========================
# RAW CSV
# =========================

st.header("🛠 RAW CSV DATA")

if positions.empty:

    st.warning(
        "DATAFRAME KOSONG"
    )

else:

    st.dataframe(
        positions
    )

# =========================
# ALL POSITIONS
# =========================

st.header("📂 All Positions")

if positions.empty:

    st.info(
        "Tidak ada posisi"
    )

else:

    st.dataframe(
        positions
    )

# =========================
# OPEN POSITIONS
# =========================

st.header("📡 Open Positions")

st.write(
    f"OPEN ROWS: `{len(open_positions)}`"
)

if open_positions.empty:

    st.warning(
        "Tidak ada posisi OPEN"
    )

else:

    st.dataframe(
        open_positions
    )

# =========================
# CLOSED PNL
# =========================

st.header("📈 Closed PnL")

if closed_positions.empty:

    st.warning(
        "Belum ada CLOSED"
    )

else:

    total_closed = closed_positions[
        "pnl"
    ].sum()

    st.success(
        f"TOTAL CLOSED PNL: {total_closed:,.0f}"
    )

    st.dataframe(
        closed_positions
    )

# =========================
# FOOTER
# =========================

st.success(
    "🔥 REAL MARKET REGIME AI ACTIVE"
)
