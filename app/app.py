from pathlib import Path
import sys
import sqlite3  # Retained for compatibility with the existing project structure.

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # Retained for future chart extensions.
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_cleaning import clean_orders

# Page configuration must be the first Streamlit command.
st.set_page_config(
    page_title="E-Commerce Business Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Dark navy UI theme. This changes presentation only, not business calculations.
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
  

/* Main dashboard heading */
.hero {
    padding: 28px 32px;
    margin: 8px 0 30px 0;
    border: 1px solid rgba(85, 166, 255, 0.3);
    border-radius: 18px;
    background: linear-gradient(
        115deg,
        #172e4b 0%,
        #12243a 55%,
        #102d38 100%
    );
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
}

.hero-kicker {
    color: #70b4ff !important;
    font-size: 12px;
    font-weight: 750;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.hero-title {
    color: #f4f8ff !important;
    font-size: 36px;
    font-weight: 800;
    line-height: 1.2;
    letter-spacing: -1px;
    margin: 0;
}

.hero-subtitle {
    color: #b7c8dc !important;
    font-size: 15px;
    line-height: 1.6;
    margin-top: 12px;
}

/* Section headings */
.section-label {
    color: #69adff !important;
    font-size: 12px;
    font-weight: 750;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    margin: 28px 0 12px 0;
}

/* Chart and content headings */
h2 {
    color: #f1f6ff !important;
    font-size: 23px !important;
    font-weight: 750 !important;
    letter-spacing: -0.5px;
}

h3 {
    color: #e4edfa !important;
    font-size: 19px !important;
    font-weight: 700 !important;
}

/* Improve supporting text */
[data-testid="stCaptionContainer"] {
    color: #9aabc2 !important;
    font-size: 13px;
}


/* ==================================
   COLOURED EXECUTIVE KPI CARDS
================================== */

/* Revenue - Blue */
[data-testid="stHorizontalBlock"] [data-testid="stMetric"]:nth-child(1) {
    background: linear-gradient(145deg, #142D43, #102337) !important;
    border: 1px solid #258BCB !important;
}

/* Profit - Green */
[data-testid="stHorizontalBlock"] [data-testid="stMetric"]:nth-child(2) {
    background: linear-gradient(145deg, #142F2C, #102520) !important;
    border: 1px solid #239B78 !important;
}

/* Orders - Purple */
[data-testid="stHorizontalBlock"] [data-testid="stMetric"]:nth-child(3) {
    background: linear-gradient(145deg, #292747, #1D1B35) !important;
    border: 1px solid #8272DB !important;
}

/* Profit margin - Gold */
[data-testid="stHorizontalBlock"] [data-testid="stMetric"]:nth-child(4) {
    background: linear-gradient(145deg, #342C1D, #282116) !important;
    border: 1px solid #C18C35 !important;
}

/* Refunds - Rose */
[data-testid="stHorizontalBlock"] [data-testid="stMetric"]:nth-child(5) {
    background: linear-gradient(145deg, #35232C, #281B25) !important;
    border: 1px solid #C15D82 !important;
}

/* Common KPI card appearance */
[data-testid="stMetric"] {
    border-radius: 16px !important;
    padding: 22px 20px !important;
    min-height: 125px !important;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.18);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

/* Hover effect */
[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.3);
}

/* KPI labels */
[data-testid="stMetricLabel"] {
    color: #C5D3E5 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

/* KPI numbers */
[data-testid="stMetricValue"] {
    color: #F4F7FF !important;
    font-size: 30px !important;
    font-weight: 750 !important;
}

/* ==================================
   CHART CONTAINERS
================================== */

div[data-testid="stElementContainer"]:has(
    [data-testid="stPlotlyChart"]
) {
    background: linear-gradient(
        145deg,
        #111F32,
        #0F1A2B
    ) !important;
    border: 1px solid #263E5B !important;
    border-radius: 16px !important;
    padding: 16px !important;
    margin-bottom: 18px !important;
    box-shadow: 0 8px 22px rgba(0, 0, 0, 0.18);
}

/* Chart headings */
h2, h3 {
    color: #EAF2FF !important;
    font-weight: 750 !important;
}

/* Chart captions */
[data-testid="stCaptionContainer"] {
    color: #9EB2CC !important;
}

/* Chart spacing */
[data-testid="stPlotlyChart"] {
    border-radius: 12px !important;
    overflow: hidden;
}


    </style>
    """,
    unsafe_allow_html=True,
)

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Arial, sans-serif", color="#dce7f5", size=12),
    margin=dict(l=12, r=12, t=36, b=12),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#c7d5e6")),
    hoverlabel=dict(bgcolor="#152238", font_color="#f3f7ff"),
)
ACCENT = ["#55a6ff", "#35c6b0", "#a78bfa", "#f5b85b", "#f17c9a", "#7dd3fc"]


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

# Sidebar filters: same filter fields and defaults as the existing dashboard.
st.sidebar.markdown("## 🎛️ Explore the data")
st.sidebar.caption("Adjust filters to update every section of the dashboard.")
min_date, max_date = df.order_date.min().date(), df.order_date.max().date()
date_value = st.sidebar.date_input(
    "Order date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(date_value, (tuple, list)):
    if len(date_value) == 2:
        start_date, end_date = date_value
    elif len(date_value) == 1:
        start_date = end_date = date_value[0]
    else:
        start_date, end_date = min_date, max_date
else:
    start_date = end_date = date_value

regions_all = sorted(df.region.unique())
cats_all = sorted(df.category.unique())
status_all = sorted(df.order_status.unique())
regions = st.sidebar.multiselect(
    "Region", regions_all, default=[x for x in regions_all if x != "Unknown"]
)
categories = st.sidebar.multiselect("Category", cats_all, default=cats_all)
statuses = st.sidebar.multiselect("Order status", status_all, default=status_all)

f = df[
    df.order_date.dt.date.between(start_date, end_date)
    & df.region.isin(regions)
    & df.category.isin(categories)
    & df.order_status.isin(statuses)
].copy()

# Header
st.markdown(
    """
    <div class="hero">
      <div class="hero-kicker">Business intelligence · Portfolio dashboard</div>
      <div class="hero-title">📈 E-Commerce Business Intelligence</div>
      <div class="hero-subtitle">Sales performance, customer behaviour and operational analytics </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if f.empty:
    st.warning("No orders match the selected filters. Adjust the date, region, category or status.")
    st.stop()

# Keep the original business calculations unchanged.
delivered = f[f.order_status == "Delivered"].copy()
total_orders = len(f)
delivered_orders = len(delivered)
cancelled_orders = int((f.order_status == "Cancelled").sum())
returned_orders = int((f.order_status == "Returned").sum())
recognized_revenue = delivered.recognized_revenue.sum()
recognized_profit = delivered.recognized_profit.sum()
profit_margin = recognized_profit / recognized_revenue * 100 if recognized_revenue else 0
refunds = f.refund_amount.sum()
return_rate = returned_orders / total_orders * 100 if total_orders else 0
cancel_rate = cancelled_orders / total_orders * 100 if total_orders else 0

st.markdown('<div class="section-label">Executive overview</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Recognized revenue", f"₹{recognized_revenue/100000:.2f}L")
k2.metric("Recognized profit", f"₹{recognized_profit/100000:.2f}L")
k3.metric("All orders", f"{total_orders:,}")
k4.metric("Profit margin", f"{profit_margin:.1f}%")
k5.metric("Refund value", f"₹{refunds/100000:.2f}L")

st.caption(
    f"Delivered: {delivered_orders:,}  ·  Returned: {returned_orders:,} ({return_rate:.1f}%)  ·  Cancelled: {cancelled_orders:,} ({cancel_rate:.1f}%)"
)
st.divider()

# Sales and order-status charts.
st.markdown('<div class="section-label">Sales performance</div>', unsafe_allow_html=True)
left, right = st.columns((1.5, 1))
with left:
    st.subheader("Monthly recognized revenue")
    monthly = delivered.groupby("year_month", as_index=False).agg(
        revenue=("recognized_revenue", "sum"),
        profit=("recognized_profit", "sum"),
    )
    if not monthly.empty:
        fig = px.line(
            monthly,
            x="year_month",
            y=["revenue", "profit"],
            markers=True,
            color_discrete_sequence=["#55a6ff", "#35c6b0"],
            labels={"year_month": "Month", "value": "INR", "variable": "Metric"},
        )
        fig.update_layout(**PLOTLY_LAYOUT, legend_title_text="", xaxis_tickangle=-35)
        fig.update_traces(line=dict(width=3), marker=dict(size=7))
        fig.update_layout(
    paper_bgcolor="#111F32",
    plot_bgcolor="#111F32",
    font=dict(
        family="Arial",
        color="#EAF2FF",
        size=14
    ),
    xaxis=dict(
        title=dict(text="Month", font=dict(color="#FFFFFF", size=15)),
        tickfont=dict(color="#DCE8F7", size=12),
        showgrid=False,
        zeroline=False
    ),
    yaxis=dict(
        title=dict(text="Revenue / Profit (INR)", font=dict(color="#FFFFFF", size=15)),
        tickfont=dict(color="#DCE8F7", size=12),
        gridcolor="#34465E",
        gridwidth=1,
        zeroline=False
    ),
    legend=dict(
        font=dict(color="#FFFFFF", size=13),
        bgcolor="rgba(17,31,50,0)"
    ),
    hoverlabel=dict(
        bgcolor="#1B304A",
        font=dict(color="#FFFFFF", size=14)
    )
)


        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=8)
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No delivered orders in this filter selection.")

with right:
    st.subheader("Order status mix")
    status_counts = f.order_status.value_counts().rename_axis("status").reset_index(name="orders")
    fig = px.pie(
        status_counts,
        names="status",
        values="orders",
        hole=0.58,
        color_discrete_sequence=ACCENT,
    )
    
    fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#111F32",
            plot_bgcolor="#111F32",
            font=dict(color="#FFFFFF", size=14),
            legend=dict(
                font=dict(color="#FFFFFF", size=14)
            ),
            margin=dict(l=20, r=20, t=35, b=20)
        )

    fig.update_traces(
            hole=0.62,
            textposition="inside",
            textinfo="percent",
            textfont=dict(
                color="#0B1220",
                size=16,
                family="Arial",
                weight="bold"
            ),
            marker=dict(
                colors=["#55A6FF", "#2CC6AD", "#A78BFA"],
                line=dict(color="#111F32", width=3)
            ),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Orders: %{value:,}<br>"
                "Share: %{percent}<extra></extra>"
            )
        )

    st.plotly_chart(fig, use_container_width=True)

# Category and regional analysis.
st.markdown('<div class="section-label">Product and regional analysis</div>', unsafe_allow_html=True)
left, right = st.columns(2)
with left:
    st.subheader("Category profitability")
    category_perf = delivered.groupby("category", as_index=False).agg(
        revenue=("recognized_revenue", "sum"),
        profit=("recognized_profit", "sum"),
    )
    if not category_perf.empty:
        fig = px.bar(
            category_perf,
            x="category",
            y="profit",
            color="revenue",
            color_continuous_scale=[[0, "#17365b"], [0.55, "#287ec2"], [1, "#55c6d7"]],
            labels={"profit": "Recognized profit (₹)", "revenue": "Revenue (₹)"},
        )
        fig.update_layout(**PLOTLY_LAYOUT, coloraxis_colorbar=dict(title="Revenue"))
        fig.update_traces(marker_line_width=0, opacity=0.92)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No delivered orders for category profitability.")
with right:
    st.subheader("Regional revenue")
    region_perf = delivered.groupby("region", as_index=False).recognized_revenue.sum()
    if not region_perf.empty:
        fig = px.bar(
            region_perf,
            x="region",
            y="recognized_revenue",
            color="region",
            color_discrete_sequence=ACCENT,
            labels={"recognized_revenue": "Recognized revenue (₹)"},
        )
        fig.update_layout(**PLOTLY_LAYOUT, showlegend=False)
        fig.update_traces(marker_line_width=0, opacity=0.92)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No delivered orders for regional revenue.")

# Customer RFM segmentation: same scoring and segment rules as the original.
st.markdown('<div class="section-label">Customer intelligence</div>', unsafe_allow_html=True)
st.subheader("Customer RFM segmentation")
st.caption(
    "RFM is calculated using delivered orders in the selected date range. Recency is measured from the latest date in the filtered dataset."
)
if not delivered.empty:
    snapshot = delivered.order_date.max() + pd.Timedelta(days=1)
    rfm = delivered.groupby("customer_id").agg(
        recency=("order_date", lambda x: (snapshot - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("recognized_revenue", "sum"),
    ).reset_index()
    # Quantile scoring with rank(method='first') handles tied values safely.
    rfm["R"] = pd.qcut(rfm.recency.rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F"] = pd.qcut(rfm.frequency.rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M"] = pd.qcut(rfm.monetary.rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM_score"] = rfm[["R", "F", "M"]].sum(axis=1)

    def segment(row):
        if row.R >= 4 and row.F >= 4 and row.M >= 4:
            return "Champions"
        if row.F >= 4 and row.M >= 3:
            return "Loyal customers"
        if row.R >= 4 and row.F <= 2:
            return "New / promising"
        if row.R <= 2 and row.F >= 3:
            return "At risk"
        if row.R <= 2 and row.F <= 2:
            return "Hibernating"
        return "Potential loyalists"

    rfm["segment"] = rfm.apply(segment, axis=1)
    seg = rfm.segment.value_counts().rename_axis("segment").reset_index(name="customers")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.caption("Customer distribution by segment")
        fig = px.bar(
            seg,
            x="segment",
            y="customers",
            color="segment",
            color_discrete_sequence=ACCENT,
        )
        fig.update_layout(**PLOTLY_LAYOUT, showlegend=False, xaxis_tickangle=-25)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.caption("Top customers by recognized spend")
        st.dataframe(
            rfm.sort_values("monetary", ascending=False).head(15),
            use_container_width=True,
            hide_index=True,
        )
else:
    st.info("Select Delivered in Order status to calculate RFM customer segments.")

# Returns, cancellations and business observations.
st.markdown('<div class="section-label">Operations and insights</div>', unsafe_allow_html=True)
st.subheader("Returns and cancellations")
ops = f.groupby("order_status", as_index=False).agg(
    orders=("order_id", "count"),
    order_value=("order_value", "sum"),
    refunds=("refund_amount", "sum"),
)
st.dataframe(ops, use_container_width=True, hide_index=True)

st.subheader("Business observations")
if not delivered.empty:
    top_cat = category_perf.sort_values("revenue", ascending=False).iloc[0]
    top_region = region_perf.sort_values("recognized_revenue", ascending=False).iloc[0]
    st.write(f"- Highest revenue category in the selected filters: **{top_cat.category}** (₹{top_cat.revenue:,.0f}).")
    st.write(f"- Highest revenue region: **{top_region.region}** (₹{top_region.recognized_revenue:,.0f}).")
    st.write(f"- Delivered-order profit margin: **{profit_margin:.1f}%**.")
st.write(f"- Return rate: **{return_rate:.1f}%**; cancellation rate: **{cancel_rate:.1f}%**.")

# Transaction-level data and CSV download.
st.markdown('<div class="section-label">Data explorer</div>', unsafe_allow_html=True)
st.subheader("Filtered order details")
st.caption(f"Showing {len(f):,} orders matching the current filters.")
st.dataframe(f.sort_values("order_date", ascending=False), use_container_width=True, hide_index=True)
st.download_button(
    "⬇️ Download filtered orders (CSV)",
    f.to_csv(index=False).encode("utf-8"),
    file_name="filtered_ecommerce_orders.csv",
    mime="text/csv",
)

with st.expander("Data quality report"):
    missing = df.isna().sum().reset_index()
    missing.columns = ["column", "missing_values"]

    st.write(
        f"{len(df):,} cleaned rows | {len(df.columns)} columns | "
        f"{df.order_id.nunique():,} unique order IDs"
    )

    st.dataframe(
        missing,
        use_container_width=True,
        hide_index=True
    )

st.divider()
st.caption(
    "Portfolio demonstration only. All transactions, customers and financial values are synthetic; no real-company performance is represented."
)
