from pathlib import Path
import sys, sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_cleaning import clean_orders

st.set_page_config(page_title="E-Commerce Business Intelligence", page_icon="📈", layout="wide")
st.title("📈 E-Commerce Business Intelligence")
st.caption("Sales performance, customer behaviour and operational analytics | Synthetic portfolio dataset")

@st.cache_data
def load_orders():
    clean_path = ROOT / "data" / "ecommerce_orders_clean.csv"
    if not clean_path.exists():
        df = clean_orders()
    else:
        df = pd.read_csv(clean_path, parse_dates=["order_date"])
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df

df = load_orders()
st.sidebar.header("Explore the data")
min_date, max_date = df.order_date.min().date(), df.order_date.max().date()
date_value = st.sidebar.date_input("Order date range", value=(min_date,max_date), min_value=min_date, max_value=max_date)
if isinstance(date_value, (tuple,list)):
    if len(date_value)==2: start_date,end_date = date_value
    elif len(date_value)==1: start_date=end_date=date_value[0]
    else: start_date,end_date=min_date,max_date
else:
    start_date=end_date=date_value
regions_all = sorted(df.region.unique())
cats_all = sorted(df.category.unique())
status_all = sorted(df.order_status.unique())
regions = st.sidebar.multiselect("Region", regions_all, default=[x for x in regions_all if x!="Unknown"])
categories = st.sidebar.multiselect("Category", cats_all, default=cats_all)
statuses = st.sidebar.multiselect("Order status", status_all, default=status_all)

f = df[
    df.order_date.dt.date.between(start_date,end_date) &
    df.region.isin(regions) &
    df.category.isin(categories) &
    df.order_status.isin(statuses)
].copy()

if f.empty:
    st.warning("No orders match the selected filters. Adjust the date, region, category or status.")
    st.stop()

delivered = f[f.order_status=="Delivered"].copy()
total_orders = len(f)
delivered_orders = len(delivered)
cancelled_orders = int((f.order_status=="Cancelled").sum())
returned_orders = int((f.order_status=="Returned").sum())
recognized_revenue = delivered.recognized_revenue.sum()
recognized_profit = delivered.recognized_profit.sum()
profit_margin = recognized_profit/recognized_revenue*100 if recognized_revenue else 0
refunds = f.refund_amount.sum()
return_rate = returned_orders/total_orders*100 if total_orders else 0
cancel_rate = cancelled_orders/total_orders*100 if total_orders else 0

st.subheader("Executive overview")
k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Recognized revenue", f"₹{recognized_revenue/100000:.2f}L")
k2.metric("Recognized profit", f"₹{recognized_profit/100000:.2f}L")
k3.metric("All orders", f"{total_orders:,}")
k4.metric("Profit margin", f"{profit_margin:.1f}%")
k5.metric("Refund value", f"₹{refunds/100000:.2f}L")

st.caption(f"Delivered: {delivered_orders:,} | Returned: {returned_orders:,} ({return_rate:.1f}%) | Cancelled: {cancelled_orders:,} ({cancel_rate:.1f}%)")
st.divider()

left,right = st.columns((1.5,1))
with left:
    st.subheader("Monthly recognized revenue")
    monthly = delivered.groupby("year_month",as_index=False).agg(revenue=("recognized_revenue","sum"),profit=("recognized_profit","sum"))
    if not monthly.empty:
        fig = px.line(monthly,x="year_month",y=["revenue","profit"],markers=True,
                      labels={"year_month":"Month","value":"INR","variable":"Metric"})
        fig.update_layout(legend_title_text="",xaxis_tickangle=-45)
        st.plotly_chart(fig,use_container_width=True)
    else:
        st.info("No delivered orders in this filter selection.")
with right:
    st.subheader("Order status mix")
    status_counts = f.order_status.value_counts().rename_axis("status").reset_index(name="orders")
    fig = px.pie(status_counts,names="status",values="orders",hole=.48)
    st.plotly_chart(fig,use_container_width=True)

left,right = st.columns(2)
with left:
    st.subheader("Category profitability")
    category_perf = delivered.groupby("category",as_index=False).agg(
        revenue=("recognized_revenue","sum"),profit=("recognized_profit","sum"))
    if not category_perf.empty:
        fig=px.bar(category_perf,x="category",y="profit",color="revenue",
                   labels={"profit":"Recognized profit (₹)","revenue":"Revenue (₹)"})
        st.plotly_chart(fig,use_container_width=True)
