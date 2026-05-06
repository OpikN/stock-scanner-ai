import json
import os

STRATEGY_PATH = "data/strategy.json"


def load_strategy():
    if os.path.exists(STRATEGY_PATH):
        try:
            with open(STRATEGY_PATH) as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_strategy(data):
    with open(STRATEGY_PATH, "w") as f:
        json.dump(data, f, indent=2)
