import pandas as pd
import os

TRADES_FILE = "trades.csv"
START_CAPITAL = 10_000_000

def save_trade(data):
    df = pd.DataFrame([data])

    if os.path.exists(TRADES_FILE):
        old = pd.read_csv(TRADES_FILE)
        df = pd.concat([old, df], ignore_index=True)

    df.to_csv(TRADES_FILE, index=False)


def calculate_pnl(entry, exit_price, signal, lot):
    if signal == "BUY":
        return (exit_price - entry) * lot * 100
    elif signal == "SELL":
        return (entry - exit_price) * lot * 100
    return 0


def get_equity():
    if not os.path.exists(TRADES_FILE):
        return START_CAPITAL

    df = pd.read_csv(TRADES_FILE)
    return START_CAPITAL + df["PnL"].sum()


def get_performance():
    if not os.path.exists(TRADES_FILE):
        return "Belum ada trade"

    df = pd.read_csv(TRADES_FILE)

    total = len(df)
    win = len(df[df["PnL"] > 0])
    loss = len(df[df["PnL"] <= 0])

    winrate = (win / total) * 100 if total > 0 else 0
    equity = START_CAPITAL + df["PnL"].sum()

    return f"""
Trade: {total}
Win: {win} | Loss: {loss}
Winrate: {round(winrate,2)}%
Equity: {int(equity)}
"""
