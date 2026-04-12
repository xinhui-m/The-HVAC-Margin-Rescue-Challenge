import pandas as pd
import numpy as np
import ast

# =========================
# LOAD
# =========================
bh = pd.read_csv("data/raw data/billing_history_all.csv", low_memory=False)
bli = pd.read_csv("data/raw data/billing_line_items_all.csv", low_memory=False)
co = pd.read_csv("data/raw data/change_orders_all.csv", low_memory=False)

# =========================
# CLEAN COLS
# =========================
def clean_cols(df):
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
    )
    return df

bh = clean_cols(bh)
bli = clean_cols(bli)
co = clean_cols(co)

# =========================
# CLEAN NUMERIC
# =========================
for c in ["scheduled_value", "total_billed", "pct_complete", "application_number"]:
    if c in bli.columns:
        bli[c] = pd.to_numeric(bli[c], errors="coerce")

# =========================
# pct_billed: CURRENT BILLING PROGRESS
# =========================
# 用最新一期 cumulative billed / scheduled value
bli["pct_billed"] = np.where(
    bli["scheduled_value"] > 0,
    bli["total_billed"] / bli["scheduled_value"] * 100,
    np.nan
)

# =========================
# LATEST SOV RECORD
# =========================
# 保留每个 project + sov_line 最新一期记录
bli_latest = (
    bli.sort_values(["project_id", "sov_line_id", "application_number"])
       .groupby(["project_id", "sov_line_id"], as_index=False)
       .tail(1)
       .copy()
)

# =========================
# pct_complete: CONSTRUCTION PROGRESS
# =========================
# 只用 billing_line_items_all.csv 自己带的 raw pct_complete
# 按 project + sov_line 取最大值
pct_complete_summary = (
    bli.groupby(["project_id", "sov_line_id"])["pct_complete"]
       .max()
       .reset_index()
       .rename(columns={"pct_complete": "pct_complete_max"})
)

bli_latest = bli_latest.merge(
    pct_complete_summary,
    on=["project_id", "sov_line_id"],
    how="left"
)

# 用本地原始数据里的 max pct_complete 覆盖
bli_latest["pct_complete"] = bli_latest["pct_complete_max"].clip(0, 100)

# =========================
# BILLING GAP
# =========================
bli_latest["billing_gap"] = bli_latest["pct_complete"] - bli_latest["pct_billed"]

# =========================
# BILLING HISTORY
# =========================
bh["status"] = (
    bh["status"]
    .astype(str)
    .str.strip()
    .str.upper()
)

bh["payment_date"] = pd.to_datetime(bh["payment_date"], errors="coerce")
bh["is_paid"] = bh["payment_date"].notna()

def fix_status(row):
    if row["is_paid"]:
        return "PAID"
    elif row["status"] == "APPROVED":
        return "APPROVED"
    else:
        return "PENDING"

bh["status_clean"] = bh.apply(fix_status, axis=1)
bh["retention_held"] = pd.to_numeric(bh["retention_held"], errors="coerce")

latest_bh = (
    bh.sort_values(["project_id", "application_number"])
      .groupby("project_id", as_index=False)
      .tail(1)
      .copy()
)

# =========================
# CHANGE ORDER
# =========================
co["status"] = (
    co["status"]
    .astype(str)
    .str.strip()
    .str.upper()
)

co["amount"] = pd.to_numeric(co["amount"], errors="coerce")

def parse(x):
    try:
        return ast.literal_eval(x) if pd.notna(x) else []
    except Exception:
        return []

co["affected_sov_lines"] = co["affected_sov_lines"].apply(parse)
co = co.explode("affected_sov_lines")
co = co.rename(columns={"affected_sov_lines": "sov_line_id"})
co = co[co["sov_line_id"].notna()].copy()

co_approved = co[co["status"] == "APPROVED"]

co_summary = (
    co_approved.groupby(["project_id", "sov_line_id"], as_index=False)
               .agg(total_co_amount=("amount", "sum"))
)

# =========================
# MERGE → SOV
# =========================
sov = (
    bli_latest[[
        "project_id",
        "sov_line_id",
        "scheduled_value",
        "total_billed",
        "pct_complete",
        "pct_billed",
        "billing_gap"
    ]]
    .merge(
        latest_bh[["project_id", "retention_held"]],
        on="project_id",
        how="left"
    )
    .merge(
        co_summary,
        on=["project_id", "sov_line_id"],
        how="left"
    )
)

sov["total_co_amount"] = sov["total_co_amount"].fillna(0)
sov["retention_held"] = sov["retention_held"].fillna(0)

# =========================
# RISK LOGIC
# =========================
# 这里是百分点，不是小数
sov["underbilling_flag"] = sov["billing_gap"] > 0.04
sov["overbilling_flag"] = sov["billing_gap"] < -0.04

sov["closeout_flag"] = (
    (sov["pct_complete"] >= 100) &
    (sov["total_billed"] < sov["scheduled_value"])
)

sov["retention_flag"] = sov["retention_held"] > 1

sov["true_closeout_issue"] = (
    sov["closeout_flag"] & (~sov["retention_flag"])
)

# =========================
# RISK COMPONENTS
# =========================
sov["underbilling_points"] = sov["underbilling_flag"].astype(int) * 2
sov["overbilling_points"] = sov["overbilling_flag"].astype(int) * 1
sov["closeout_points"] = sov["true_closeout_issue"].astype(int) * 3

sov["co_points"] = np.select(
    [
        sov["total_co_amount"] > 50000,
        sov["total_co_amount"] > 10000,
        sov["total_co_amount"] > 0
    ],
    [3, 2, 1],
    default=0
)

sov["risk_score"] = (
    sov["underbilling_points"] +
    sov["overbilling_points"] +
    sov["closeout_points"] +
    sov["co_points"]
)

# =========================
# PROJECT SUMMARY
# =========================
project_summary = (
    sov.groupby("project_id", as_index=False)
       .agg(
           total_budget=("scheduled_value", "sum"),
           total_billed=("total_billed", "sum"),
           avg_gap=("billing_gap", "mean"),
           risk_score=("risk_score", "sum")
       )
)

project_summary["margin"] = (
    project_summary["total_billed"] - project_summary["total_budget"]
) / project_summary["total_budget"]

# =========================
# FLAGGED
# =========================
projects_flagged = project_summary[
    project_summary["margin"] < 0.05
].copy()

# =========================
# DEBUG
# =========================
print("SOV risk_score distribution:")
print(sov["risk_score"].value_counts(dropna=False).sort_index())

print("\nBilling gap summary:")
print(sov["billing_gap"].describe())

print("\nUnderbilling count:", int(sov["underbilling_flag"].sum()))
print("Overbilling count:", int(sov["overbilling_flag"].sum()))
print("True closeout issue count:", int(sov["true_closeout_issue"].sum()))
print("CO flag count:", int((sov["total_co_amount"] > 0).sum()))

# =========================
# SAVE
# =========================
sov.to_csv("sov_summary.csv", index=False)
project_summary.to_csv("project_summary.csv", index=False)
projects_flagged.to_csv("projects_flagged.csv", index=False)

print("✅ FINAL VERSION READY")
