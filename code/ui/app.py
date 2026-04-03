import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

st.set_page_config(page_title="AeroScore Dashboard", layout="wide")
st.title("🚀 AeroScore Dashboard")
st.markdown("**Aircraft Asset Scoring System** — Credit-score style (300–850) with Environmental Impact")

# ========================== LOAD DATA ==========================
@st.cache_data
def load_data():
    scr_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(scr_dir,"..", "scored_dummy_aircraft_data.csv")
    df = pd.read_csv(file_path)
    df['month'] = pd.to_datetime(df['month'] + '-01')  # for proper time series
    return df

df = load_data()

# ========================== SIDEBAR FILTERS ==========================
st.sidebar.header("Filters")

# Aircraft type filter
types = sorted(df['aircraft_type'].unique())
selected_types = st.sidebar.multiselect("Aircraft Type", types, default=types[:3])

# Tail number filter (searchable)
tails = sorted(df['tail_number'].unique())
selected_tail = st.sidebar.selectbox("Select Tail Number (for detailed trend)", tails)

# Date range
min_date = df['month'].min()
max_date = df['month'].max()
date_range = st.sidebar.date_input("Month Range", [min_date.date(), max_date.date()])

# Apply filters
filtered_df = df[
    (df['aircraft_type'].isin(selected_types)) &
    (df['month'].dt.date.between(*date_range))
]

# ========================== OVERVIEW TAB ==========================
tab1, tab2, tab3 = st.tabs(["📊 Fleet Overview", "📈 Single Aircraft Deep Dive", "📋 Raw Data"])

with tab1:
    st.subheader("Fleet-Wide AeroScore Distribution")
    col1, col2 = st.columns([3, 2])

    with col1:
        fig_hist = px.histogram(filtered_df, x="AeroScore", nbins=50, color="Tier",
                                color_discrete_map={"Prime": "#00cc96", "Good": "#00b0f0", "Fair": "#ffcc00", "High Risk": "#ff4444"},
                                title="AeroScore Distribution (300–850)")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        tier_counts = filtered_df['Tier'].value_counts()
        fig_pie = px.pie(values=tier_counts.values, names=tier_counts.index, title="Tier Breakdown")
        st.plotly_chart(fig_pie, use_container_width=True)

    # Summary stats
    st.metric("Total Aircraft", df['tail_number'].nunique())
    st.metric("Average AeroScore", f"{filtered_df['AeroScore'].mean():.0f}")
    st.metric("Prime Assets", f"{(filtered_df['Tier'] == 'Prime').sum()}")

    # Environmental impact highlight
    st.subheader("🌍 Environmental Impact Overview")
    env_avg = filtered_df.groupby('aircraft_type')['env_impact'].mean().round(1)
    st.bar_chart(env_avg, use_container_width=True)

with tab2:
    st.subheader(f"Deep Dive: {selected_tail}")
    
    aircraft_df = df[df['tail_number'] == selected_tail].sort_values('month')
    
    # Main score trend
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=aircraft_df['month'], y=aircraft_df['AeroScore'],
                                   mode='lines+markers', name='AeroScore', line=dict(color='#00cc96', width=4)))
    fig_trend.update_layout(title="36-Month AeroScore Trend", xaxis_title="Month", yaxis_title="AeroScore (300-850)")
    st.plotly_chart(fig_trend, use_container_width=True)

    # Category breakdown over time
    st.subheader("Category Contribution Over Time")
    cat_df = aircraft_df.melt(id_vars=['month'], 
                              value_vars=['tech_health','op_reliability','maint_mgmt','util_wear','compliance','env_impact'],
                              var_name='Category', value_name='Score')
    fig_cat = px.area(cat_df, x='month', y='Score', color='Category', title="Weighted Category Scores (stacked)")
    st.plotly_chart(fig_cat, use_container_width=True)

    # Key metrics table
    st.subheader("Key Metrics (Last 6 Months)")
    last6 = aircraft_df.tail(6)[['month', 'AeroScore', 'Tier', 'env_impact', 'fuel_efficiency_dev_pct', 
                                 'next_major_check_months', 'mr_coverage_pct', 'tdr_12m_rolling']]
    st.dataframe(last6, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Raw Data Explorer")
    st.dataframe(filtered_df.head(1000), use_container_width=True)  # first 1000 rows for speed

# ========================== FOOTER / TBD ==========================
st.caption("Built for AeroScore project | Data: 43,200+ rows • 1,200+ aircraft • 15 types")
st.caption("TBD: Add historical risk trend line • SAF/CORSIA integration • Export to PDF report")