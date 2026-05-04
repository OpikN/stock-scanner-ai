def choose_strategy(df):
    r = df.iloc[-1]

    adx = r["adx"]

    if adx > 25:
        return "TREND"

    return "SIDEWAYS"
