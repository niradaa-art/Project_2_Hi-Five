import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="NYC 311 Resolution Time Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. Mock Data Generator (สำหรับใช้รันระบบทดสอบ Dashboard)
# ---------------------------------------------------------
@st.cache_data
def load_data():
    np.random.seed(42)
    n_samples = 5000
    
    agencies = ['NYPD', 'HPD', 'DOT', 'DSNY', 'DEP', 'DOB']
    boroughs = ['MANHATTAN', 'BROOKLYN', 'QUEENS', 'BRONX', 'STATEN ISLAND']
    complaint_types = [
        'Noise - Residential', 'Illegal Parking', 'UNSANITARY CONDITION', 
        'PLUMBING', 'HEAT/HOT WATER', 'Blocked Driveway', 'Street Condition'
    ]
    
    dates = pd.date_range(start='2025-01-01', end='2025-12-31', freq='h')
    created_dates = np.random.choice(dates, size=n_samples)
    
    # จำลอง resolution time (ชั่วโมง) แบบ Skewed Distribution
    res_times = np.random.exponential(scale=24, size=n_samples) + np.random.uniform(0.5, 5, size=n_samples)
    
    df = pd.DataFrame({
        'created_date': created_dates,
        'agency': np.random.choice(agencies, size=n_samples, p=[0.35, 0.25, 0.15, 0.1, 0.1, 0.05]),
        'borough': np.random.choice(boroughs, size=n_samples),
        'complaint_type': np.random.choice(complaint_types, size=n_samples),
        'resolution_time': res_times
    })
    
    # Feature Extraction
    df['hour'] = df['created_date'].dt.hour
    df['day_of_week'] = df['created_date'].dt.day_name()
    df['month'] = df['created_date'].dt.month_name()
    
    return df

df = load_data()

# ---------------------------------------------------------
# 3. Sidebar Filters
# ---------------------------------------------------------
st.sidebar.header("🔍 ตัวกรองข้อมูล (Data Filters)")

selected_borough = st.sidebar.multiselect(
    "เลือกเขตพื้นที่ (Borough):",
    options=df['borough'].unique(),
    default=df['borough'].unique()
)

selected_agency = st.sidebar.multiselect(
    "เลือกหน่วยงาน (Agency):",
    options=df['agency'].unique(),
    default=df['agency'].unique()
)

# Filter Data
filtered_df = df[(df['borough'].isin(selected_borough)) & (df['agency'].isin(selected_agency))]

# ---------------------------------------------------------
# 4. Header & KPI Metrics
# ---------------------------------------------------------
st.title("📊 NYC 311 Service Requests Analytics Dashboard")
st.markdown("ระบบวิเคราะห์และคาดการณ์ระยะเวลาการแก้ไขปัญหาคำร้องเรียน ประจำปี 2025 (กลุ่ม **Hi-Five**)")

st.divider()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Complaints", value=f"{len(filtered_df):,}")
with col2:
    st.metric(label="Mean Resolution Time", value=f"{filtered_df['resolution_time'].mean():.2f} hrs")
with col3:
    st.metric(label="Median Resolution Time", value=f"{filtered_df['resolution_time'].median():.2f} hrs")
with col4:
    closed_24h = (filtered_df['resolution_time'] <= 24).mean() * 100
    st.metric(label="Closed within 24 Hours", value=f"{closed_24h:.1f}%")

st.divider()

# ---------------------------------------------------------
# 5. Visualizations Section
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📈 ภาพรวมประสิทธิภาพ (Performance)", "⏱️ พฤติกรรมตามเวลา (Time Trends)", "🤖 ระบบจำลองทำนายผล (Prediction Simulator)"])

with tab1:
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("ระยะเวลาดำเนินการมัธยฐาน แยกตามประเภทคำร้องเรียน (Top Complaints)")
        complaint_stats = filtered_df.groupby('complaint_type')['resolution_time'].median().reset_index()
        complaint_stats = complaint_stats.sort_values(by='resolution_time', ascending=True)
        fig_complaints = px.bar(
            complaint_stats, 
            x='resolution_time', 
            y='complaint_type', 
            orientation='h',
            labels={'resolution_time': 'Median Hours', 'complaint_type': 'Complaint Type'},
            color='resolution_time',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_complaints, use_container_width=True)

    with col_right:
        st.subheader("จำนวนคำร้องเรียนแยกตามหน่วยงาน (Agency Distribution)")
        agency_counts = filtered_df['agency'].value_counts().reset_index()
        agency_counts.columns = ['agency', 'count']
        fig_agency = px.pie(
            agency_counts, 
            names='agency', 
            values='count',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_agency, use_container_width=True)

with tab2:
    col_time1, col_time2 = st.columns(2)
    
    with col_time1:
        st.subheader("ความหนาแน่นของการแจ้งเรื่องตามชั่วโมงในแต่ละวัน")
        heatmap_data = filtered_df.groupby(['day_of_week', 'hour']).size().unstack().fillna(0)
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_data.reindex(days_order)
        
        fig_heatmap = px.imshow(
            heatmap_data,
            labels=dict(x="Hour of Day", y="Day of Week", color="Requests Count"),
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
    with col_time2:
        st.subheader("การกระจายตัวของระยะเวลาปิดเรื่อง (Resolution Time Distribution)")
        fig_dist = px.box(
            filtered_df, 
            x='borough', 
            y='resolution_time',
            color='borough',
            labels={'resolution_time': 'Hours', 'borough': 'Borough'}
        )
        fig_dist.update_layout(yaxis=dict(type='log')) # ใช้ Log Scale เนื่องจากข้อมูลมีความเบ้สูง
        st.plotly_chart(fig_dist, use_container_width=True)

with tab3:
    st.subheader("🔮 เครื่องมือจำลองทำนายระยะเวลาปิดเรื่อง (Machine Learning Simulator)")
    st.write("เลือกคุณลักษณะของเรื่องร้องเรียนเพื่อประเมินระยะเวลาแก้ไขปัญหา")
    
    sim_col1, sim_col2 = st.columns(2)
    
    with sim_col1:
        input_agency = st.selectbox("เลือกหน่วยงานรับเรื่อง (Agency):", df['agency'].unique())
        input_complaint = st.selectbox("เลือกประเภทเรื่องร้องเรียน (Complaint Type):", df['complaint_type'].unique())
        input_borough = st.selectbox("เลือกเขตพื้นที่ (Borough):", df['borough'].unique())
        
    with sim_col2:
        input_hour = st.slider("ช่วงเวลาที่แจ้ง (Hour of Day):", 0, 23, 12)
        input_day = st.selectbox("วันที่แจ้ง (Day of Week):", ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

    if st.button("🚀 คำนวณระยะเวลาคาดการณ์ (Predict Resolution Time)"):
        # Dummy Machine Learning Model Logic (จำลองการทำนายผล)
        base_time = 10.0
        if input_agency == 'NYPD':
            base_time -= 5.0
        elif input_agency == 'HPD':
            base_time += 45.0
            
        if 'Noise' in input_complaint:
            base_time -= 2.0
        elif 'UNSANITARY' in input_complaint:
            base_time += 30.0
            
        pred_time = max(0.5, base_time + np.random.normal(0, 2))
        
        st.success(f"📌 **คาดการณ์ว่าจะใช้เวลาแก้ไขประมาณ:** `{pred_time:.2f}` **ชั่วโมง**")
        st.info(f"💡 คำร้องเรียนประเภท **{input_complaint}** ในเขต **{input_borough}** ที่รับเรื่องโดย **{input_agency}**")