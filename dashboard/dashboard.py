import streamlit as st

from streamlit_autorefresh import (
    st_autorefresh
)

import pandas as pd
import json
import os

from app.config import (
    DASHBOARD_TITLE,
    STRATEGY_PATH,
    POSITIONS_PATH,
    INITIAL_BALANCE
)

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="AI Trading Terminal",
    layout="wide"
)

# =========================
# AUTO REFRESH
# =========================

st_autorefresh(

    interval=5000,

    key="live_dashboard"
)

# =========================
# TITLE
# =========================

st.title(
    DASHBOARD_TITLE
)

# =========================
# LOAD CSV
# =========================

try:

    positions = pd.read_csv(
        POSITIONS_PATH
    )

except Exception:

    positions = pd.DataFrame()

# =========================
# OPEN / CLOSED POSITIONS
# =========================

if positions.empty:

    open_positions = pd.DataFrame()

    closed_positions = pd.DataFrame()

else:

    try:

        open_positions = positions[
            positions["status"] == "OPEN"
        ]

    except Exception:

        open_positions = pd.DataFrame()

    try:

        closed_positions = positions[
            positions["status"] == "CLOSED"
        ]

    except Exception:

        closed_positions = pd.DataFrame()

# =========================
# CALCULATE PNL
# =========================

try:

    closed_pnl = closed_positions[
        "pnl"
    ].sum()

except Exception:

    closed_pnl = 0

try:

    floating_pnl = open_positions[
        "pnl"
    ].sum()

except Exception:

    floating_pnl = 0

closed_equity = (
    INITIAL_BALANCE + closed_pnl
)

live_equity = (
    closed_equity + floating_pnl
)

# =========================
# DEBUG
# =========================

st.write(
    f"DEBUG ROWS: `{len(positions)}`"
)

# =========================
# ACCOUNT
# =========================

st.header(
    "💰 Account"
)

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
        f"{floating_pnl:,.0f}"
    )

# =========================
# AI MODE
# =========================

st.header(
    "🧠 AI Mode"
)

st.write(
    "Mode: AGGRESSIVE"
)

st.write(
    "Market Regime: TRENDING"
)

# =========================
# STRATEGY
# =========================

st.header(
    "🧠 AI Strategy"
)

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

st.success(
    f"TOTAL CLOSED PNL: {closed_pnl:,.0f}"
)

if not closed_positions.empty:

    st.dataframe(
        closed_positions
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
# FOOTER
# =========================

st.success(
    "🔥 REAL MARKET REGIME AI ACTIVE"
)
