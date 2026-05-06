import time
import os

from app.adaptive import update_mode
from app.learning import learn_from_trades
from app.optimizer import optimize

LAST_OPT_PATH = "data/last_opt.txt"


# =========================
# CHECK OPTIMIZER TIMER
# =========================
def should_run_optimizer():
    if not os.path.exists(LAST_OPT_PATH):
        return True

    with open(LAST_OPT_PATH) as f:
        last = float(f.read())

    # 6 jam
    return (time.time() - last) > 21600


def mark_optimizer_run():
    with open(LAST_OPT_PATH, "w") as f:
        f.write(str(time.time()))


# =========================
# AI BRAIN 🔥
# =========================
def run_brain(df):
    # =========================
    # 1. ADAPTIVE (REALTIME)
    # =========================
    state = update_mode(df)

    # =========================
    # 2. LEARNING (REAL TRADE)
    # =========================
    learn_from_trades()

    # =========================
    # 3. OPTIMIZER (PERIODIC)
    # =========================
    if should_run_optimizer():
        print("🧠 RUN OPTIMIZER...")
        optimize()
        mark_optimizer_run()

    return state
