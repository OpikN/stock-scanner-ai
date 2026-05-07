import pandas as pd
import os
import json
import time

# =========================
# SAVE TRADE
# =========================
def save_trade(
    path,
    trade_data
):

    try:

        new_df = pd.DataFrame(
            [trade_data]
        )

        # =========================
        # FILE EXISTS
        # =========================
        if os.path.exists(path):

            old_df = pd.read_csv(path)

            df = pd.concat(

                [old_df, new_df],

                ignore_index=True
            )

        else:

            df = new_df

        df.to_csv(

            path,

            index=False
        )

    except Exception as e:

        print(
            f"SAVE TRADE ERROR: {e}"
        )

# =========================
# SAVE STRATEGY
# =========================
def save_strategy(
    strategy,
    path="data/strategy.json"
):

    try:

        with open(

            path,

            "w"
        ) as f:

            json.dump(

                strategy,

                f,

                indent=4
            )

    except Exception as e:

        print(
            f"SAVE STRATEGY ERROR: {e}"
        )

# =========================
# LOAD STRATEGY
# =========================
def load_strategy(
    path="data/strategy.json"
):

    try:

        if not os.path.exists(path):

            return {}

        with open(
            path,
            "r"
        ) as f:

            return json.load(f)

    except Exception as e:

        print(
            f"LOAD STRATEGY ERROR: {e}"
        )

        return {}

# =========================
# SAVE JSON
# =========================
def save_json(
    path,
    data
):

    try:

        with open(
            path,
            "w"
        ) as f:

            json.dump(
                data,
                f,
                indent=4
            )

    except Exception as e:

        print(
            f"SAVE JSON ERROR: {e}"
        )

# =========================
# LOAD JSON
# =========================
def load_json(path):

    try:

        if not os.path.exists(path):

            return {}

        with open(
            path,
            "r"
        ) as f:

            return json.load(f)

    except Exception as e:

        print(
            f"LOAD JSON ERROR: {e}"
        )

        return {}
