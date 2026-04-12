import pandas as pd

df_material = pd.read_csv("data/raw data/material_deliveries_all.csv")

str_cols = df_material.select_dtypes(include="object").columns
df_material[str_cols] = df_material[str_cols].apply(lambda x: x.str.strip())

# group by sov_line_id, sum total_cost
summary = df_material.groupby(["project_id", "sov_line_id"])["total_cost"].sum().reset_index()
summary.columns = ["project_id", "sov_line_id", "material_total_cost"]

summary.to_csv("data/Cleaned data/material_summary.csv", index=False)