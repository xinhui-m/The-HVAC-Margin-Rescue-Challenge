import pandas as pd
import numpy as np

df_materials = pd.read_csv("/Users/chloewang/Downloads/material_deliveries_all.csv")

#material cost group
df_material_cost = (
    df_materials.groupby(["project_id", "sov_line_id"])["total_cost"]
    .sum()
    .reset_index()
    .rename(columns={"total_cost": "material_cost"})
)

all_projects = df_materials["project_id"].unique()
sov_suffixes = [f"SOV-{str(i).zfill(2)}" for i in range(1, 16)]

full_index = pd.MultiIndex.from_tuples(
    [(proj, f"{proj}-{sov}") for proj in all_projects for sov in sov_suffixes],
    names=["project_id", "sov_line_id"]
)
df_full = pd.DataFrame(index=full_index).reset_index()

df_material_cost = df_full.merge(df_material_cost, on=["project_id", "sov_line_id"], how="left")
df_material_cost["material_cost"] = df_material_cost["material_cost"].fillna(0).round(3)
df_material_cost = df_material_cost.sort_values(by=["project_id", "sov_line_id"]).reset_index(drop=True)

# Labor
df_labor = pd.read_csv("/Users/chloewang/Downloads/cleaned_labor_log.csv")

df_cost = df_material_cost.merge(df_labor, on=["project_id", "sov_line_id"], how="left")
df_cost["total_labor_cost"] = df_cost["total_labor_cost"].fillna(0).round(3)

df_cost["total_cost"] = (df_cost["material_cost"] + df_cost["total_labor_cost"]).round(3)

# Budget - 直接从 sov_budget_all 读
df_budget = pd.read_csv("/Users/chloewang/Downloads/sol_budget_cleaned.csv")

df_budget["estimated_labor_material"] = (
    df_budget["estimated_labor_cost"] + df_budget["estimated_material_cost"]
).round(3)

df_budget_summary = (
    df_budget.groupby(["project_id", "sov_line_id"])["estimated_labor_material"]
    .sum()
    .reset_index()
)

df_cost = df_cost.merge(df_budget_summary, on=["project_id", "sov_line_id"], how="left")
df_cost["estimated_labor_material"] = df_cost["estimated_labor_material"].fillna(0).round(3)

# Variance = Actual - Budget
df_cost["variance"] = (df_cost["total_cost"] - df_cost["estimated_labor_material"]).round(3)

df_cost.to_csv("/Users/chloewang/Downloads/cost_summary.csv", index=False)