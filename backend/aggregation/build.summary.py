import pandas as pd

#6075rows summary

#merging labor cost, material cost, and budget to get total cost and variance

df_labor_cost = pd.read_csv("data/Cleaned data/cleaned_labor_log.csv")
df_material_cost = pd.read_csv("data/Cleaned data/material_summary_material_overrun.csv")

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


####need to change bcuz 0 is already filled
# --- Step 3: merging material cost 
df_merged = df_merged.merge(df_material_cost, on=["project_id", "sov_line_id"], how="left")#material_total_cost,estimated_material_cost,material_overrun_ratio

# --- Step 4: merging contract_value (project level, broadcast to line items) ---
df_merged = df_merged.merge(df_contract_value, on="project_id", how="left")

# --- Step 5: merging rfis (project level) ---
df_merged = df_merged.merge(df_rfis, on="project_id", how="left")

# --- Step 6: exporting ---
df_merged.to_csv("data/final_data/final_summary.csv", index=False)

# --- Step 7: printing column names ---
print(f"Total Rows: {len(df_merged)}")
print(f"\nFeature Names ({len(df_merged.columns)} columns):")
for col in df_merged.columns:
    print(f"- {col}")

#total cost=actual_labor_cost + actual_material_cost
# Variance = Actual Cost - Budget


#total_variance（总成本偏差）✅你的公式2 = actual_total_cost - total_budget
#