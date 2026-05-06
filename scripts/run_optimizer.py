import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.optimizer import optimize

if __name__ == "__main__":
    optimize()
