import yfinance as yf
from datetime import datetime
import os

from app.config import STOCKS
from app.indicators import apply_indicators
from app.strategy import generate_signal
from app.portfolio import open_position, update_positions
from app.scanner import run


# =========================
# GITHUB PUSH (WAJIB 🔥)
# =========================
def push_to_github():
    try:
        os.system('git config --global user.email "bot@ai.com"')
        os.system('git config --global user.name "AI Bot"')
        os.system('git add data/positions.csv')
        os.system('git commit -m "update positions"')
        os.system('git push')
        print("✅ pushed to github")
    except Exception as e:
        print("❌ push error:", e)


# =========================
# SCANNER ENGINE
# =========================
def run():
    print("🚀 SCANNER START (FINAL MODE)")

    latest_prices = {}

    for stock in STOCKS:
        try:
            df = yf.download(
                stock,
                period="5d",
                interval="1h",
                progress=False
            )

            # =========================
            # SAFE CHECK
            # =========================
            if df is None:
                print(f"SKIP {stock} (no data)")
                continue

            if hasattr(df, "empty") and df.empty:
                print(f"SKIP {stock} (empty)")
                continue

            if len(df) < 20:
                print(f"SKIP {stock} (not enough data)")
                continue

            # =========================
            # APPLY INDICATORS
            # =========================
            df = apply_indicators(df)

            # =========================
            # GENERATE SIGNAL
            # =========================
            signal, price = generate_signal(df)

            try:
                price = float(price)
            except:
                print(f"SKIP {stock} (invalid price)")
                continue

            latest_prices[stock] = price

            print(f"SIGNAL: {stock} {signal} @ {price}")

            # =========================
            # SKIP HOLD
            # =========================
            if signal == "HOLD":
                continue

            # =========================
            # OPEN POSITION
            # =========================
            opened = open_position(
                stock,
                signal,
                price,
                price * 1.03,  # TP
                price * 0.98   # SL
            )

            if opened:
                print(f"OPENED: {stock} {signal}")

        except Exception as e:
            print(f"❌ ERROR: {stock} {e}")

    # =========================
    # UPDATE POSITIONS
    # =========================
    try:
        update_positions(latest_prices)
    except Exception as e:
        print("❌ UPDATE ERROR:", e)

    # =========================
    # PUSH KE GITHUB 🔥
    # =========================
    push_to_github()


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    run()
