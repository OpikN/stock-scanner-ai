import csv
import os

FILE = "trades.csv"
START_EQUITY = 10000000  # 10 juta awal


# =========================
# LOAD TRADES
# =========================
def load_trades():
    if not os.path.exists(FILE):
        return []

    with open(FILE, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)


# =========================
# SAVE TRADE
# =========================
def save_trade(trade):
    file_exists = os.path.exists(FILE)

    with open(FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Stock", "Signal", "Entry", "Exit", "Lot", "PnL"
        ])

        if not file_exists:
            writer.writeheader()

        writer.writerow(trade)


# =========================
# PNL CALCULATION
# =========================
def calculate_pnl(entry, exit_price, signal, lot):
    if signal == "BUY":
        return (exit_price - entry) * lot

    elif signal == "SELL":
        return (entry - exit_price) * lot

    return 0


# =========================
# EQUITY
# =========================
def get_equity():
    trades = load_trades()

    equity = START_EQUITY

    for t in trades:
        equity += float(t["PnL"])

    return round(equity, 2)


# =========================
# PERFORMANCE
# =========================
def get_performance():
    trades = load_trades()

    if not trades:
        return "Trade: 0\nWin: 0 | Loss: 0\nWinrate: 0%"

    win = 0
    loss = 0

    for t in trades:
        pnl = float(t["PnL"])

        if pnl > 0:
            win += 1
        elif pnl < 0:
            loss += 1

    total = len(trades)
    winrate = (win / total) * 100 if total > 0 else 0

    return f"Trade: {total}\nWin: {win} | Loss: {loss}\nWinrate: {round(winrate,2)}%"


# =========================
# EXPECTANCY (FIXED)
# =========================
def get_expectancy(trades):
    if not trades or len(trades) == 0:
        return 0

    wins = []
    losses = []

    for t in trades:
        pnl = float(t["PnL"])

        if pnl > 0:
            wins.append(pnl)
        elif pnl < 0:
            losses.append(abs(pnl))

    total = len(trades)
    winrate = len(wins) / total
    lossrate = len(losses) / total

    avg_win = sum(wins) / len(wins) if wins else 0
    avg_loss = sum(losses) / len(losses) if losses else 0

    expectancy = (winrate * avg_win) - (lossrate * avg_loss)

    return round(expectancy, 2)


# =========================
# OPTIONAL: LOT CALCULATOR (fallback)
# =========================
def calculate_lot(price, sl, equity):
    risk_amount = equity * 0.02
    lot = int(risk_amount / abs(price - sl))

    if lot < 1:
        lot = 1

    return lot
