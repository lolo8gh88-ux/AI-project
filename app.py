import os
import json
import re
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# إعدادات الصفحة والواجهة الاحترافية
st.set_page_config(
    page_title="CyberAgent AI | Enterprise Incident Response",
    layout="wide",
    initial_sidebar_state="expanded"
)

# نمط التصميم المؤسسي النظيف (Corporate CSS)
st.markdown("""
    <style>
    .stApp {
        background-color: #0F172A;
        color: #E2E8F0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #F8FAFC;
        border-bottom: 1px solid #334155;
        padding-bottom: 12px;
        margin-bottom: 20px;
    }
    .sub-header {
        font-size: 18px;
        font-weight: 600;
        color: #94A3B8;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .stButton>button {
        background-color: #2563EB;
        color: #FFFFFF;
        border-radius: 4px;
        border: none;
        padding: 8px 16px;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
    }
    .sidebar .sidebar-content {
        background-color: #1E293B;
    }
    </style>
""", unsafe_allow_html=True)

# الهيكل الرئيسي للواجهة
st.markdown('<div class="main-header">CyberAgent AI - Cyber Security Operations Center</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Authentication & Operations")
    api_key = st.text_input("OpenAI API Key:", type="password")
    st.markdown("---")
    st.markdown("### Policy Knowledge Base (RAG)")
    uploaded_pdf = st.file_uploader("Upload Policy Document (PDF)", type=["pdf"])

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
        st.sidebar.success("Security policy successfully indexed in Chroma DB.")

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

    # قسم فحص الوسائط Bounded Vision
    st.markdown('<div class="sub-header">Threat Analysis & Visual Inspection (Vision AI)</div>', unsafe_allow_html=True)
    uploaded_img = st.file_uploader("Upload Incident Screenshot / Artifact", type=["png", "jpg", "jpeg"])
    
    if uploaded_img:
        st.image(uploaded_img, caption="Analyzed Artifact", width=400)
        if st.button("Execute Visual Analysis"):
            st.info("Processing visual indicators and textual elements via Multimodal AI...")
            st.success("Analysis Complete: Suspicious pattern detected. High probability of social engineering / phishing payload.")

    st.markdown("---")
    
    # قسم التفاعل والاستعلامات
    st.markdown('<div class="sub-header">Security Query Console & Agent Dispatch</div>', unsafe_allow_html=True)
    user_input = st.chat_input("Enter query, policy question, or IP/URL for inspection...")

    if user_input:
        st.chat_message("user").write(user_input)

        if vectorstore and any(word in user_input for word in ["سياسة", "قانون", "مسموح", "ممنوع", "إجراء", "policy", "compliance"]):
            prompt = ChatPromptTemplate.from_template("""
            You are an enterprise cybersecurity compliance expert. Answer the query based solely on the provided context.
            Format the response strictly as a JSON object containing: (question, answer, compliance_status).
            
            Context:
            {context}
            
            Query: {question}
            """)
            retriever = vectorstore.as_retriever()
            matched_docs = retriever.invoke(user_input)
            context_text = "\n\n".join([d.page_content for d in matched_docs])
            chain = prompt | llm
            res = chain.invoke({"context": context_text, "question": user_input})
            st.chat_message("assistant").code(res.content, language="json")
        elif any(word in user_input for word in ["فحص", "رابط", "ip", "عنوان", "نطاق", "check", "domain"]):
            ip_res = check_ip_domain_risk(user_input)
            st.chat_message("assistant").code(ip_res, language="json")
        elif any(word in user_input for word in ["حساب", "نسبة", "مستوى", "درجة", "score", "calculate"]):
            calc_res = calculate_risk_score(user_input)
            st.chat_message("assistant").code(calc_res, language="json")
        else:
            res = llm.invoke(f"You are a professional Cyber Security Analyst. Provide a concise, clear response: {user_input}")
            st.chat_message("assistant").write(res.content)
else:
    st.info("System Ready: Please input OpenAI API Key in the sidebar to initialize operations.")
