from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "ecommerce_orders.csv"
CLEAN_PATH = ROOT / "data" / "ecommerce_orders_clean.csv"

def clean_orders(input_path=RAW_PATH, output_path=CLEAN_PATH):
    df = pd.read_csv(input_path)
    df.columns = df.columns.str.strip().str.lower()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    numeric = ["quantity","unit_price","discount_pct","gross_sales","order_value",
               "cost","refund_amount","recognized_revenue","recognized_cost","recognized_profit"]
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.drop_duplicates(subset=["order_id"])
    df = df.dropna(subset=["order_id","order_date","customer_id","category","order_status"])
    for col in ["region","product","payment_method"]:
        df[col] = df[col].fillna("Unknown")
    df["quantity"] = df["quantity"].fillna(1).clip(lower=1)
    df["unit_price"] = df["unit_price"].fillna(df["unit_price"].median()).clip(lower=0)
    df["discount_pct"] = df["discount_pct"].fillna(0).clip(0,1)

    # Recalculate order value consistently. Recognized revenue is only for delivered orders.
    df["gross_sales"] = (df["unit_price"] * df["quantity"]).round(2)
    df["order_value"] = (df["gross_sales"] * (1-df["discount_pct"])).round(2)
    df["cost"] = df["cost"].fillna(df["gross_sales"] * 0.60).clip(lower=0).round(2)
    df["refund_amount"] = df.apply(
        lambda r: r["order_value"] if r["order_status"] == "Returned" else 0.0, axis=1
    ).round(2)
    df["recognized_revenue"] = df.apply(
        lambda r: r["order_value"] if r["order_status"] == "Delivered" else 0.0, axis=1
    ).round(2)
    df["recognized_cost"] = df.apply(
        lambda r: r["cost"] if r["order_status"] == "Delivered" else 0.0, axis=1
    ).round(2)
    df["recognized_profit"] = (df["recognized_revenue"]-df["recognized_cost"]).round(2)
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month
    df["month_name"] = df["order_date"].dt.strftime("%b")
    df["year_month"] = df["order_date"].dt.to_period("M").astype(str)
    df["profit_margin_pct"] = (
        df["recognized_profit"] / df["recognized_revenue"].replace(0, pd.NA) * 100
    ).fillna(0).round(2)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df

if __name__ == "__main__":
    cleaned = clean_orders()
    print(f"Cleaned {len(cleaned):,} orders. Saved to {CLEAN_PATH}")
