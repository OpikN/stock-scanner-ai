def apply_indicators(df):
    df["ema5"] = df["Close"].ewm(span=5).mean()
    df["ema10"] = df["Close"].ewm(span=10).mean()
    return df
