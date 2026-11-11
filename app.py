import os
import json
import re
import streamlit as st
from langchain_openai import ChatOpenAI

st.set_page_config(
    page_title="CyberAgent AI - Digital Shield",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تطبيق الألوان والتصميم المستوحى من الواجهة النموذجية
css_code = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'IBM Plex Sans Arabic', sans-serif;
        background-color: #F4F8F7;
        color: #1A252C;
        direction: rtl;
        text-align: right;
    }
    
    /* الشريط الجانبي الداكن */
    [data-testid="stSidebar"] {
        background-color: #0E1B2B !important;
        color: #E2E8F0;
    }
    [data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }
    
    .sidebar-brand {
        font-size: 20px;
        font-weight: 700;
        color: #6366F1 !important;
        margin-bottom: 2px;
    }
    .sidebar-sub {
        font-size: 12px;
        color: #94A3B8 !important;
        margin-bottom: 20px;
    }
    
    /* العناوين والبطاقات */
    .dashboard-title {
        font-size: 26px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 4px;
    }
    .dashboard-subtitle {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 24px;
    }
    
    .card-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }
    .card-header {
        font-size: 16px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 12px;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 8px;
    }
    
    /* التنبيهات والبطاقات التفاعلية */
    .report-card {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        padding: 18px;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .report-title {
        font-size: 16px;
        font-weight: 700;
        color: #0F172A;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 8px;
        margin-bottom: 12px;
    }
    .badge-danger {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
    }
    .badge-success {
        background-color: #DCFCE7;
        color: #166534;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
    }
    .reasons-list {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 12px 18px;
        margin-top: 10px;
        border: 1px solid #E2E8F0;
    }
    .reasons-list li {
        margin-bottom: 6px;
        color: #334155;
    }
    
    /* الأزرار والحقول */
    .stButton>button {
        background-color: #0E1B2B;
        color: #FFFFFF !important;
        border-radius: 10px;
        border: none;
        padding: 8px 16px;
        font-weight: 600;
        font-family: 'IBM Plex Sans Arabic', sans-serif;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1E293B;
        color: #FFFFFF !important;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div {
        background-color: #FFFFFF;
        color: #0F172A;
        border: 1px solid #CBD5E1;
        border-radius: 8px;
    }
    </style>
"""
st.markdown(css_code, unsafe_allow_html=True)

# الشريط الجانبي الداكن المستوحى من الصورة
with st.sidebar:
    st.markdown('<div class="sidebar-brand">CyberAgent AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Digital Shield Platform</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("**مساحة العمل**")
    st.markdown("- نظرة عامة")
    st.markdown("- اختيار خدمة")
    st.markdown("- سجل الحوادث")
    st.divider()
    st.markdown("**إعدادات النظام**")
    api_key = st.text_input("مفتاح التشغيل OpenAI API:", type="password")

if not api_key:
    api_key = os.environ.get("OPENAI_API_KEY", "")

st.markdown('<div class="dashboard-title">ما الذي تريد مراجعته؟</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">اختر مساراً أمنياً للمتابعة، وسيقوم المساعد الذكي بتحليل وتوليد التقارير المباشرة.</div>', unsafe_allow_html=True)

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
    
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
    except Exception:
        st.error("يرجى التأكد من إدخال مفتاح API صحيح.")

    # تقسيم الخدمات إلى بطاقات تفاعلية منظمة
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card-box">
            <div class="card-header">01 / خطة الاستجابة السريعة للحوادث</div>
            <p style="font-size: 13px; color: #64748B;">توليد بروتوكولات احتواء فورية عند وقوع هجمات أمنية.</p>
        """, unsafe_allow_html=True)
        incident_type = st.selectbox(
            "نوع الحادث الأمني:",
            [
                "اختر نوع الهجمة...",
                "برمجية فدية (Ransomware)",
                "اختراق بريد إلكتروني (Email Breach)",
                "تسريب بيانات حساسة (Data Leak)",
                "هجمة حجب الخدمة (DDoS Attack)"
            ],
            label_visibility="collapsed"
        )
        generate_plan_btn = st.button("توليد خطة الاستجابة")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card-box">
            <div class="card-header">02 / تحليل الأدلة والصور (Vision AI)</div>
            <p style="font-size: 13px; color: #64748B;">فحص بصرية محاولات التصيد والواجهات المشبوهة.</p>
        """, unsafe_allow_html=True)
        uploaded_img = st.file_uploader("اختر صورة للتحليل البصري", type=["png", "jpg", "jpeg"], key="img_uploader", label_visibility="collapsed")
        analyze_img_btn = st.button("بدء تحليل الصورة") if uploaded_img else None
        st.markdown('</div>', unsafe_allow_html=True)

    # معالجة خدمة الاستجابة للحوادث
    if incident_type != "اختر نوع الهجمة..." and generate_plan_btn:
        inc_json = {
            "incident_type": incident_type,
            "severity_assessment": "CRITICAL",
            "containment_protocol": "ISOLATE_NETWORK_AND_REVOKE_CREDENTIALS",
            "recommended_actions": [
                "Disconnect affected hosts from local LAN immediately",
                "Reset active directory tokens and primary user secrets",
                "Engage Incident Response Team for digital forensics"
            ]
        }
        
        st.markdown(f"""
        <div class="report-card">
            <div class="report-title">خطة الاستجابة الفورية: {incident_type}</div>
            <div style="margin-bottom: 8px;"><b>مستوى الخطورة:</b> <span class="badge-danger">حرج جداً (Critical)</span></div>
            <div style="margin-bottom: 8px;"><b>بروتوكول الاحتواء:</b> عزل الأجهزة المتأثرة وإلغاء الصلاحيات فوراً.</div>
            <div style="margin-top: 12px; font-weight: 600;">خطوات التنفيذ المباشرة:</div>
            <div class="reasons-list">
                <ul>
                    <li>فصل الأنظمة والأجهزة المتأثرة عن الشبكة المحلية والإنترنت لتجنب الانتشار.</li>
                    <li>إعادة تعيين كلمات المرور والرموز النش
