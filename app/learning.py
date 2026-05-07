import pandas as pd
import os

LEARNING_PATH = "data/learning.csv"

# =========================
# SAVE LEARNING
# =========================
def save_learning(data):

    try:

        new_df = pd.DataFrame([data])

        if os.path.exists(LEARNING_PATH):

            old_df = pd.read_csv(
                LEARNING_PATH
            )

            df = pd.concat(

                [old_df, new_df],

                ignore_index=True
            )

        else:

            df = new_df

        df.to_csv(

            LEARNING_PATH,

            index=False
        )

    except Exception as e:

        print(
            f"LEARNING SAVE ERROR: {e}"
        )

# =========================
# LOAD LEARNING
# =========================
def load_learning():

    try:

        if os.path.exists(
            LEARNING_PATH
        ):

            return pd.read_csv(
                LEARNING_PATH
            )

        return pd.DataFrame()

    except:

        return pd.DataFrame()

# =========================
# AI LEARNING SCORE
# =========================
def get_ai_learning_score():

    df = load_learning()

    if df.empty:

        return 0

    try:

        wins = len(
            df[df["pnl"] > 0]
        )

        losses = len(
            df[df["pnl"] <= 0]
        )

        total = wins + losses

        if total == 0:

            return 0

        score = (
            wins / total
        ) * 100

        return round(score, 2)

    except:

        return 0
