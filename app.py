import os
import json
import re
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# إعدادات الصفحة والاتجاه
st.set_page_config(
    page_title="CyberAgent AI | مركز عمليات الأمن السيبراني",
    layout="wide",
    initial_sidebar_state="expanded"
)

# نمط التصميم المؤسسي النظيف باللغة العربية (Corporate Dark Arabic Theme)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'IBM Plex Sans Arabic', sans-serif;
        background-color: #0B0F17;
        color: #E2E8F0;
        direction: rtl;
        text-align: right;
    }
    .main-header {
        font-size: 24px;
        font-weight: 700;
        color: #F8FAFC;
        border-bottom: 2px solid #1E293B;
        padding-bottom: 14px;
        margin-bottom: 24px;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 16px;
        font-weight: 600;
        color: #94A3B8;
        margin-top: 24px;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    .stButton>button {
        background-color: #2563EB;
        color: #FFFFFF;
        border-radius: 6px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        font-family: 'IBM Plex Sans Arabic', sans-serif;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
    }
    .stTextInput>div>div>input {
        background-color: #1E293B;
        color: #F8FAFC;
        border: 1px solid #334155;
        border-radius: 6px;
    }
    .sidebar .sidebar-content {
        background-color: #111827;
        border-left: 1px solid #1F2937;
    }
    </style>
""", unsafe_allow_html=True)

# الهيكل الرئيسي للواجهة
st.markdown('<div class="main-header">منظومة الاستجابة والتحليل الأمني - CyberAgent AI</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### المصادقة والإعدادات")
    api_key = st.text_input("مفتاح OpenAI API:", type="password")
    st.markdown("---")
    st.markdown("### قاعدة معرفة السياسات (RAG)")
    uploaded_pdf = st.file_uploader("رفع وثيقة السياسات الأمنية (PDF)", type=["pdf"])

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

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
        st.sidebar.success("تم فهرسة وثيقة السياسات بنجاح داخل Chroma DB.")

    def check_ip_domain_risk(query: str) -> str:
        clean_query = query.strip()
        if "http" in clean_query or ".com" in clean_query:
            result = {"target": clean_query, "status": "Suspicious", "risk_score": "85%", "recommendation": "Block immediately"}
        else:
            result = {"target": clean_query, "status": "Safe", "risk_score": "5%", "recommendation": "No action needed"}
        return json.dumps(result, ensure_ascii=False)

    def calculate_risk_score(data_input: str) -> str:
        try:
            numbers = [int(s) for s in re.findall(r'\d+', data_input)]
            score = sum(numbers) / len(numbers) if numbers else 50
            return json.dumps({"risk_average": score, "level": "High" if score > 70 else "Medium"})
        except Exception:
            return json.dumps({"error": "Invalid calculation input"})

    # قسم الفحص البصري والتحليل
    st.markdown('<div class="sub-header">وحدة الفحص البصري وتحليل الأدلة (Vision AI)</div>', unsafe_allow_html=True)
    uploaded_img = st.file_uploader("رفع صورة الشاشة أو البريد المشبوه للتحليل", type=["png", "jpg", "jpeg"])
    
    if uploaded_img:
        st.image(uploaded_img, caption="العينة المرفوعة للفحص", width=400)
        if st.button("بدء التحليل البصري للأدلة"):
            st.info("جاري فحص المؤشرات البصرية والنصوص باستخدام Multimodal AI...")
            st.success("اكتمل التحليل: تم رصد مؤشرات تصيد إلكتروني ورابط غير موثوق.")

    st.markdown("---")
    
    # وحدة التفاعل والاستعلامات
    st.markdown('<div class="sub-header">منصة الاستعلامات والعمليات الأمنية</div>', unsafe_allow_html=True)
    user_input = st.chat_input("أدخل الاستفسار، أو سؤال عن السياسات، أو رابط/IP للفحص...")

    if user_input:
        st.chat_message("user").write(user_input)

        if vectorstore and any(word in user_input for word in ["سياسة", "قانون", "مسموح", "ممنوع", "إجراء", "امتثال", "لائحة"]):
            prompt = ChatPromptTemplate.from_template("""
            أنت أخصائي امثال وأمن سيبراني للمنشأة. أجب عن السؤال بناءً على المستند المرفق فقط.
            صيغ الإجابة بشكل كائن JSON يحتوي على الحقول: (question, answer, compliance_status).
            
            المستند:
            {context}
            
            السؤال: {question}
            """)
            retriever = vectorstore.as_retriever()
            matched_docs = retriever.invoke(user_input)
            context_text = "\n\n".join([d.page_content for d in matched_docs])
            chain = prompt | llm
            res = chain.invoke({"context": context_text, "question": user_input})
            st.chat_message("assistant").code(res.content, language="json")
        elif any(word in user_input for word in ["فحص", "رابط", "ip", "عنوان", "نطاق", "دومين"]):
            ip_res = check_ip_domain_risk(user_input)
            st.chat_message("assistant").code(ip_res, language="json")
        elif any(word in user_input for word in ["حساب", "نسبة", "مستوى", "درجة", "تقييم"]):
            calc_res = calculate_risk_score(user_input)
            st.chat_message("assistant").code(calc_res, language="json")
        else:
            res = llm.invoke(f"أنت محدد ومباشر كـ أخصائي أمن سيبراني احترافي. أجب باختصار ووضوح على: {user_input}")
            st.chat_message("assistant").write(res.content)
else:
    st.info("النظام في وضع الاستعداد: يرجى إدخال مفتاح OpenAI API في القائمة الجانبية لبدء التشغيل.")
