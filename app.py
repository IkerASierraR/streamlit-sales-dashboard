import plotly.express as px
import streamlit as st

from src.data import breakdown, compute_kpis, filter_sales, load_sales, monthly_revenue

st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")


@st.cache_data
def get_data():
    return load_sales()


df = get_data()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
min_d, max_d = df["order_date"].min().date(), df["order_date"].max().date()
date_range = st.sidebar.date_input("Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
start, end = date_range if len(date_range) == 2 else (min_d, max_d)

regions = st.sidebar.multiselect("Region", sorted(df["region"].unique()))
categories = st.sidebar.multiselect("Category", sorted(df["category"].unique()))
channels = st.sidebar.multiselect("Channel", sorted(df["channel"].unique()))

st.sidebar.caption("Empty filter = all values.")

data = filter_sales(df, start, end, regions, categories, channels)

# ---------- Header ----------
st.title("📊 Sales Dashboard")
st.caption(f"Synthetic retail sales in Peru · {start:%d %b %Y} – {end:%d %b %Y} · {len(data):,} orders")

if data.empty:
    st.warning("No orders match the selected filters.")
    st.stop()

# ---------- KPIs ----------
k = compute_kpis(data)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Revenue", f"S/ {k['revenue']:,.0f}")
c2.metric("Profit", f"S/ {k['profit']:,.0f}")
c3.metric("Orders", f"{k['orders']:,}")
c4.metric("Avg. ticket", f"S/ {k['avg_ticket']:,.2f}")
c5.metric("Margin", f"{k['margin']:.1%}")

# ---------- Monthly trend ----------
st.subheader("Monthly trend")
monthly = monthly_revenue(data)
fig_trend = px.line(monthly, x="month", y=["revenue", "profit"], markers=True,
                    labels={"value": "S/", "month": "", "variable": ""})
fig_trend.update_layout(hovermode="x unified")
st.plotly_chart(fig_trend, width="stretch")

# ---------- Category & region ----------
left, right = st.columns(2)

with left:
    st.subheader("Revenue by category")
    by_cat = breakdown(data, "category")
    fig_cat = px.bar(by_cat, x="revenue", y="category", orientation="h",
                     labels={"revenue": "S/", "category": ""})
    fig_cat.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_cat, width="stretch")

with right:
    st.subheader("Revenue by region")
    by_reg = breakdown(data, "region")
    fig_reg = px.bar(by_reg, x="region", y="revenue", labels={"revenue": "S/", "region": ""})
    st.plotly_chart(fig_reg, width="stretch")

# ---------- Channel & heatmap ----------
left, right = st.columns(2)

with left:
    st.subheader("Online vs. store")
    by_ch = breakdown(data, "channel")
    fig_ch = px.pie(by_ch, names="channel", values="revenue", hole=0.5)
    st.plotly_chart(fig_ch, width="stretch")

with right:
    st.subheader("Category × region")
    pivot = data.pivot_table(index="category", columns="region", values="revenue",
                             aggfunc="sum", fill_value=0)
    fig_heat = px.imshow(pivot, text_auto=".2s", aspect="auto", color_continuous_scale="Blues",
                         labels={"color": "S/", "x": "", "y": ""})
    st.plotly_chart(fig_heat, width="stretch")

# ---------- Orders table ----------
st.subheader("Filtered orders")
table = data.sort_values("order_date", ascending=False)
st.dataframe(table, width="stretch", hide_index=True)
st.download_button(
    "⬇️ Download CSV",
    table.to_csv(index=False).encode("utf-8"),
    file_name="filtered_sales.csv",
    mime="text/csv",
)
