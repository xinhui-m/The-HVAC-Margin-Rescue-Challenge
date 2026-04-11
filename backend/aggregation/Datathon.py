import pandas as pd
from pathlib import Path


def infer_status(df: pd.DataFrame) -> pd.Series:
    def _infer(row):
        if pd.notna(row["payment_date"]):
            return "PAID"
        if row["status"] == "APPROVED":
            return "APPROVED"
        return "PENDING"

    return df.apply(_infer, axis=1)


def compute_payment_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["is_paid"] = df["payment_date"].notna()
    df["true_status"] = infer_status(df)
    df["status_mismatch"] = (
        ((df["status"] == "PAID") & df["payment_date"].isna()) |
        ((df["status"] == "PENDING") & df["payment_date"].notna())
    )
    return df


def generate_reason(row: pd.Series) -> str:
    reasons = []
    if row.get("underbilling_flag"):
        reasons.append("Significant underbilling detected")
    if row.get("overbilling_flag"):
        reasons.append("Potential overbilling risk")
    if row.get("payment_delay_flag"):
        reasons.append("Approved but unpaid billing")
    if row.get("cost_overrun_flag"):
        reasons.append("Cost exceeds budget")
    if row.get("closeout_flag"):
        reasons.append("Project completed but not fully billed")
    return "; ".join(reasons)


def compute_billing_risk(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["pct_billed"] = df["total_billed"] / df["scheduled_value"] * 100
    df["billing_gap"] = df["pct_complete"] - df["pct_billed"]
    df["underbilling_flag"] = df["billing_gap"] > 10
    df["overbilling_flag"] = df["billing_gap"] < -10
    df["payment_delay_flag"] = (
        (df["status"] == "APPROVED") & df["payment_date"].isna()
    )
    df["closeout_flag"] = (
        (df["pct_complete"] == 100) &
        (df["total_billed"] < df["scheduled_value"])
    )
    df["cost_overrun_flag"] = df["variance"] > 0
    df["risk_score"] = (
        df["underbilling_flag"].astype(int) * 3 +
        df["payment_delay_flag"].astype(int) * 3 +
        df["cost_overrun_flag"].astype(int) * 2 +
        df["overbilling_flag"].astype(int) * 1 +
        df["closeout_flag"].astype(int) * 2
    )
    df["risk_level"] = df["risk_score"].apply(
        lambda value: "HIGH" if value >= 6 else "MEDIUM" if value >= 3 else "LOW"
    )
    df["risk_reason"] = df.apply(generate_reason, axis=1)
    return df


def generate_report(row: pd.Series) -> str:
    return (
        f"Project {row.get('project_id', 'unknown')} billing summary:\n"
        f"- Completion: {row.get('pct_complete', 0):.1f}%\n"
        f"- Billed: {row.get('pct_billed', 0):.1f}%\n"
        f"- Variance: {row.get('variance', 0)}\n"
        f"- Risk Level: {row.get('risk_level', 'UNKNOWN')}\n"
        f"- Issues: {row.get('risk_reason', 'None')}\n"
    )


def summarize_change_orders(df: pd.DataFrame) -> pd.DataFrame:
    approved_co = df[df["status"] == "APPROVED"]
    return (
        approved_co.groupby("project_id", as_index=False)
        .agg(
            change_order_count=("co_number", "count"),
            total_change_order_amount=("amount", "sum"),
            linked_rfi_count=("related_rfi", lambda s: s.notna().sum()),
        )
    )


def summarize_change_order_reasons(df: pd.DataFrame) -> pd.DataFrame:
    approved_co = df[df["status"] == "APPROVED"]
    return (
        approved_co.groupby("reason_category", as_index=False)
        .agg(
            count=("co_number", "count"),
            total_amount=("amount", "sum"),
        )
    )


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def main() -> None:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    billing_path = data_dir / "Bill-items.csv"
    history_path = data_dir / "Bill-history.csv"
    change_order_path = data_dir / "Change-Order.csv"

    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    if billing_path.exists():
        billing_df = load_csv(billing_path)
        billing_df = compute_billing_risk(compute_payment_flags(billing_df))
        print(billing_df.head())
    else:
        print(f"Missing billing file: {billing_path}")

    if history_path.exists():
        history_df = load_csv(history_path)
        history_df = compute_payment_flags(history_df)
        print(history_df.head())
    else:
        print(f"Missing bill history file: {history_path}")

    if change_order_path.exists():
        change_order_df = load_csv(change_order_path)
        print(summarize_change_orders(change_order_df).head())
        print(summarize_change_order_reasons(change_order_df).head())
    else:
        print(f"Missing change order file: {change_order_path}")


if __name__ == "__main__":
    main()
    return (
        approved_co.groupby("project_id", as_index=False)
        .agg(
            change_order_count=("co_number", "count"),
            total_change_order_amount=("amount", "sum"),
            linked_rfi_count=("related_rfi", lambda s: s.notna().sum()),
        )
    )


def summarize_change_order_reasons(df: pd.DataFrame) -> pd.DataFrame:
    approved_co = df[df["status"] == "APPROVED"]
    return (
        approved_co.groupby("reason_category", as_index=False)
        .agg(
            count=("co_number", "count"),
            total_amount=("amount", "sum"),
        )
    )


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def main() -> None:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    billing_path = data_dir / "Bill-items.csv"
    history_path = data_dir / "Bill-history.csv"
    change_order_path = data_dir / "Change-Order.csv"

    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    if billing_path.exists():
        billing_df = load_csv(billing_path)
        billing_df = compute_billing_risk(compute_payment_flags(billing_df))
        print(billing_df.head())
    else:
        print(f"Missing billing file: {billing_path}")

    if history_path.exists():
        history_df = load_csv(history_path)
        history_df = compute_payment_flags(history_df)
        print(history_df.head())
    else:
        print(f"Missing bill history file: {history_path}")

    if change_order_path.exists():
        change_order_df = load_csv(change_order_path)
        print(summarize_change_orders(change_order_df).head())
        print(summarize_change_order_reasons(change_order_df).head())
    else:
        print(f"Missing change order file: {change_order_path}")


if __name__ == "__main__":
    main()

>>>>>>> caa4aff (Add backend aggregation Datathon script with billing and risk scoring utilities)
