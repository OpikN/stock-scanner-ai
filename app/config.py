import os

# =========================
# MARKET CONFIG
# =========================
STOCKS = ["BBCA.JK", "BBRI.JK", "TLKM.JK"]

# =========================
# FILE PATH
# =========================
DATA_PATH = os.getenv("DATA_PATH", "data/trades.csv")

# =========================
# TELEGRAM
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# =========================
# TRADING MODE
# =========================
MODE = os.getenv("MODE", "SAFE")  # SAFE / AGGRESSIVE

# =========================
# MONEY MANAGEMENT 🔥
# =========================
INITIAL_BALANCE = 10_000_000   # modal awal (10 juta)
RISK_PERCENT = 0.02            # 2% risk per trade
MAX_LOT = 1000                 # batas maksimal lot
