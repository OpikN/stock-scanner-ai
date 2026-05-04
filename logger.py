import pandas as pd
import os
from datetime import datetime

LOG_FILE = "log.csv"

def save_log(data):
    df = pd.DataFrame(data)

    df["date"] = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists(LOG_FILE):
        old = pd.read_csv(LOG_FILE)
        df = pd.concat([old, df], ignore_index=True)

    df.to_csv(LOG_FILE, index=False)


def get_stats():
    if not os.path.exists(LOG_FILE):
        return "Belum ada data"

    df = pd.read_csv(LOG_FILE)

    total = len(df)
    buy = len(df[df["Signal"] == "BUY"])
    sell = len(df[df["Signal"] == "SELL"])

    return f"Total: {total} | BUY: {buy} | SELL: {sell}"
