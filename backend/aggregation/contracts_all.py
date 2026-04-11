import pandas as pd
import numpy as np

df_contracts_all=pd.read_csv("/Users/chloewang/Downloads/contracts_all.csv")

df_contracts_all["contract_date"] = pd.to_datetime(df_contracts_all["contract_date"], errors="coerce")
df_contracts_all["substantial_completion_date"] = pd.to_datetime(df_contracts_all["substantial_completion_date"], errors="coerce")

df_contracts_all["cohort_year"] = df_contracts_all["project_id"].str.extract(r"PRJ-(\d{4})-").astype(int)
df_contracts_all["contract_year_match"] = df_contracts_all["contract_date"].dt.year == df_contracts_all["cohort_year"]

df_contracts_all["completion_in_window"] = (
    df_contracts_all["substantial_completion_date"].dt.year <= df_contracts_all["cohort_year"] + 2
)

df_contracts_all["duration_days"] = (df_contracts_all["substantial_completion_date"] - df_contracts_all["contract_date"]).dt.days
df_contracts_all["duration_years"] = df_contracts_all["duration_days"] / 365.25

df_contracts_all["duration_flag"] = np.where(
    df_contracts_all["duration_years"] > 3, "too_long",
    np.where(df_contracts_all["duration_years"] < 0, "invalid", "ok")
)

print(df_contracts_all["duration_flag"].value_counts(dropna=False))
print(df_contracts_all["contract_year_match"].value_counts(dropna=False))
print(df_contracts_all["completion_in_window"].value_counts(dropna=False))