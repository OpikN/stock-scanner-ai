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
INITIAL_BALANCE = 10_000_000   # modal awal
RISK_PERCENT = 0.02            # 2% risk per trade
MAX_LOT = 1000                 # batas maksimal lot

# =========================
# ADVANCED RISK 🔥
# =========================
BREAK_EVEN_RR = 1.0       # pindah ke BE saat RR 1:1
TRAILING_START_RR = 1.5   # mulai trailing saat profit 1.5R
TRAILING_STEP = 0.5       # jarak trailing (R)
