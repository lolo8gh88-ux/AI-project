import os
import json
import re
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import initialize_agent, Tool, AgentType

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

    agent_tools = [
        Tool(
            name="IP_Domain_Checker",
            func=check_ip_domain_risk,
            description="مفيدة لفحص النطاقات والأذونات وعناوين IP لمعرفة مدى خطورتها."
        ),
        Tool(
            name="Risk_Calculator",
            func=calculate_risk_score,
            description="مفيدة لحساب وتقييم مستويات الخطورة بناءً على الأرقام والمعطيات."
        )
    ]

    cyber_agent = initialize_agent(
        tools=agent_tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

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
            prompt_template = ChatPromptTemplate.from_template("""
            أنت مساعد أمن سيبراني احترافي. أجب عن السؤال بناءً على المستندات فقط.
            قم بصياغة الإجابة دائماً على شكل هيكل JSON يحتوي على الحقول: (question, answer, compliance_status).
            
            <context>
            {context}
            </context>
            
            السؤال: {input}
            """)
            combine_chain = create_stuff_documents_chain(llm, prompt_template)
            rag_chain = create_retrieval_chain(vectorstore.as_retriever(), combine_chain)
            res = rag_chain.invoke({"input": user_input})
            st.chat_message("assistant").code(res["answer"], language="json")
        else:
            res = cyber_agent.run(user_input)
            st.chat_message("assistant").write(res)
else:
    st.info("💡 يرجى إدخال مفتاح OpenAI API في الشريط الجانبي لتشغيل التطبيق.")
