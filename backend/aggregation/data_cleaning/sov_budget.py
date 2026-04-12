import pandas as pd
import numpy as np

df_sov_budget = pd.read_csv("data/raw data/sov_budget_all.csv")

df_sov_budget = df_sov_budget.sort_values(
    by="sov_line_id"
).reset_index(drop=True)

df_sov_budget = df_sov_budget.dropna(subset=[
    "project_id",
    "sov_line_id",
    "estimated_labor_hours",
    "estimated_labor_cost",
    "estimated_material_cost",
    "estimated_equipment_cost",
    "estimated_sub_cost",
    "productivity_factor"
])

df_sov_budget["estimated_budget"] = (
    df_sov_budget["estimated_labor_cost"] / df_sov_budget["productivity_factor"]
    + df_sov_budget["estimated_material_cost"]
    + df_sov_budget["estimated_equipment_cost"]
    + df_sov_budget["estimated_sub_cost"]
).round(3)


df_sov_budget.to_csv("data/Cleaned data/sov_budget_cleaned.csv", index=False)