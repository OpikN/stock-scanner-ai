import os

# =========================
# STOCK LIST
# =========================
STOCKS = [
    "BBCA.JK",
    "BBRI.JK",
    "TLKM.JK"
]

# =========================
# ACCOUNT
# =========================
INITIAL_BALANCE = 100_000_000

# =========================
# RISK MANAGEMENT
# =========================
RISK_SAFE = 0.01

RISK_AGGRESSIVE = 0.03

# =========================
# TRADE LIMIT
# =========================
MAX_OPEN_POSITIONS = 5

MIN_TRADE_SIZE = 100_000

# =========================
# STOP LOSS / TAKE PROFIT
# =========================
SL_PERCENT = 0.02

TP1_PERCENT = 0.02

TP2_PERCENT = 0.04

BREAK_EVEN_TRIGGER = 0.015

TRAILING_PERCENT = 0.01

PARTIAL_CLOSE_RATIO = 0.5

# =========================
# DATA PATH
# =========================
DATA_PATH = "data/trades.csv"

POSITIONS_PATH = "data/positions.csv"

STRATEGY_PATH = "data/strategy.json"

# =========================
# TELEGRAM
# =========================
TELEGRAM_TOKEN = os.getenv(
    "TELEGRAM_TOKEN"
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID"
)

# =========================
# AI ENGINE
# =========================
AI_MODE = "AUTO"

ENABLE_TRAILING = True

ENABLE_BREAK_EVEN = True

ENABLE_PARTIAL_CLOSE = True

ENABLE_AI_CONFIDENCE = True

ENABLE_MARKET_REGIME = True

ENABLE_TRADE_RANKING = True

# =========================
# AI CONFIDENCE FILTER
# =========================
MIN_CONFIDENCE = 70

# =========================
# MAX AI TRADE
# =========================
MAX_TOP_TRADES = 2

# =========================
# DASHBOARD
# =========================
DASHBOARD_TITLE = (
    "📊 AI TRADING TERMINAL"
)
