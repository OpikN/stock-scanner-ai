import pandas as pd
import os

# =========================
# SAVE TRADE
# =========================
def save_trade(path, data):

    try:

        # =========================
        # CREATE DATAFRAME
        # =========================
        new_df = pd.DataFrame([data])

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

        # =========================
        # SAVE CSV
        # =========================
        df.to_csv(

            path,

            index=False
        )

    except Exception as e:

        print(
            f"SAVE TRADE ERROR: {e}"
        )

# =========================
# LOAD CSV
# =========================
def load_csv(path):

    try:

        if os.path.exists(path):

            return pd.read_csv(path)

        return pd.DataFrame()

    except:

        return pd.DataFrame()
