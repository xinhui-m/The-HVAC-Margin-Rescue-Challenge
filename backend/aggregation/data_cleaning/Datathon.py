import pandas as pd

#Bill-history.csv
df["is_paid"] = df["payment_date"].notna()

def infer_status(row):
    if pd.notna(row["payment_date"]):
        return "PAID"
    elif row["status"] == "APPROVED":
        return "APPROVED"
    else:
        return "PENDING"

df["true_status"] = df.apply(infer_status, axis=1)

df["status_mismatch"] = (
    ((df["status"] == "PAID") & df["payment_date"].isna()) |
    ((df["status"] == "PENDING") & df["payment_date"].notna())
)
#统计mismatch比例，在report里输出


#Bill-items.csv
#输出：
# 📊 Billing Analysis:

# - SOV Line: Electrical Work
# - Completion: 80%
# - Billed: 60%

# ⚠️ Issue:
# - Underbilling detected (20% gap)

# Impact:
# - Potential cash flow delay

# Recommendation:
# - Accelerate billing for completed work

#underbilling
if pct_complete == 100 and total_billed < scheduled_value:
    → underbilling

#retention not released
if pct_complete == 100 and retention_held > 0:
    → expected unpaid (not risk)

df["pct_billed"] = df["total_billed"] / df["scheduled_value"] * 100
df["billing_gap"] = df["pct_complete"] - df["pct_billed"]
df["underbilling_flag"] = df["billing_gap"] > 10 #underbilling
df["overbilling_flag"] = df["billing_gap"] < -10 #overbilling
df["payment_delay_flag"] = (
    (df["status"] == "APPROVED") & (df["payment_date"].isna())
) #payment delay risk
df["closeout_flag"] = (
    (df["pct_complete"] == 100) &
    (df["total_billed"] < df["scheduled_value"])
) #closeout risk
df["cost_overrun_flag"] = df["variance"] > 0 #cost overrun risk 实际花的钱>预算的钱
#评分系统（加权）
df["risk_score"] = (
    df["underbilling_flag"] * 3 +
    df["payment_delay_flag"] * 3 +
    df["cost_overrun_flag"] * 2 +
    df["overbilling_flag"] * 1 +
    df["closeout_flag"] * 2
)
#结果
def risk_level(score):
    if score >= 6:
        return "HIGH"
    elif score >= 3:
        return "MEDIUM"
    else:
        return "LOW"

df["risk_level"] = df["risk_score"].apply(risk_level)

#自动输出风险原因
def generate_reason(row):
    reasons = []

    if row["underbilling_flag"]:
        reasons.append("Significant underbilling detected")

    if row["overbilling_flag"]:
        reasons.append("Potential overbilling risk")

    if row["payment_delay_flag"]:
        reasons.append("Approved but unpaid billing")

    if row["cost_overrun_flag"]:
        reasons.append("Cost exceeds budget")

    if row["closeout_flag"]:
        reasons.append("Project completed but not fully billed")

    return "; ".join(reasons)

df["risk_reason"] = df.apply(generate_reason, axis=1)
def generate_report(row):
    prompt = f"""
    You are a construction financial analyst.

    Data:
    - Completion: {row['pct_complete']}%
    - Billed: {row['pct_billed']}%
    - Variance: {row['variance']}
    - Risk Level: {row['risk_level']}
    - Issues: {row['risk_reason']}

    Generate:
    1. Summary
    2. Risk explanation
    3. Recommendation
    """
    return prompt
