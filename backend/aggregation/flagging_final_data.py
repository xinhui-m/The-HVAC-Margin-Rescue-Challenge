import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

df = pd.read_csv("data/final_data/final_summary.csv")

# calculate margin_erosion
df["margin_erosion"] = df["bid_margin"] - df["realized_margin"]

# choose features
features = [
    "actual_margin",
    "margin_erosion",
    "labor_overrun_ratio",
    "material_overrun_ratio",
    "total_co_amount",
    "billing_gap",
    "pct_complete",
    "total_delay_days"
]

# 去掉 NaN
df_model = df[features].fillna(0)

# standarlizing
scaler = StandardScaler()
X = scaler.fit_transform(df_model)

# Isolation Forest machine learning
model = IsolationForest(
    contamination=0.1,
    random_state=42
)
df["anomaly_flag"] = model.fit_predict(X)
df["anomaly_flag"] = df["anomaly_flag"].map({1: 0, -1: 1})
def flag_reasons(row):
    reasons = []
    if row["actual_margin"] < 0.05:
        reasons.append("low_margin")
    if row["labor_overrun_ratio"] > 1.2:
        reasons.append("labor_overrun")
    if row["material_overrun_ratio"] > 1.5:
        reasons.append("material_overrun")
    if row["total_co_amount"] > df["total_co_amount"].quantile(0.9):
        reasons.append("high_co_amount")
    if row["billing_gap"] > 10:
        reasons.append("high_billing_gap")
    if row["total_delay_days"] > df["total_delay_days"].quantile(0.9):
        reasons.append("high_delay")
    if row["anomaly_flag"] == 1 and not reasons:
        reasons.append("ml_anomaly")
    return ", ".join(reasons) if reasons else "ok"

df["flag_reason"] = df.apply(flag_reasons, axis=1)

# output
projects_flagged = df[
    (df["anomaly_flag"] == 1) |
    (df["actual_margin"] < 0.05)
]

print(f"Total number of projects: {len(df)}")
print(f"Number of flagged cases: {len(projects_flagged)}")
print(f"Flagged cases percentage: {len(projects_flagged)/len(df)*100:.1f}%")


projects_flagged.to_csv("data/final_data/projects_flagged.csv", index=False)
print("✅ Done!")