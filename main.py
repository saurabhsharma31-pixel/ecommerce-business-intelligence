from pathlib import Path
import sqlite3
from src.data_cleaning import clean_orders

ROOT = Path(__file__).resolve().parent
df = clean_orders()
db_path = ROOT / "data" / "ecommerce_analytics.db"
with sqlite3.connect(db_path) as conn:
    df.to_sql("orders",conn,if_exists="replace",index=False)
print(f"Prepared {len(df):,} cleaned orders.")
print(f"SQLite database created: {db_path}")
print("Launch dashboard with: streamlit run app/app.py")
