import pandas as pd
import numpy as np

df_contracts_all=pd.read_csv("/Users/chloewang/Downloads/contracts_all.csv")

df_contracts_all = df_contracts_all.sort_values(
    by="project_id"
).reset_index(drop=True)

df_sol_budget = pd.read_csv("/Users/chloewang/Downloads/sol_budget_cleaned.csv")

# 先把每个project的estimated_budget加总
df_budget_summary = df_sol_budget.groupby("project_id")["estimated_budget"].sum().reset_index()
df_budget_summary.rename(columns={"estimated_budget": "total_estimated_budget"}, inplace=True)

# merge进contracts_all
df_contracts_all = df_contracts_all.merge(df_budget_summary, on="project_id", how="left")

df_contracts_all = df_contracts_all.drop(columns=["gc_name", "architect", "engineer_of_record"])
# 计算budget coverage
df_contracts_all["budget_coverage"] = (
    df_contracts_all["total_estimated_budget"] / df_contracts_all["original_contract_value"]
).round(3)

df_contracts_all.to_csv("/Users/chloewang/Downloads/contracts_all_cleaned.csv", index=False)