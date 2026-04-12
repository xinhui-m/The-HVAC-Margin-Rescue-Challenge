import pandas as pd

#merging labor cost, material cost, and budget to get total cost and variance

df_labor_cost = pd.read_csv("data/Cleaned data/cleaned_labor_log.csv")
df_material_cost = 