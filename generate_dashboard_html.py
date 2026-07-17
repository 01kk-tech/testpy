import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

df = pd.read_csv('bquxjob_6c32ae3b_19f6dfc7004.csv')
df['sales_date'] = pd.to_datetime(df['sales_date'], format='%d/%m/%Y', errors='coerce')

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

df['time_period'] = df['time_range'].apply(clean_time_range)

time_order = ['12AM-1AM','1AM-2AM','2AM-3AM','3AM-4AM','4AM-5AM','5AM-6AM',
    '6AM-7AM','7AM-8AM','8AM-9AM','9AM-10AM','10AM-11AM','11AM-12PM',
    '1PM-2PM','2PM-3PM','3PM-4PM','4PM-5PM','5PM-6PM','6PM-7PM',
    '7PM-8PM','8PM-9PM','9PM-10PM','10PM-11PM','11PM-12AM']

# --- Chart 1: Hourly Sales Velocity ---
hourly = df.groupby('time_period').agg(
    revenue=('sales_amount', 'sum'),
    transactions=('sales_amount', 'count')
).reset_index()
hourly['time_period'] = pd.Categorical(hourly['time_period'], categories=time_order, ordered=True)
hourly = hourly.sort_values('time_period')

fig1 = go.Figure()
fig1.add_trace(go.Bar(x=hourly['time_period'], y=hourly['revenue'], name="Sales Amount", marker_color='#38B2AC', yaxis='y'))
fig1.add_trace(go.Scatter(x=hourly['time_period'], y=hourly['transactions'], name="Transactions", mode='lines+markers',
    marker=dict(color='#81E6D9', size=8), line=dict(width=3, color='#81E6D9'), yaxis='y2'))
fig1.update_layout(
    title=dict(text="Hourly Sales Velocity", font=dict(size=18)),
    plot_bgcolor='white', height=380, margin=dict(l=40,r=40,t=50,b=40),
    yaxis=dict(title="Sales ($)", showgrid=True, gridcolor='#F3F4F6'),
    yaxis2=dict(title="Transactions", overlaying='y', side='right', showgrid=False),
    xaxis=dict(showgrid=False, tickangle=-45),
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
chart1_html = fig1.to_html(full_html=False, include_plotlyjs=False)

# --- Chart 2: Top Stores ---
store = df.groupby('store_id').agg(
    revenue=('sales_amount', 'sum'),
    transactions=('sales_amount', 'count')
).reset_index().sort_values('revenue', ascending=True)

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    y=store['store_id'].astype(str), x=store['revenue'], orientation='h',
    marker=dict(color=store['revenue'], colorscale=['#FCA5A5', '#EF4444', '#B91C1C']),
    text=store['revenue'].apply(lambda x: f"${x:,.0f}"), textposition='auto',
    hovertemplate="<b>Store: %{y}</b><br>Revenue: $%{x:,.2f}<br>Transactions: %{customdata:,}<extra></extra>",
    customdata=store['transactions']
))
fig2.update_layout(
    title=dict(text="Top Stores by Revenue", font=dict(size=18)),
    plot_bgcolor='white', height=280, margin=dict(l=30,r=30,t=50,b=20),
    xaxis=dict(title="Revenue ($)", showgrid=True, gridcolor='#F3F4F6'),
    yaxis=dict(title="Store ID", showgrid=False, type='category')
)
chart2_html = fig2.to_html(full_html=False, include_plotlyjs=False)

# --- Chart 3: Daily Revenue Trend ---
daily = df.groupby('sales_date').agg(revenue=('sales_amount', 'sum')).reset_index().sort_values('sales_date')

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=daily['sales_date'], y=daily['revenue'], mode='lines+markers',
    name="Daily Revenue", line=dict(color='#38B2AC', width=3),
    marker=dict(color='#38B2AC', size=6), fill='tozeroy', fillcolor='rgba(56, 178, 172, 0.1)'))
fig3.update_layout(
    title=dict(text="Daily Revenue Trend", font=dict(size=18)),
    plot_bgcolor='white', height=350, margin=dict(l=40,r=20,t=50,b=40),
    xaxis=dict(title="Date", showgrid=False, rangeselector=dict(
        buttons=[dict(count=7, label="7d", step="day", stepmode="backward"),
                 dict(count=14, label="14d", step="day", stepmode="backward"),
                 dict(count=1, label="1m", step="month", stepmode="backward"),
                 dict(step="all")])),
    yaxis=dict(title="Revenue ($)", showgrid=True, gridcolor='#F3F4F6'),
    hovermode="x unified"
)
chart3_html = fig3.to_html(full_html=False, include_plotlyjs=False)

# --- Chart 4: Revenue by Day of Week ---
df['day_name'] = df['sales_date'].dt.day_name()
day_order_list = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
dow = df.groupby('day_name').agg(revenue=('sales_amount', 'sum')).reindex(day_order_list).reset_index()

fig4 = go.Figure()
fig4.add_trace(go.Bar(x=dow['day_name'], y=dow['revenue'],
    marker_color=['#FCA5A5','#F87171','#EF4444','#DC2626','#B91C1C','#991B1B','#7F1D1D'],
    text=dow['revenue'].apply(lambda x: f"${x:,.0f}"), textposition='auto',
    hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>"))
fig4.update_layout(
    title=dict(text="Revenue by Day of Week", font=dict(size=18)),
    plot_bgcolor='white', height=320, margin=dict(l=40,r=20,t=50,b=40),
    xaxis=dict(title="Day", showgrid=False),
    yaxis=dict(title="Revenue ($)", showgrid=True, gridcolor='#F3F4F6')
)
chart4_html = fig4.to_html(full_html=False, include_plotlyjs=False)

# ============================================================
# รวมทุก Charts ในหน้า HTML เดียวกัน (Interactive + SPA)
# ============================================================
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sales Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: #F8F9FA;
            padding: 20px;
            color: #111827;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }}
        .header p {{
            color: #6B7280;
            font-size: 14px;
        }}
        .kpi-row {{
            display: flex;
            gap: 16px;
            margin-bottom: 24px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        .kpi-card {{
            background: white;
            border-radius: 12px;
            padding: 20px 28px;
            flex: 1;
            min-width: 180px;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid #E5E7EB;
        }}
        .kpi-card .value {{
            font-size: 28px;
            font-weight: 700;
            color: #1F2937;
        }}
        .kpi-card .label {{
            font-size: 13px;
            color: #6B7280;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .chart-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        .chart-card {{
            background: white;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid #E5E7EB;
        }}
        .chart-card.full {{
            grid-column: 1 / -1;
        }}
        @media (max-width: 768px) {{
            .chart-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>COMPREHENSIVE RETAIL SALES PERFORMANCE DASHBOARD</h1>
        <p>Detailed Performance Insights & Hourly Velocity</p>
    </div>

    <div class="chart-grid">
        <div class="chart-card full">
            {chart3_html}
        </div>
        <div class="chart-card">
            {chart1_html}
        </div>
        <div class="chart-card">
            {chart2_html}
        </div>
        <div class="chart-card">
            {chart4_html}
        </div>
    </div>

    <script>
        // Auto-resize plots on window resize
        window.addEventListener('resize', function() {{
            var plots = document.querySelectorAll('.js-plotly-plot');
            plots.forEach(function(p) {{
                Plotly.Plots.resize(p);
            }});
        }});
    </script>
</body>
</html>"""

with open('dashboard_full.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ สร้าง dashboard_full.html เรียบร้อย!")
print("📄 ไฟล์: dashboard_full.html")
print("🔗 เปิดใน browser หรือใช้ Embed ใน Looker Studio ได้เลย")