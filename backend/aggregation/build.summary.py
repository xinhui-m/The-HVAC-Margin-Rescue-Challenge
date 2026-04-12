import pandas as pd

#6075rows summary

#merging labor cost, material cost, and budget to get total cost and variance

df_labor_cost = pd.read_csv("data/Cleaned data/cleaned_labor_log.csv")
df_material_cost = pd.read_csv("data/Cleaned data/material_summary.csv")

df_budget = pd.read_csv("data/Cleaned data/sov_budget_cleaned.csv") #only using estimated_labor and estimated_material for now
df_contract_value = pd.read_csv("data/Cleaned data/contract_val_cleaned.csv")