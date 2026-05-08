import streamlit as st
import pandas as pd
import json
import os
import importlib

from app.config import (
    DASHBOARD_TITLE,
    STRATEGY_PATH
)

# =========================
# FORCE RELOAD PORTFOLIO
# =========================

from app import portfolio

importlib.reload(portfolio)

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
# DEBUG MODULE
# =========================

st.write("MODULE FUNCTIONS:")

st.write(dir(portfolio))

# =========================
# LOAD DATA SAFE
# =========================

try:

    positions = portfolio.load_positions()

except Exception as e:

    st.error(
        f"LOAD POSITIONS ERROR: {e}"
    )

    positions = pd.DataFrame()

# =========================
# OPEN POSITIONS SAFE
# =========================

try:

    open_positions = portfolio.get_open_positions()

except Exception as e:

    st.error(
        f"OPEN POSITIONS ERROR: {e}"
    )

    open_positions = pd.DataFrame()

# =========================
# CLOSED POSITIONS SAFE
# =========================

try:

    closed_positions = portfolio.get_closed_positions()

except Exception as e:

    st.error(
        f"CLOSED POSITIONS ERROR: {e}"
    )

    closed_positions = pd.DataFrame()

# =========================
# EQUITY SAFE
# =========================

try:

    closed_equity = portfolio.get_closed_equity()

except Exception:

    closed_equity = 0

try:

    live_equity = portfolio.get_live_equity()

except Exception:

    live_equity = 0

floating = live_equity - closed_equity

# =========================
# DEBUG ROWS
# =========================

st.write(
    f"DEBUG ROWS: `{len(positions)}`"
)

# =========================
# ACCOUNT
# =========================

st.header("💰 Account")

col1, col2, col3 = st.columns(3)

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

st.write(
    "Mode: AGGRESSIVE"
)

st.write(
    "Market Regime: TRENDING"
)

# =========================
# STRATEGY
# =========================

st.header("🧠 AI Strategy")

if os.path.exists(
    STRATEGY_PATH
):

    try:

        with open(
            STRATEGY_PATH,
            "r"
        ) as f:

            strategy = json.load(f)

        st.json(strategy)

    except Exception as e:

        st.error(
            f"STRATEGY ERROR: {e}"
        )

else:

    st.warning(
        "Strategy file not found"
    )

# =========================
# BRAIN STATUS
# =========================

st.header(
    "🧠 AI Brain Status"
)

st.write(
    "Last Optimizer Run: Active"
)

# =========================
# RAW CSV
# =========================

st.header(
    "🛠 RAW CSV DATA"
)

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

st.header(
    "📂 All Positions"
)

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

st.header(
    "📡 Open Positions"
)

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

st.header(
    "📈 Closed PnL"
)

if closed_positions.empty:

    st.warning(
        "Belum ada CLOSED"
    )

else:

    try:

        total_closed = closed_positions[
            "pnl"
        ].sum()

    except Exception:

        total_closed = 0

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
