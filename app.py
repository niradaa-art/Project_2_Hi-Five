import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. Page Configuration & Dark Neon Styling (อิงตามภาพตัวอย่าง)
# ---------------------------------------------------------
st.set_page_config(
    page_title="NYC 311 Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS สำหรับปรับแต่งหน้าตาแดชบอร์ดเป็นโทน Cyber-Dark/Neon Purple-Blue
st.markdown("""
    <style>
    /* พื้นหลังหลัก */
    .stApp {
        background-color: #0b0c10;
        color: #e0e0e0;
    }
    /* พื้นหลัง Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #12131c;
    }
    /* การ์ดสถิติ Metric Card */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1f1b3a 0%, #161537 100%);
        border: 1px solid #3d3b6b;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }
    div[data-testid="stMetricLabel"] {
        color: #9a9bba !important;
        font-size: 14px;
    }
    div[data-testid="stMetricValue"] {
        color: #00d2ff !important;
        font-weight: bold;
    }
    /* ปุ่มกด */
    .stButton>button {
        background: linear-gradient(90deg, #7b2cbf 0%, #00d2ff 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.6);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Synthetic Data Generator (100,000 Records with Real Logic)
# ---------------------------------------------------------
@st.cache_data
def load_data():
    np.random.seed(42)
    n_samples = 1_000_000
    
    # 15 ประเภทเรื่องร้องเรียนตามที่กำหนด
    complaint_types = [
        'Illegal Parking',
        'Noise - Residential',
        'HEAT/HOT WATER',
        'Noise - Street/Sidewalk',
        'Blocked Driveway',
        'UNSANITARY CONDITION',
        'Water System',
        'Street Condition',
        'PLUMBING',
        'Abandoned Vehicle',
        'Noise - Commercial',
        'Dirty Condition',
        'PAINT/PLASTER',
        'Noise',
        'Traffic Signal Condition'
    ]
    
    #  Mapping หน่วยงานหลักที่รับผิดชอบประเภทเรื่องร้องเรียนจริง
    complaint_to_agency = {
        'Illegal Parking': 'NYPD',
        'Noise - Residential': 'NYPD',
        'HEAT/HOT WATER': 'HPD',
        'Noise - Street/Sidewalk': 'NYPD',
        'Blocked Driveway': 'NYPD',
        'UNSANITARY CONDITION': 'HPD',
        'Water System': 'DEP',
        'Street Condition': 'DOT',
        'PLUMBING': 'HPD',
        'Abandoned Vehicle': 'DSNY',
        'Noise - Commercial': 'NYPD',
        'Dirty Condition': 'DSNY',
        'PAINT/PLASTER': 'HPD',
        'Noise': 'DEP',
        'Traffic Signal Condition': 'DOT'
    }
    
    boroughs = ['MANHATTAN', 'BROOKLYN', 'QUEENS', 'BRONX', 'STATEN ISLAND']
    
    # สุ่มเลือกประเภทเรื่องร้องเรียนตามสัดส่วนความถี่จริง
    complaint_weights = [
        0.15, 0.14, 0.12, 0.09, 0.08, 
        0.07, 0.06, 0.06, 0.05, 0.04, 
        0.04, 0.03, 0.03, 0.02, 0.02
    ]
    
    sampled_complaints = np.random.choice(complaint_types, size=n_samples, p=complaint_weights)
    sampled_agencies = [complaint_to_agency[c] for c in sampled_complaints]
    sampled_boroughs = np.random.choice(boroughs, size=n_samples, p=[0.28, 0.30, 0.22, 0.14, 0.06])
    
    # สร้างวันที่รับแจ้งตลอดปี 2025
    dates = pd.date_range(start='2025-01-01', end='2025-12-31', freq='min')
    created_dates = np.random.choice(dates, size=n_samples)
    
    # จำลองระยะเวลาปิดเรื่อง (ชั่วโมง) ตามประเภทเรื่องร้องเรียน
    res_times = []
    for comp in sampled_complaints:
        if 'Noise' in comp or 'Traffic' in comp:
            t = np.random.exponential(scale=3.5) + 0.5  # จัดการเร็ว (~3-5 ชม.)
        elif comp in ['Illegal Parking', 'Blocked Driveway']:
            t = np.random.exponential(scale=5.0) + 1.0  # จัดการปานกลาง (~5-8 ชม.)
        elif comp in ['HEAT/HOT WATER', 'Water System', 'Street Condition']:
            t = np.random.exponential(scale=35.0) + 4.0 # จัดการปานกลาง-ช้า (~30-40 ชม.)
        else: # HPD / Building Issues (UNSANITARY, PLUMBING, PAINT/PLASTER)
            t = np.random.exponential(scale=120.0) + 12.0 # ใช้เวลานานมาก (หลายวัน)
        res_times.append(t)
        
    df = pd.DataFrame({
        'created_date': created_dates,
        'agency': sampled_agencies,
        'borough': sampled_boroughs,
        'complaint_type': sampled_complaints,
        'resolution_time': res_times
    })
    
    # ดึงฟีเจอร์เวลา
    df['hour'] = df['created_date'].dt.hour
    df['day_of_week'] = df['created_date'].dt.day_name()
    df['month'] = df['created_date'].dt.month_name()
    
    return df

df = load_data()

# โทนสีหลักสำหรับกราฟ Plotly (Cyberpunk / Neon Violet Palette)
NEON_COLORS = ['#00D2FF', '#8A2BE2', '#FF007F', "#A75EE3", "#B245AF", '#F72585', '#7209B7', '#3F37C9']

# ---------------------------------------------------------
# 3. Sidebar Filters
# ---------------------------------------------------------
st.sidebar.title("🎛️ Control Panel")
st.sidebar.markdown("---")

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

selected_complaint = st.sidebar.multiselect(
    "เลือกประเภทคำร้องเรียน (15 ประเภท):",
    options=df['complaint_type'].unique(),
    default=df['complaint_type'].unique()
)

# กรองข้อมูล
filtered_df = df[
    (df['borough'].isin(selected_borough)) & 
    (df['agency'].isin(selected_agency)) & 
    (df['complaint_type'].isin(selected_complaint))
]

# ---------------------------------------------------------
# 4. Header & Top KPI Metrics
# ---------------------------------------------------------
st.title("🌌 NYC 311 Service Requests Analytics Dashboard")
st.markdown("ระบบวิเคราะห์และคาดการณ์ระยะเวลาดำเนินการเรื่องร้องเรียนนครนิวยอร์ก ประจำปี 2025 (กลุ่ม **Hi-Five**)")
st.caption("⚡ รองรับการประมวลผล Big Data สุ่มตัวอย่าง 100,000 รายการ")

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Complaints", value=f"{len(filtered_df):,}")
with col2:
    st.metric(label="Mean Resolution Time", value=f"{filtered_df['resolution_time'].mean():.1f} hrs")
with col3:
    st.metric(label="Median Resolution Time", value=f"{filtered_df['resolution_time'].median():.1f} hrs")
with col4:
    closed_24h = (filtered_df['resolution_time'] <= 24).mean() * 100
    st.metric(label="Closed within 24 Hours", value=f"{closed_24h:.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. Dashboard Visualizations (Dark/Neon Styling)
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 สถิติและประสิทธิภาพ", "⏱️ รูปแบบตามช่วงเวลา", "🤖 ML Prediction Simulator"])

with tab1:
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("📌 ปริมาณคำร้องเรียนแยกตามประเภท (15 ประเภท)")
        complaint_counts = filtered_df['complaint_type'].value_counts().reset_index()
        complaint_counts.columns = ['complaint_type', 'count']
        
        fig_comp = px.bar(
            complaint_counts,
            y='complaint_type',
            x='count',
            orientation='h',
            color='count',
            color_continuous_scale=['#4CC9F0', '#8A2BE2', '#FF007F']
        )
        fig_comp.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#8642A5"),
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    with col_r:
        st.subheader("🏢 สัดส่วนคำร้องเรียนตามหน่วยงาน (Agency Share)")
        agency_counts = filtered_df['agency'].value_counts().reset_index()
        agency_counts.columns = ['agency', 'count']
        
        fig_agency = px.pie(
            agency_counts,
            names='agency',
            values='count',
            hole=0.5,
            color_discrete_sequence=NEON_COLORS
        )
        fig_agency.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#1525DD")
        )
        st.plotly_chart(fig_agency, use_container_width=True)

    st.markdown("---")
    st.subheader("🌆 เวลาปิดเรื่องมัธยฐาน แยกตามเขตพื้นที่ (Borough) และหน่วยงาน")
    borough_agency = filtered_df.groupby(['borough', 'agency'])['resolution_time'].median().reset_index()
    fig_ba = px.bar(
        borough_agency,
        x='borough',
        y='resolution_time',
        color='agency',
        barmode='group',
        color_discrete_sequence=NEON_COLORS,
        labels={'resolution_time': 'Median Resolution Time (Hours)'}
    )
    fig_ba.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E0E0E0')
    )
    st.plotly_chart(fig_ba, use_container_width=True)

with tab2:
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.subheader("🔥 Heatmap ความหนาแน่นของเรื่องร้องเรียน")
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = filtered_df.groupby(['day_of_week', 'hour']).size().unstack().fillna(0).reindex(days_order)
        
        fig_hm = px.imshow(
            heatmap_data,
            labels=dict(x="Hour of Day", y="Day of Week", color="Count"),
            color_continuous_scale=["#3B4D8E", '#7B2CBF', '#00D2FF', '#FF007F']
        )
        fig_hm.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0')
        )
        st.plotly_chart(fig_hm, use_container_width=True)
        
    with col_t2:
        st.subheader("📦 การกระจายตัวของระยะเวลาปิดเรื่อง (Log Scale)")
        fig_box = px.box(
            filtered_df,
            x='agency',
            y='resolution_time',
            color='agency',
            color_discrete_sequence=NEON_COLORS
        )
        fig_box.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E0E0E0'),
            yaxis=dict(type='log', title="Resolution Time (Hours - Log Scale)")
        )
        st.plotly_chart(fig_box, use_container_width=True)

with tab3:
    st.subheader("🔮 ML Simulator: ทำนายระยะเวลาปิดเรื่องร้องเรียน")
    st.write("ป้อนข้อมูลจำลองเพื่อประเมินระยะเวลาแก้ไขปัญหาของภาครัฐ")
    
    sim_c1, sim_c2 = st.columns(2)
    
    with sim_c1:
        in_complaint = st.selectbox("ประเภทเรื่องร้องเรียน:", df['complaint_type'].unique())
        # Auto select agency matching complaint
        agency_map = df[df['complaint_type'] == in_complaint]['agency'].iloc[0]
        st.info(f"หน่วยงานรับผิดชอบอัตโนมัติ: **{agency_map}**")
        in_borough = st.selectbox("เขตพื้นที่ (Borough):", df['borough'].unique())
        
    with sim_c2:
        in_hour = st.slider("ช่วงเวลาที่รับแจ้ง (Hour):", 0, 23, 14)
        in_day = st.selectbox("วันในสัปดาห์:", ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚡ ทำนายเวลาปิดเรื่อง (Predict Resolution Time)"):
        # Machine Learning Logic Simulator
        base_h = filtered_df[filtered_df['complaint_type'] == in_complaint]['resolution_time'].median()
        pred_val = max(0.5, base_h + np.random.normal(0, base_h * 0.1))
        
        st.markdown(f"""
            <div style="background: linear-gradient(90deg, #1f1b3a 0%, #2d1b4e 100%); border: 1px solid #7b2cbf; border-radius: 10px; padding: 20px; text-align: center;">
                <h3 style="color: #00d2ff; margin:0;">ระยะเวลาคาดการณ์โดยประมาณ</h3>
                <h1 style="color: #ff007f; margin:10px 0; font-size: 42px;">{pred_val:.2f} ชั่วโมง</h1>
                <p style="color: #b0b0b0; margin:0;">(ประมาณ {pred_val/24:.1f} วัน)</p>
            </div>
        """, unsafe_allow_html=True)