with right:
    st.subheader("Regional revenue")
    region_perf=delivered.groupby("region",as_index=False).recognized_revenue.sum()
    if not region_perf.empty:
        fig=px.bar(region_perf,x="region",y="recognized_revenue",
                   labels={"recognized_revenue":"Recognized revenue (₹)"})
        st.plotly_chart(fig,use_container_width=True)

st.subheader("Customer RFM segmentation")
st.caption("RFM is calculated using delivered orders in the selected date range. Recency is measured from the latest date in the filtered dataset.")
if not delivered.empty:
    snapshot = delivered.order_date.max() + pd.Timedelta(days=1)
    rfm = delivered.groupby("customer_id").agg(
        recency=("order_date",lambda x:(snapshot-x.max()).days),
        frequency=("order_id","nunique"),
        monetary=("recognized_revenue","sum")
    ).reset_index()
    # Quantile scoring with rank(method='first') handles tied values safely.
    rfm["R"] = pd.qcut(rfm.recency.rank(method="first"),5,labels=[5,4,3,2,1]).astype(int)
    rfm["F"] = pd.qcut(rfm.frequency.rank(method="first"),5,labels=[1,2,3,4,5]).astype(int)
    rfm["M"] = pd.qcut(rfm.monetary.rank(method="first"),5,labels=[1,2,3,4,5]).astype(int)
    rfm["RFM_score"] = rfm[["R","F","M"]].sum(axis=1)
    def segment(row):
        if row.R >= 4 and row.F >= 4 and row.M >= 4: return "Champions"
        if row.F >= 4 and row.M >= 3: return "Loyal customers"
        if row.R >= 4 and row.F <= 2: return "New / promising"
        if row.R <= 2 and row.F >= 3: return "At risk"
        if row.R <= 2 and row.F <= 2: return "Hibernating"
        return "Potential loyalists"
    rfm["segment"] = rfm.apply(segment,axis=1)
    seg = rfm.segment.value_counts().rename_axis("segment").reset_index(name="customers")
    c1,c2=st.columns([1,1])
    with c1:
        st.plotly_chart(px.bar(seg,x="segment",y="customers",color="segment"),use_container_width=True)
    with c2:
        st.dataframe(rfm.sort_values("monetary",ascending=False).head(15),use_container_width=True,hide_index=True)
else:
    st.info("Select Delivered in Order status to calculate RFM customer segments.")

st.subheader("Returns and cancellations")
ops = f.groupby("order_status",as_index=False).agg(orders=("order_id","count"),order_value=("order_value","sum"),refunds=("refund_amount","sum"))
st.dataframe(ops,use_container_width=True,hide_index=True)

st.subheader("Business observations")
if not delivered.empty:
    top_cat=category_perf.sort_values("revenue",ascending=False).iloc[0]
    top_region=region_perf.sort_values("recognized_revenue",ascending=False).iloc[0]
    st.write(f"- Highest revenue category in the selected filters: **{top_cat.category}** (₹{top_cat.revenue:,.0f}).")
    st.write(f"- Highest revenue region: **{top_region.region}** (₹{top_region.recognized_revenue:,.0f}).")
    st.write(f"- Delivered-order profit margin: **{profit_margin:.1f}%**.")
st.write(f"- Return rate: **{return_rate:.1f}%**; cancellation rate: **{cancel_rate:.1f}%**.")

st.subheader("Filtered order details")
st.dataframe(f.sort_values("order_date",ascending=False),use_container_width=True,hide_index=True)
st.download_button("Download filtered orders (CSV)",f.to_csv(index=False).encode("utf-8"),
                   file_name="filtered_ecommerce_orders.csv",mime="text/csv")

with st.expander("Data quality report"):
    missing=df.isna().sum().rename("missing_values").reset_index(names="column")
    st.write(f"{len(df):,} cleaned rows | {len(df.columns)} columns | {df.order_id.nunique():,} unique order IDs")
    st.dataframe(missing,use_container_width=True,hide_index=True)

st.caption("Portfolio demonstration only. All transactions, customers and financial values are synthetic; no real-company performance is represented.")
