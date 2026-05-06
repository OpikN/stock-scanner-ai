import yfinance as yf
from datetime import datetime

from app.config import STOCKS
from app.indicators import apply_indicators
from app.strategy import generate_signal
from app.portfolio import open_position, update_positions


def run():
    print("🚀 SCANNER START (CLEAN MODE)")

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
            # SAFE CHECK (ANTI SERIES BUG 🔥)
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
            # INDICATORS
            # =========================
            df = apply_indicators(df)

            # =========================
            # SIGNAL
            # =========================
            signal, price = generate_signal(df)

            try:
                price = float(price)
            except:
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
            opened = open_position(stock, signal, price, price * 1.03, price * 0.98)

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


if __name__ == "__main__":
    run()
