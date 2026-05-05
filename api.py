from fastapi import FastAPI
import pandas as pd

app = FastAPI()

INITIAL_CAPITAL = 10000000


@app.get("/")
def root():
    return {"status": "API RUNNING"}


@app.get("/trades")
def get_trades():
    df = pd.read_csv("trades.csv")
    return df.to_dict(orient="records")


@app.get("/stats")
def get_stats():
    df = pd.read_csv("trades.csv")

    if df.empty:
        return {
            "equity": INITIAL_CAPITAL,
            "total": 0,
            "win": 0,
            "loss": 0,
            "winrate": 0
        }

    total = len(df)
    win = len(df[df["PnL"] > 0])
    loss = len(df[df["PnL"] < 0])

    winrate = (win / total) * 100

    equity = df["PnL"].cumsum().iloc[-1] + INITIAL_CAPITAL

    return {
        "equity": int(equity),
        "total": total,
        "win": win,
        "loss": loss,
        "winrate": round(winrate, 2)
    }
