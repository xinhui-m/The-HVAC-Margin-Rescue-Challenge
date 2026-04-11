import pandas as pd

df = pd.read_csv("data/raw data/rfis_all.csv")
summary = df.groupby("project_id").size().reset_index(name="rfi_count")
summary.to_csv("data/Cleaned data/rfis_summary.csv", index=False)