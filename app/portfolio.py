import os
import pandas as pd

# =========================
# PORTFOLIO PATH
# =========================

POSITIONS_PATH = (
    "data/positions.csv"
)

INITIAL_BALANCE = (
    100000000
)

# =========================
# ENSURE DATA DIR
# =========================

os.makedirs(
    "data",
    exist_ok=True
)

# =========================
# CREATE FILE IF NOT EXISTS
# =========================

if not os.path.exists(
    POSITIONS_PATH
):

    df = pd.DataFrame(columns=[

        "stock",

        "side",

        "entry_price",

        "current_price",

        "pnl",

        "sl",

        "tp1",

        "tp2",

        "status"

    ])

    df.to_csv(
        POSITIONS_PATH,
        index=False
    )

# =========================
# LOAD POSITIONS
# =========================

def load_positions():

    return pd.read_csv(
        POSITIONS_PATH
    )

# =========================
# SAVE POSITIONS
# =========================

def save_positions(df):

    df.to_csv(

        POSITIONS_PATH,

        index=False

    )

# =========================
# OPEN POSITION
# =========================

def open_position(

    stock,

    side,

    entry_price,

    sl,

    tp1,

    tp2

):

    df = load_positions()

    new_position = {

        "stock": stock,

        "side": side,

        "entry_price": entry_price,

        "current_price": entry_price,

        "pnl": 0,

        "sl": sl,

        "tp1": tp1,

        "tp2": tp2,

        "status": "OPEN"

    }

    df = pd.concat(

        [

            df,

            pd.DataFrame([

                new_position

            ])

        ],

        ignore_index=True

    )

    save_positions(df)

# =========================
# UPDATE POSITIONS
# =========================

def update_positions(

    stock,

    current_price

):

    df = load_positions()

    if df.empty:

        return

    for idx, row in df.iterrows():

        if (

            row["stock"] == stock

            and

            row["status"] == "OPEN"

        ):

            df.at[

                idx,

                "current_price"

            ] = current_price

            # =========================
            # CALCULATE PNL
            # =========================

            if row["side"] == "BUY":

                pnl = (

                    current_price
                    - row["entry_price"]

                ) * 100

            else:

                pnl = (

                    row["entry_price"]
                    - current_price

                ) * 100

            df.at[

                idx,

                "pnl"

            ] = pnl

    save_positions(df)

# =========================
# GET OPEN POSITIONS
# =========================

def get_open_positions():

    df = load_positions()

    if df.empty:

        return df

    return df[

        df["status"] == "OPEN"

    ]

# =========================
# CALCULATE EQUITY
# =========================

def calculate_equity():

    positions = get_open_positions()

    floating_pnl = 0

    if not positions.empty:

        floating_pnl = positions[
            "pnl"
        ].sum()

    live_equity = (

        INITIAL_BALANCE
        + floating_pnl

    )

    return {

        "live_equity": live_equity,

        "floating_pnl": floating_pnl

    }
