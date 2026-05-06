import sys
import os
import time

# =========================
# FIX IMPORT PATH
# =========================
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# =========================
# IMPORT
# =========================
from app.optimizer import optimize


# =========================
# MAIN RUN
# =========================
def run():
    print("🧠 RUN AI OPTIMIZER")

    try:
        # jalankan optimizer (limit biar tidak berat)
        optimize(limit=50)

        print("✅ OPTIMIZER DONE")

    except Exception as e:
        print("❌ OPTIMIZER ERROR:", e)

    # =========================
    # SAVE LAST RUN TIME
    # =========================
    try:
        os.makedirs("data", exist_ok=True)

        with open("data/last_opt.txt", "w") as f:
            f.write(str(time.time()))

        print("🕒 last_opt.txt updated")

    except Exception as e:
        print("⚠️ gagal update last_opt.txt:", e)


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    run()
