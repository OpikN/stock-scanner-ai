import json
import os
import random


def run():

    print("[SCANNER START]")

    current_price = random.randint(

        3200,

        3400

    )

    pnl = random.randint(

        -50000,

        150000

    )

    floating_pnl = random.randint(

        -100000,

        300000

    )

    equity = 100000000 + floating_pnl

    live_data = {

        "equity": equity,

        "floating_pnl": floating_pnl,

        "open_positions": [

            {

                "stock": "BBRI.JK",

                "side": "SELL",

                "entry_price": 3310,

                "current_price": current_price,

                "pnl": pnl,

                "sl": 3343,

                "tp1": 3243

            }

        ]

    }

    os.makedirs(

        "data",

        exist_ok=True

    )

    with open(

        "data/live_data.json",

        "w"

    ) as f:

        json.dump(

            live_data,

            f,

            indent=4

        )

    print("[LIVE JSON UPDATED]")

    print("[SCANNER FINISHED]")
