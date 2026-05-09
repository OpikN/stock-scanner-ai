import sys
import os

# =========================
# FIX IMPORT
# =========================
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from app.scanner import run

# =========================
# RUN ENGINE
# =========================
if __name__ == "__main__":

    run()
