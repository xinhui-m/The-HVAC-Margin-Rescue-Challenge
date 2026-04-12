import pandas as pd
import numpy as np

bli = pd.read_csv("data/raw data/billing_line_items_all.csv")

bli["pct_complete"] = bli["pct_complete"].fillna(0)
bli["balance_to_finish"] = bli["balance_to_finish"].fillna(0)

# pct_billed
bli["pct_billed"] = (
    bli["total_billed"] / (bli["total_billed"] + bli["balance_to_finish"])
* 100).fillna(0).round(3)

# billing_gap = pct_complete - pct_billed
bli["billing_gap"] = (bli["pct_complete"] - bli["pct_billed"]).fillna(0).round(3)

bli = bli.sort_values(by=["project_id", "sov_line_id", "application_number"]).reset_index(drop=True)
bli.to_csv("data/Cleaned data/billing_with_gap_cleaned.csv", index=False)
