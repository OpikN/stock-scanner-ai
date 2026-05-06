import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.optimizer import optimize


if __name__ == "__main__":
    print("🚀 RUN AI OPTIMIZER (SAFE MODE)")

    try:
        optimize(limit=50)  # 🔥 BATASIN ITERASI
        print("✅ OPTIMIZER DONE")
    except Exception as e:
        print("❌ OPTIMIZER ERROR:", e)
