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
# CLEAN COLUMN NAMES
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
# BILLING LINE ITEMS CLEAN
# =========================
num_cols = [
    "scheduled_value","previous_billed","this_period",
    "total_billed","pct_complete"
]

for c in num_cols:
    bli[c] = pd.to_numeric(bli[c], errors="coerce")

# pct_billed
bli["pct_billed"] = bli["total_billed"] / bli["scheduled_value"] * 100

# fill pct_complete（关键修复）
bli["pct_complete"] = bli["pct_complete"].where(
    bli["pct_complete"].notna(),
    bli["pct_billed"]
)

# billing gap
bli["billing_gap"] = bli["pct_complete"] - bli["pct_billed"]

# =========================
# KEEP ONLY LATEST BILLING
# =========================
bli_latest = (
    bli.sort_values(["project_id","sov_line_id","application_number"])
    .groupby(["project_id","sov_line_id"], as_index=False)
    .tail(1)
)

# =========================
# CHANGE ORDER CLEAN
# =========================
co["amount"] = pd.to_numeric(co["amount"], errors="coerce")
co["schedule_impact_days"] = pd.to_numeric(co["schedule_impact_days"], errors="coerce")

def parse(x):
    try:
        return ast.literal_eval(x) if pd.notna(x) else []
    except:
        return []

co["affected_sov_lines"] = co["affected_sov_lines"].apply(parse)
co = co.explode("affected_sov_lines")

co = co.rename(columns={"affected_sov_lines":"sov_line_id"})

# only approved
co = co[co["status"].str.upper()=="APPROVED"]

co_summary = (
    co.groupby(["project_id","sov_line_id"], as_index=False)
    .agg(
        change_order_count=("co_number","count"),
        total_co_amount=("amount","sum"),
        total_delay_days=("schedule_impact_days","sum")
    )
)

# =========================
# SOV SUMMARY（核心表）
# =========================
sov_summary = (
    bli_latest[[
        "project_id","sov_line_id",
        "scheduled_value","total_billed",
        "pct_complete","billing_gap"
    ]]
    .merge(co_summary, on=["project_id","sov_line_id"], how="left")
)

# fill NA
sov_summary[["change_order_count","total_co_amount","total_delay_days"]] = \
    sov_summary[["change_order_count","total_co_amount","total_delay_days"]].fillna(0)

# =========================
# PROJECT SUMMARY
# =========================
project_summary = (
    sov_summary.groupby("project_id", as_index=False)
    .agg(
        total_budget=("scheduled_value","sum"),
        total_billed=("total_billed","sum"),
        avg_billing_gap=("billing_gap","mean"),
        total_co_amount=("total_co_amount","sum"),
        total_delay_days=("total_delay_days","sum")
    )
)

# margin
#project_summary["margin"] = (
    #project_summary["total_billed"] - project_summary["total_budget"]
#) / project_summary["total_budget"]

# =========================
# FLAGGED PROJECTS
# =========================
#projects_flagged = project_summary[
#    (project_summary["margin"] < 0.05)]

# =========================
# SAVE FILES
# =========================
sov_summary.to_csv("data/Cleaned data/sov_summary.csv", index=False)
#project_summary.to_csv("data/Cleaned data/project_summary.csv", index=False)
#projects_flagged.to_csv("data/Cleaned data/projects_flagged.csv", index=False)

print("✅ Done!")