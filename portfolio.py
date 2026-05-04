import csv
import os

FILE = "trades.csv"
START_EQUITY = 10000000


# ===== LOAD =====
def load_trades():
    if not os.path.exists(FILE):
        return []

    trades = []
    with open(FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                trades.append({
                    "Stock": row["Stock"],
                    "Signal": row["Signal"],
                    "Entry": float(row["Entry"]),
                    "Exit": float(row["Exit"]),
                    "Lot": int(row["Lot"]),
                    "PnL": float(row["PnL"])
                })
            except:
                continue

    return trades


# ===== SAVE =====
def save_trade(data):
    file_exists = os.path.isfile(FILE)

    with open(FILE, "a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Stock","Signal","Entry","Exit","Lot","PnL"]
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)


# ===== PNL =====
def calculate_pnl(entry, exit_price, signal, lot):
    if signal == "BUY":
        return (exit_price - entry) * lot * 100
    else:
        return (entry - exit_price) * lot * 100


# ===== EQUITY =====
def get_equity():
    trades = load_trades()
    equity = START_EQUITY

    for t in trades:
        equity += t["PnL"]

    return equity


# ===== PERFORMANCE =====
def get_performance():
    trades = load_trades()

    wins = sum(1 for t in trades if t["PnL"] > 0)
    losses = sum(1 for t in trades if t["PnL"] < 0)

    total = len(trades)

    winrate = (wins / total * 100) if total > 0 else 0

    return f"Trade: {total}\nWin: {wins} | Loss: {losses}\nWinrate: {round(winrate,2)}%"


# ===== EXPECTANCY =====
def get_expectancy(trades):
    wins = [t["PnL"] for t in trades if t["PnL"] > 0]
    losses = [abs(t["PnL"]) for t in trades if t["PnL"] < 0]

    total = len(trades)
    if total == 0:
        return 0

    winrate = len(wins) / total
    lossrate = len(losses) / total

    avg_win = sum(wins) / len(wins) if wins else 0
    avg_loss = sum(losses) / len(losses) if losses else 0

    expectancy = (winrate * avg_win) - (lossrate * avg_loss)

    return round(expectancy, 2)


# ===== DYNAMIC LOT =====
def calculate_lot(entry, sl, equity, risk_pct=0.02):
    risk_amount = equity * risk_pct
    risk_per_unit = abs(entry - sl)

    if risk_per_unit == 0:
        return 1

    lot = risk_amount / risk_per_unit

    return max(1, int(lot))
