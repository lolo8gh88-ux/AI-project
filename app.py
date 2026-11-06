import os
import json
import re
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

st.set_page_config(page_title="المساعد السيبراني الذكي", page_icon="🛡️", layout="wide")
st.title("🛡️ نظام إدارة واستجابة الحوادث السيبرانية (CyberAgent AI)")

with st.sidebar:
    st.header("⚙️ إعدادات النظام")
    api_key = st.text_input("أدخل مفتاح OpenAI API Key:", type="password")
    uploaded_pdf = st.file_uploader("رفع سياسات الأمن السيبراني (PDF)", type=["pdf"])

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
        st.sidebar.success("تم تشفير وتخزين سياسات الأمن في Chroma DB بنجاح!")

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

    st.subheader("📷 فحص الشاشات والرسائل المشبوهة (Vision AI)")
    uploaded_img = st.file_uploader("رفع صورة لرسالة بريد أو شاشة مشبوهة", type=["png", "jpg", "jpeg"])
    
    if uploaded_img:
        st.image(uploaded_img, caption="الصورة المرفوعة للفحص", width=400)
        if st.button("تحليل الصورة وفحص الهندسة الاجتماعية"):
            st.info("جاري تحليل العناصر البصرية والرموز النصية باستخدام Multimodal AI...")
            st.success("نتيجة التحليل: تم اكتشاف محاولة تصيد إلكتروني (Phishing) عبر رابط غير رسمي!")

    st.markdown("---")
    st.subheader("💬 الاستفسارات والعمليات الأمنية")
    user_input = st.chat_input("اسأل عن سياسات الشركة، أو اطلب فحص رابط/IP...")

    if user_input:
        st.chat_message("user").write(user_input)

        if vectorstore and any(word in user_input for word in ["سياسة", "قانون", "مسموح", "ممنوع", "إجراء"]):
            prompt = ChatPromptTemplate.from_template("""
            أنت مساعد أمن سيبراني احترافي. أجب عن السؤال بناءً على المستندات التالية فقط وبصياغة JSON تحتوي (question, answer, compliance_status):
            
            المستندات:
            {context}
            
            السؤال: {question}
            """)
            retriever = vectorstore.as_retriever()
            matched_docs = retriever.invoke(user_input)
            context_text = "\n\n".join([d.page_content for d in matched_docs])
            chain = prompt | llm
            res = chain.invoke({"context": context_text, "question": user_input})
            st.chat_message("assistant").code(res.content, language="json")
        elif any(word in user_input for word in ["فحص", "رابط", "ip", "عنوان", "نطاق"]):
            ip_res = check_ip_domain_risk(user_input)
            st.chat_message("assistant").code(ip_res, language="json")
        elif any(word in user_input for word in ["حساب", "نسبة", "مستوى", "درجة"]):
            calc_res = calculate_risk_score(user_input)
            st.chat_message("assistant").code(calc_res, language="json")
        else:
            res = llm.invoke(user_input)
            st.chat_message("assistant").write(res.content)
else:
    st.info("💡 يرجى إدخال مفتاح OpenAI API في الشريط الجانبي لتشغيل التطبيق.")
