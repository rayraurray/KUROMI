import pandas as pd

def load_data(path="data/Dataset-Cleaned.csv"):
    df = pd.read_csv(path)

    return df