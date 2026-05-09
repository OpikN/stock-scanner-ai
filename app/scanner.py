import json
import os


def run():

    print("[SCANNER START]")

    live_data = {

        "equity": 100021000,

        "floating_pnl": 21000,

        "open_positions": [

            {

                "stock": "BBRI.JK",

                "side": "SELL",

                "entry_price": 3310,

                "current_price": 3260,

                "pnl": 50000,

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
