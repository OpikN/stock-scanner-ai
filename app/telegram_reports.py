from app.telegram import send_telegram

from app.portfolio import (
    get_live_equity,
    load_positions
)

from app.analytics import (
    total_trades,
    winrate,
    total_pnl,
    best_stock,
    worst_stock,
    avg_pnl
)

# =========================
# DAILY REPORT
# =========================
def send_daily_report():

    df = load_positions()

    floating = 0

    open_positions = 0

    if not df.empty:

        floating = df[
            df["status"] == "OPEN"
        ]["pnl"].sum()

        open_positions = len(
            df[
                df["status"] == "OPEN"
            ]
        )

    send_telegram(

        f"📊 DAILY AI REPORT\n\n"

        f"💰 Equity:\n"
        f"{get_live_equity():,.0f}\n\n"

        f"📈 Floating PnL:\n"
        f"{floating:,.0f}\n\n"

        f"📊 Closed PnL:\n"
        f"{total_pnl():,.0f}\n\n"

        f"🧠 Total Trades:\n"
        f"{total_trades()}\n\n"

        f"🏆 Winrate:\n"
        f"{winrate()}%\n\n"

        f"📡 Open Positions:\n"
        f"{open_positions}\n\n"

        f"🔥 Best Stock:\n"
        f"{best_stock()}\n\n"

        f"⚠️ Worst Stock:\n"
        f"{worst_stock()}\n\n"

        f"📈 Average PnL:\n"
        f"{avg_pnl():,.0f}"
    )

# =========================
# HIGH CONFIDENCE ALERT
# =========================
def send_high_confidence_alert(
    stock,
    signal,
    confidence,
    regime,
    price
):

    send_telegram(

        f"🚨 HIGH CONFIDENCE SETUP\n\n"

        f"{stock}\n\n"

        f"Signal:\n"
        f"{signal}\n\n"

        f"Price:\n"
        f"{price:.2f}\n\n"

        f"Confidence:\n"
        f"{confidence}%\n\n"

        f"Regime:\n"
        f"{regime}"
    )

# =========================
# REGIME CHANGE
# =========================
def send_regime_change(
    old_regime,
    new_regime
):

    send_telegram(

        f"🧠 MARKET REGIME CHANGE\n\n"

        f"{old_regime}\n"
        f"→ {new_regime}\n\n"

        f"AI updated strategy mode"
    )

# =========================
# DRAWDOWN WARNING
# =========================
def send_drawdown_warning(
    drawdown
):

    send_telegram(

        f"⚠️ DRAWDOWN WARNING\n\n"

        f"Floating Loss:\n"
        f"{drawdown:,.0f}\n\n"

        f"AI switched to SAFE mode"
    )
