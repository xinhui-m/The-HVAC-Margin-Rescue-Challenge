import pandas as pd
import numpy as np
import os

def clean_and_aggregate():
    #read through csv
    print("Loading data...")
    df = pd.read_csv('/Users/xin/Desktop/Datathon/raw data/labor_logs_all.csv')
    print(f"Shape: {df.shape}")
    print(df.dtypes)
    print() 