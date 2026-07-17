import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ---------------------------------------------------------
# 1. Page Configuration & Custom Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Retail Sales Performance",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a cleaner, premium look
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #F8F9FA;
    }
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #1F2937;
        font-weight: 600;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #6B7280;
    }
    /* Headers */
    h1, h2, h3 {
        color: #111827;
        font-family: 'Inter', sans-serif;
    }
    .report-title {
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .report-subtitle {
        color: #6B7280;
        font-size: 16px;
        margin-top: 0px;
        padding-top: 0px;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Data Loading and Preprocessing
# ---------------------------------------------------------
@st.cache_data
def load_and_prep_data():
    # โหลดข้อมูล
    df = pd.read_csv("bquxjob_6c32ae3b_19f6dfc7004.csv")
    
    # แปลงวันที่
    df['sales_date'] = pd.to_datetime(df['sales_date'], format='%d/%m/%Y', errors='coerce')
    
    # ฟังก์ชันทำความสะอาด time_range ที่อ่านยาก (เช่น 1-?.?. ให้เป็น 01:00-02:00)
    def clean_time_range(t):
        t = str(t)
        if '00-01' in t: return '12AM-1AM'
        elif t.startswith('1-'): return '1AM-2AM'
        elif t.startswith('2-'): return '2AM-3AM'
        elif t.startswith('3-'): return '3AM-4AM'
        elif t.startswith('4-'): return '4AM-5AM'
        elif t.startswith('5-'): return '5AM-6AM'
        elif t.startswith('6-'): return '6AM-7AM'
        elif t.startswith('7-'): return '7AM-8AM'
        elif t.startswith('8-'): return '8AM-9AM'
        elif t.startswith('9-'): return '9AM-10AM'
        elif t.startswith('10-'): return '10AM-11AM'
        elif t.startswith('11-'): return '11AM-12PM'
        elif '13-14' in t: return '1PM-2PM'
        elif '14-15' in t: return '2PM-3PM'
        elif '15-16' in t: return '3PM-4PM'
        elif '16-17' in t: return '4PM-5PM'
        elif '17-18' in t: return '5PM-6PM'
        elif '18-19' in t: return '6PM-7PM'
        elif '19-20' in t: return '7PM-8PM'
        elif '20-21' in t: return '8PM-9PM'
        elif '21-22' in t: return '9PM-10PM'
        elif '22-23' in t: return '10PM-11PM'
        elif '23-24' in t: return '11PM-12AM'
        else: return t
        
    df['clean_time'] = df['time_range'].apply(clean_time_range)
    
    # สร้างลำดับที่ถูกต้องสำหรับแกน X (เรียงตามเวลา)
    time_order = [
        '12AM-1AM', '1AM-2AM', '2AM-3AM', '3AM-4AM', '4AM-5AM', '5AM-6AM',
        '6AM-7AM', '7AM-8AM', '8AM-9AM', '9AM-10AM', '10AM-11AM', '11AM-12PM',
        '1PM-2PM', '2PM-3PM', '3PM-4PM', '4PM-5PM', '5PM-6PM', '6PM-7PM',
        '7PM-8PM', '8PM-9PM', '9PM-10PM', '10PM-11PM', '11PM-12AM'
    ]
    df['clean_time'] = pd.Categorical(df['clean_time'], categories=time_order, ordered=True)
    
    return df

df = load_and_prep_data()

# ---------------------------------------------------------
# 3. Sidebar Filters
# ---------------------------------------------------------
st.sidebar.markdown("### 🎛️ Dashboard Controls")

# Date Filter
min_date, max_date = df['sales_date'].min().date(), df['sales_date'].max().date()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

# Store Filter
stores = ['All'] + sorted(df['store_id'].unique().tolist())
selected_store = st.sidebar.selectbox("Select Store ID", stores)

# Apply Filters
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[(df['sales_date'].dt.date >= start_date) & (df['sales_date'].dt.date <= end_date)]
else:
    filtered_df = df.copy()

if selected_store != 'All':
    filtered_df = filtered_df[filtered_df['store_id'] == selected_store]

# ---------------------------------------------------------
# 4. Header & KPIs
# ---------------------------------------------------------
st.markdown('<p class="report-title">COMPREHENSIVE RETAIL SALES PERFORMANCE DASHBOARD</p>', unsafe_allow_html=True)
st.markdown('<p class="report-subtitle">Detailed Performance Insights & Hourly Velocity</p>', unsafe_allow_html=True)

# Calculate KPIs
total_sales = filtered_df['sales_amount'].sum()
total_transactions = len(filtered_df) # สมมติว่า 1 row = 1 transaction
avg_basket = total_sales / total_transactions if total_transactions > 0 else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Revenue", f"${total_sales:,.0f}")
with col2:
    st.metric("Total Transactions", f"{total_transactions:,}")
with col3:
    st.metric("Avg. Transaction Value", f"${avg_basket:,.2f}")
with col4:
    st.metric("Active Stores", f"{filtered_df['store_id'].nunique()}")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. Charts
# ---------------------------------------------------------
col_chart1, col_chart2 = st.columns([1.2, 1])

# --- Chart 1: Hourly Sales Velocity (Bar + Line) ---
with col_chart1:
    st.markdown("### HOURLY SALES VELOCITY AND TRANSACTION VOLUME")
    
    # Prepare data for Chart 1
    hourly_data = filtered_df.groupby('clean_time').agg(
        revenue=('sales_amount', 'sum'),
        transactions=('sales_amount', 'count') # นับจำนวน row แทน Volume
    ).reset_index()
    
    # Create combo chart using Plotly Graph Objects
    fig1 = go.Figure()

    # Add Bar chart for Revenue (Turquoise gradient)
    fig1.add_trace(
        go.Bar(
            x=hourly_data['clean_time'],
            y=hourly_data['revenue'],
            name="Sales Amount",
            marker_color='#38B2AC', # โทนเทอร์ควอยซ์
            yaxis='y'
        )
    )

    # Add Line chart for Transactions (Light Blue)
    fig1.add_trace(
        go.Scatter(
            x=hourly_data['clean_time'],
            y=hourly_data['transactions'],
            name="Transaction Volume",
            mode='lines+markers',
            marker=dict(color='#81E6D9', size=8),
            line=dict(width=3, color='#81E6D9'),
            yaxis='y2'
        )
    )

    # Layout styling
    fig1.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Sales Amount ($)", showgrid=True, gridcolor='#F3F4F6'),
        yaxis2=dict(title="Transactions", overlaying='y', side='right', showgrid=False),
        xaxis=dict(showgrid=False, tickangle=-45),
        hovermode="x unified"
    )
    st.plotly_chart(fig1, use_container_width=True)


# --- Chart 2: Top 10 Stores (Horizontal Bar with details) ---
with col_chart2:
    st.markdown("### TOP 10 STORES BY REVENUE")
    
    # Prepare data for Chart 2
    store_data = filtered_df.groupby('store_id').agg(
        revenue=('sales_amount', 'sum'),
        transactions=('sales_amount', 'count')
    ).reset_index().sort_values('revenue', ascending=True).tail(10) # เอา 10 อันดับแรก เรียงจากน้อยไปมากให้กราฟสวย
    
    store_data['store_id_str'] = store_data['store_id'].astype(str)
    
    # Create horizontal bar chart
    fig2 = go.Figure()
    
    fig2.add_trace(
        go.Bar(
            y=store_data['store_id_str'],
            x=store_data['revenue'],
            orientation='h',
            marker=dict(
                color=store_data['revenue'],
                colorscale=['#FCA5A5', '#EF4444', '#B91C1C'] # โทนพีช - แดง
            ),
            text=store_data['revenue'].apply(lambda x: f"${x:,.0f}"),
            textposition='auto',
            hovertemplate="<b>Store: %{y}</b><br>Revenue: $%{x:,.2f}<br>Transactions: %{customdata:,}<extra></extra>",
            customdata=store_data['transactions']
        )
    )
    
    fig2.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(title="Revenue ($)", showgrid=True, gridcolor='#F3F4F6'),
        yaxis=dict(title="Store ID", showgrid=False, type='category')
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------
# 6. Raw Data Table
# ---------------------------------------------------------
with st.expander("View Raw Data Details"):
    st.dataframe(
        filtered_df[['sales_date', 'clean_time', 'store_id', 'item_code', 'sales_amount', 'sales_quantity']],
        use_container_width=True
    )