# E-Commerce Business Intelligence & Customer Analytics

An original portfolio project demonstrating end-to-end data analytics using Python, Pandas, SQLite, SQL, Plotly and Streamlit.

## Live Demo

##🚀 Live Demo

[Open E-Commerce Business Intelligence Dashboard] (https://ecommerce-business-intelligence-dyeabwv2bnzzog9qwvpgen.streamlit.app/)

Explore interactive sales analytics, profitability, customer segmentation, returns and operational performance.

## What it does
- Generates and analyzes 6,000 synthetic e-commerce orders from 2024–2025.
- Cleans and validates transaction-level data.
- Separates delivered recognized revenue from returned and cancelled order values.
- Builds an interactive executive dashboard with date, region, category and status filters.
- Analyzes category and regional performance, returns, cancellations and payment mix.
- Performs RFM customer segmentation (Recency, Frequency, Monetary).
- Includes ten SQL business analysis queries and CSV export.

## Important data disclosure
All order records, customers, prices, costs and financial outcomes are synthetic and generated for this portfolio demonstration. This project does not represent a real company or real-world performance. Do not claim synthetic findings as real business impact.

## Tech stack
Python, Pandas, NumPy, SQLite, SQL, Plotly, Streamlit.

## Run locally
```bash
python -m venv venv
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
streamlit run app/app.py
```
Open the local URL shown by Streamlit (usually http://localhost:8501).

## Project structure
```text
ecommerce-business-intelligence/
├── app/
│   └── app.py
├── data/
│   └── ecommerce_orders.csv
├── sql/
│   └── analysis_queries.sql
├── src/
│   └── data_cleaning.py
├── main.py
├── requirements.txt
└── README.md
```

## Business definitions
- **Order value:** discounted value of the order, regardless of final status.
- **Recognized revenue:** order value for Delivered orders only; zero for Returned and Cancelled orders in this simplified portfolio model.
- **Refund amount:** order value for Returned orders; this is a modeled refund, not a verified payment settlement.
- **Recognized profit:** recognized revenue less modeled cost for Delivered orders.
- **Return rate:** returned orders divided by all filtered orders.
- **Cancellation rate:** cancelled orders divided by all filtered orders.
- **RFM:** customer recency, delivered-order frequency and recognized revenue, calculated within the selected date range.

These definitions simplify real accounting. A production business would need shipping, partial returns, refund timing, taxes, payment settlement and inventory cost treatment.

## SQL
Ten queries are in `sql/analysis_queries.sql`, including aggregations, CASE expressions, CTEs, LAG, DENSE_RANK and RFM-style metrics.

## Deploy
Push the repository to GitHub, sign in at https://share.streamlit.io/, create an app from the repository, choose branch `main` and set the app file path to `app/app.py`.

## Resume example
**E-Commerce Business Intelligence & Customer Analytics | Python, SQL, Pandas, SQLite, Plotly, Streamlit**
- Built an interactive analytics dashboard to explore e-commerce sales, profitability, customer behaviour and order operations across 6,000 synthetic transactions.
- Developed a Pandas ETL pipeline with data validation and status-aware financial metrics.
- Wrote SQL analyses using aggregations, CTEs and window functions to investigate sales trends, category performance and customer value.
- Implemented RFM customer segmentation and interactive reporting with downloadable filtered data.

Customize the dashboard, independently verify its calculations and be prepared to explain the data model and business definitions before presenting it in interviews.
