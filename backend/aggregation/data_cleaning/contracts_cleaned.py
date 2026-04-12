import pandas as pd
import numpy as np

df_contracts_all=pd.read_csv("data/raw data/contracts_all.csv")

df_contracts_all = df_contracts_all.sort_values(
    by="project_id"
).reset_index(drop=True)


### calculating budget_coverage
df_sov_budget = pd.read_csv("data/Cleaned data/sov_budget_cleaned.csv")

# adding up estimated budget according to projects id
df_budget_summary = df_sov_budget.groupby("project_id")["estimated_budget"].sum().reset_index()
df_budget_summary.rename(columns={"estimated_budget": "total_estimated_budget"}, inplace=True)

# merge to contracts_all
df_contracts_all = df_contracts_all.merge(df_budget_summary, on="project_id", how="left")

# calculate budget coverage
df_contracts_all["budget_coverage"] = (
    df_contracts_all["total_estimated_budget"] / df_contracts_all["original_contract_value"]
).round(3)

df_contracts_all.to_csv("data/Cleaned data/contracts_val_cleaned.csv", index=False)