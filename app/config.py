import os

STOCKS = ["BBCA.JK", "BBRI.JK", "TLKM.JK"]

DATA_PATH = os.getenv("DATA_PATH", "data/trades.csv")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

MODE = os.getenv("MODE", "SAFE")  # SAFE / AGGRESSIVE
