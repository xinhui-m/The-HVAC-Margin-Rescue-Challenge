import pandas as pd

#6075rows Solve line level summary

# --- Load Data ---
df_labor_cost = pd.read_csv("data/Cleaned data/cleaned_labor_log.csv")
df_material_cost = pd.read_csv("data/Cleaned data/material_summary_material_overrun.csv")
df_material_cost = df_material_cost.drop(columns=["estimated_material_cost"])
df_budget = pd.read_csv("data/Cleaned data/sov_budget_cleaned.csv") 
#only using estimated_labor and estimated_material for now
df_contract_value = pd.read_csv("data/Cleaned data/contracts_val_cleaned.csv")
#use its budget_coverage
df_rfis = pd.read_csv("data/Cleaned data/rfis_summary.csv")
df_sov_summary = pd.read_csv("data/Cleaned data/sov_summary.csv")

###merging
# --- Step 1: sov_budget_cleaned as a base, 6075 rows--
df_merged = df_budget.copy()

# --- Step 2: merging labor cost ---
df_merged = df_merged.merge(df_labor_cost, on=["project_id", "sov_line_id"], how="left")

# --- Step 3: merging material cost 
df_merged = df_merged.merge(df_material_cost, on=["project_id", "sov_line_id"], how="left")
#material_total_cost,estimated_material_cost,material_overrun_ratio

# --- Step 4: merging contract_value (project level, broadcast to line items) ---
df_merged = df_merged.merge(df_contract_value, on="project_id", how="left")
#- total_estimated_budget is the budget on project scale!

# --- Step 5: merging rfis (project level) ---
df_merged = df_merged.merge(df_rfis, on="project_id", how="left")

#step 6: merging sov_summary (to get pct_complete and billing_gap, which are important features for the model)
df_merged = df_merged.merge(df_sov_summary, on=["project_id", "sov_line_id"], how="left")

#calculations
# Actual total cost (labor + material only)
df_merged["actual_total_cost"] = df_merged["total_labor_cost"] + df_merged["material_total_cost"]

# Budget on same scope (labor + material only, to match actual)
df_merged["estimated_labor_material_budget"] = df_merged["estimated_labor_cost"] + df_merged["estimated_material_cost"]

# Cost variance (same scope comparison)
df_merged["total_variance"] = df_merged["actual_total_cost"] - df_merged["estimated_labor_material_budget"]

# Labor overrun ratio
df_merged["labor_overrun_ratio"] = df_merged["total_labor_cost"] / df_merged["estimated_labor_cost"]

# Bid margin (planned margin at contract time)
#df_merged["bid_margin"] = (df_merged["scheduled_value"] - df_merged["estimated_budget"]) / df_merged["scheduled_value"]

#calculating bid margin and realize margin on project level
check = df_merged.groupby("project_id")["total_estimated_budget"].nunique()
print(check[check > 1]) 

# actual_total_cost is SOV level
# contract_value and total_estimated_budget is project level

# Step 1: 同时聚合所有需要sum的字段
agg_by_project = df_merged.groupby("project_id").agg(
    actual_total_cost        = ("actual_total_cost", "sum"),
    estimated_labor_cost_sum = ("estimated_labor_cost", "sum"),
    estimated_material_cost_sum = ("estimated_material_cost", "sum")
).reset_index()

# Step 2: project级别字段直接去重
project_info = df_merged[["project_id", "original_contract_value"]].drop_duplicates("project_id")

# Step 3: 合并
df_project = project_info.merge(agg_by_project, on="project_id", how="left")

# Step 4: 同口径算margin
df_project["realized_margin"] = (
    (df_project["original_contract_value"] - df_project["actual_total_cost"])
    / df_project["original_contract_value"]
)

df_project["bid_margin"] = (
    (df_project["original_contract_value"] 
     - df_project["estimated_labor_cost_sum"] 
     - df_project["estimated_material_cost_sum"])
    / df_project["original_contract_value"]
)

df_project["margin_erosion"] = df_project["bid_margin"] - df_project["realized_margin"]

# Step 5: merge back to 6075
df_merged = df_merged.merge(
    df_project[["project_id", "realized_margin", "bid_margin", "margin_erosion"]],
    on="project_id",
    how="left"
)

#pid = "PRJ-2018-001"
#row = df_project[df_project.project_id == pid].iloc[0]
#print(f"contract_value:          {row.original_contract_value:,.0f}")
#print(f"total_estimated_budget:  {row.total_estimated_budget:,.0f}")  # this is larger than contract value
#print(f"actual_total_cost:       {row.actual_total_cost:,.0f}")

# step 7: exporting ---
df_merged.to_csv("data/final_data/final_summary.csv", index=False)

# step 8: printing column names ---
print(f"Total Rows: {len(df_merged)}")
print(f"\nFeature Names ({len(df_merged.columns)} columns):")
for col in df_merged.columns:
    print(f"- {col}")