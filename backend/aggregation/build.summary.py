import pandas as pd

#6075rows summary

#merging labor cost, material cost, and budget to get total cost and variance

df_labor_cost = pd.read_csv("data/Cleaned data/cleaned_labor_log.csv")
df_material_cost = pd.read_csv("data/Cleaned data/material_summary.csv")

df_budget = pd.read_csv("data/Cleaned data/sov_budget_cleaned.csv") 
#only using estimated_labor and estimated_material for now

df_contract_value = pd.read_csv("data/Cleaned data/contracts_val_cleaned.csv")
#use its budget_coverage

df_rfis = pd.read_csv("data/Cleaned data/rfis_summary.csv")
df_sov_summary = pd.read_csv("data/Cleaned data/sov_summary.csv")

# --- Step 1: sov_budget_cleaned as a base, 6075 rows--
df_merged = df_budget.copy()

# --- Step 2: merging labor cost ---
df_merged = df_merged.merge(df_labor_cost, on=["project_id", "sov_line_id"], how="left")

# --- Step 3: merging material cost (fill missing values with 0) ---
df_merged = df_merged.merge(df_material_cost, on=["project_id", "sov_line_id"], how="left")
material_cols = [c for c in df_material_cost.columns if c not in ["project_id", "sov_line_id"]]
df_merged[material_cols] = df_merged[material_cols].fillna(0)

# --- Step 4: merging contract_value (project level, broadcast to line items) ---
df_merged = df_merged.merge(df_contract_value, on="project_id", how="left")

# --- Step 5: merging rfl (project level) ---
df_merged = df_merged.merge(df_rfis, on="project_id", how="left")

# --- Step 6: exporting ---
df_merged.to_csv("data/final_data/final_summary.csv", index=False)

# --- Step 7: printing column names ---
print(f"Total Rows: {len(df_merged)}")
print(f"\nFeature Names ({len(df_merged.columns)} columns):")
for col in df_merged.columns:
    print(f"- {col}")
