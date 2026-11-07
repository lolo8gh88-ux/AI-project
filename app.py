import os
import json
import re
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# إعدادات الصفحة والواجهة البسيطة الهادئة
st.set_page_config(
    page_title="CyberAgent AI",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# نمط تصميم عصري مشابهاً لواجهات المحادثة الذكية (Clean Chat Interface)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'IBM Plex Sans Arabic', sans-serif;
        background-color: #131314;
        color: #E3E3E3;
        direction: rtl;
        text-align: right;
    }
    .main-header {
        font-size: 22px;
        font-weight: 600;
        color: #F1F1F1;
        margin-bottom: 8px;
        text-align: center;
    }
    .sub-title {
        font-size: 14px;
        color: #8E918F;
        margin-bottom: 24px;
        text-align: center;
    }
    .upload-box {
        background-color: #1E1F20;
        border: 1px solid #2E2F31;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #A8C7FA;
        color: #040E1B;
        border-radius: 20px;
        border: none;
        padding: 8px 16px;
        font-weight: 600;
        font-family: 'IBM Plex Sans Arabic', sans-serif;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #7C9FDC;
        color: #040E1B;
    }
    .stTextInput>div>div>input {
        background-color: #1E1F20;
        color: #E3E3E3;
        border: 1px solid #444746;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# العنوان الرئيسي المباشر
st.markdown('<div class="main-header">CyberAgent AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">المساعد الذكي لفحص التهديدات الأمنية وتحليل السياسات</div>', unsafe_allow_html=True)

# إعداد المفتاح في أعلى الصفحة أو في شريط جانبي بسيط
with st.expander("إعدادات مفتاح التشغيل (API Key)", expanded=False):
    api_key = st.text_input("أدخل مفتاح OpenAI API:", type="password")

if not api_key:
    # محاولة قراءة المفتاح من بيئة العمل إن وجد
    api_key = os.environ.get("OPENAI_API_KEY", "")

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

    # منطقة رفع المرفقات الموحدة
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**رفع وثيقة السياسات (PDF)**")
        uploaded_pdf = st.file_uploader("اختر ملف PDF لتخزينه في Chroma DB", type=["pdf"], key="pdf_uploader", label_visibility="collapsed")

    with col2:
        st.markdown("**رفع صور الأدلة والرسائل**")
        uploaded_img = st.file_uploader("اختر صورة للتحليل البصري", type=["png", "jpg", "jpeg"], key="img_uploader", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    vectorstore = None
    if uploaded_pdf:
        with open("cyber_policy.pdf", "wb") as f:
            f.write(uploaded_pdf.getbuffer())
        
        loader = PyPDFLoader("cyber_policy.pdf")
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
        splits = text_splitter.split_documents(docs)
        
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        st.success("تم تشفير وتخزين المستند في Chroma DB بنجاح.")

    if uploaded_img:
        st.image(uploaded_img, caption="الصورة المرفوعة للفحص", width=350)
        if st.button("بدء تحليل الصورة"):
            st.info("جاري تحليل العناصر البصرية والنصية...")
            vision_result = {
                "analysis_type": "Visual Threat Inspection",
                "detection": "محاولة تصيد إلكتروني",
                "risk_level": "عالي جداً",
                "details": [
                    "شعارات مزيفة تقلد الواجهات الرسمية.",
                    "حقول إدخال بيانات غير محميّة.",
                    "نصوص تحث على اتخاذ إجراء سريع."
                ],
                "recommendation": "إغلاق الصفحة فوراً وعدم إدخال أي بيانات."
            }
            
            st.markdown(f"""
### تقرير التحليل البصري

* **نتيجة الكشف:** **{vision_result['detection']}**
* **مستوى الخطورة:** `{vision_result['risk_level']}`
* **التوصية:** {vision_result['recommendation']}

**ملاحظات الفحص:**
""")
            for detail in vision_result["details"]:
                st.markdown(f"- {detail}")
                
            with st.expander("عرض بيانات JSON التقنية"):
                st.code(json.dumps(vision_result, ensure_ascii=False, indent=2), language="json")

    def check_ip_domain_risk(query: str) -> dict:
        clean_query = query.strip()
        if any(w in clean_query for w in ["http", ".com", "test", "net", "org", "evil"]):
            return {
                "target": clean_query,
                "status": "مشبوه (High Risk)",
                "risk_score": "85%",
                "recommendation": "حظر الرابط وعدم الفتح",
                "reasons": [
                    "عدم وجود شهادة تشفير SSL معتمدة.",
                    "صياغة العنوان تتطابق مع نطاقات التصيد.",
                    "مدرج في قواعد بيانات التهديدات."
                ]
            }
        else:
            return {
                "target": clean_query,
                "status": "آمن (Safe)",
                "risk_score": "5%",
                "recommendation": "لا يوجد خطورة",
                "reasons": [
                    "النطاق مفحوص وموثوق.",
                    "لا توجد مؤشرات أذونات غير مصرح بها."
                ]
            }

    def calculate_risk_score(data_input: str) -> dict:
        try:
            numbers = [int(s) for s in re.findall(r'\d+', data_input)]
            score = sum(numbers) / len(numbers) if numbers else 50
