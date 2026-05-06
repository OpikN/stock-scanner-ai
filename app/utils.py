import numpy as np
import pandas as pd

def safe_float(x):
    try:
        if isinstance(x, pd.DataFrame):
            return float(x.values.flatten()[0])
        if isinstance(x, pd.Series):
            return float(x.iloc[0])
        if isinstance(x, (list, tuple, np.ndarray)):
            return float(np.array(x).flatten()[0])
        return float(x)
    except:
        return 0.0
