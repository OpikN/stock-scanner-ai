import sys
import os

# tambahkan root project ke path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.scanner import run

if __name__ == "__main__":
    run()
