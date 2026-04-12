import pandas as pd
import numpy as np

df_material = pd.read_csv("data/raw data/material_deliveries_all.csv")
str_cols = df_material.select_dtypes(include="object").columns
df_material[str_cols] = df_material[str_cols].apply(lambda x: x.str.strip())

# group by sov_line_id, sum total_cost
summary = df_material.groupby(["project_id", "sov_line_id"])["total_cost"].sum().reset_index()
summary.columns = ["project_id", "sov_line_id", "material_total_cost"]

# 创建完整的 project_id x sov_line_id 组合
all_projects = df_material["project_id"].unique()
sov_suffixes = [f"SOV-{str(i).zfill(2)}" for i in range(1, 16)]

full_index = pd.MultiIndex.from_tuples(
    [(proj, f"{proj}-{sov}") for proj in all_projects for sov in sov_suffixes],
    names=["project_id", "sov_line_id"]
)
df_full = pd.DataFrame(index=full_index).reset_index()

# merge，没有的填0
summary = df_full.merge(summary, on=["project_id", "sov_line_id"], how="left")
summary["material_total_cost"] = summary["material_total_cost"].fillna(0)

# merge budget
df_budget = pd.read_csv("data/Cleaned data/sov_budget_cleaned.csv")
summary = summary.merge(
    df_budget[["project_id", "sov_line_id", "estimated_material_cost"]],
    on=["project_id", "sov_line_id"],
    how="left"
)
summary["estimated_material_cost"] = summary["estimated_material_cost"].fillna(0)

# material overrun ratio
summary["material_overrun_ratio"] = np.where(
    (summary["estimated_material_cost"] == 0) & (summary["material_total_cost"] > 0), 2,
    np.where(
        summary["estimated_material_cost"] == 0, 0,
        (summary["material_total_cost"] / summary["estimated_material_cost"]).round(3)
    )
)

summary = summary.sort_values(by=["project_id", "sov_line_id"]).reset_index(drop=True)
summary.to_csv("data/Cleaned data/material_summary_material_overrun.csv", index=False)