import os
import pandas as pd

def save_trade(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    new_df = pd.DataFrame([data])

    if os.path.exists(path):
        try:
            old_df = pd.read_csv(path)
            df = pd.concat([old_df, new_df], ignore_index=True)
        except:
            df = new_df
    else:
        df = new_df

    df.to_csv(path, index=False)
