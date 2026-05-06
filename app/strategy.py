from .utils import safe_float
from .config import MODE

def generate_signal(df):
    last = df.iloc[-1]

    ema5 = safe_float(last["ema5"])
    ema10 = safe_float(last["ema10"])
    price = safe_float(last["Close"])

    score = 1 if ema5 > ema10 else -1

    if MODE == "AGGRESSIVE":
        signal = "BUY" if score >= 0 else "SELL"
    else:
        signal = "BUY" if score > 0 else "SELL"

    return signal, price
