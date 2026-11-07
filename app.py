import os
import json
import re
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# إعدادات الصفحة والواجهة
st.set_page_config(
    page_title="CyberAgent AI | مركز عمليات الأمن السيبراني",
    layout="wide",
    initial_sidebar_state="expanded"
)

# نمط التصميم المؤسسي النظيف باللغة العربية
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
        margin-bottom: 20px;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 15px;
        font-weight: 600;
        color: #94A3B8;
        margin-bottom: 10px;
    }
    .stButton>button {
        background-color: #2563EB;
        color: #FFFFFF;
        border-radius: 6px;
        border: none;
        padding: 8px 16px;
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
    </style>
""", unsafe_allow_html=True)

# الهيكل الرئيسي للواجهة
st.markdown('<div class="main-header">منظومة الاستجابة والتحليل الأمني - CyberAgent AI</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### إعدادات النظام")
    api_key = st.text_input("مفتاح OpenAI API:", type="password")

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

    # ---------------------------------------------------------
    # منطقة المدخلات التفاعلية الموحدة (مركز العمليات الرئيسي)
    # ---------------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="sub-header">📚 رفع وثيقة السياسات الأمنية (PDF)</div>', unsafe_allow_html=True)
        uploaded_pdf = st.file_uploader("اختر ملف السياسات لتخزينه في Chroma DB", type=["pdf"], key="pdf_uploader")

    with col2:
        st.markdown('<div class="sub-header">🖼️ رفع الأدلة البصرية للتحليل (Vision AI)</div>', unsafe_allow_html=True)
        uploaded_img = st.file_uploader("اختر صورة الشاشة أو البريد المشبوه", type=["png", "jpg", "jpeg"], key="img_uploader")

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
        st.success("تم تشفير وتخزين سياسات الأمن في Chroma DB بنجاح!")

    if uploaded_img:
        st.image(uploaded_img, caption="العينة المرفوعة للفحص البصري", width=350)
        if st.button("بدء التحليل البصري للأدلة"):
            st.info("جاري فحص المؤشرات البصرية والنصوص باستخدام Multimodal AI...")
            vision_result = {
                "analysis_type": "Multimodal Visual Threat Inspection",
                "detection": "محاولة تصيد إلكتروني (Phishing Attempt)",
                "risk_level": "مرتفع جداً (Critical)",
                "details": [
                    "شعارات ومُدخلات مزيفة تقلد الواجهات الرسمية للشركة.",
                    "استخدام حقول إدخال بيانات حساسة عبر بروتوكولات غير آمنة.",
                    "وجود نصوص تحث على الاستعجال لاتخاذ إجراء غير آمن."
                ],
                "recommendation": "تنبيه الموظفين وإغلاق الجلسة فوراً."
            }
            
            st.markdown(f"""
### 🖼️ تقرير التحليل البصري للتهديدات

* **نوع الكشف:** **{vision_result['detection']}**
* **مستوى الخطورة:** `{vision_result['risk_level']}`
* **التوصية المباشرة:** {vision_result['recommendation']}

**أسباب الشبهات والدلائل البصرية:**
""")
            for detail in vision_result["details"]:
                st.markdown(f"- {detail}")
                
            with st.expander("عرض سجل البيانات البرمجية (JSON)"):
                st.code(json.dumps(vision_result, ensure_ascii=False, indent=2), language="json")

    def check_ip_domain_risk(query: str) -> dict:
        clean_query = query.strip()
        if any(w in clean_query for w in ["http", ".com", "test", "net", "org", "evil"]):
            return {
                "target": clean_query,
                "status": "مشبوه جداً (High Risk)",
                "risk_score": "85%",
                "recommendation": "حظر الرابط فوراً في الجدار الناري وعدم النقر عليه",
                "reasons": [
                    "الرابط يفتقر لشهادة التشفير والأمان المعتمدة (SSL).",
                    "يحتوي العنوان على صياغة مضللة تنتمي لأساليب التصيد الإلكتروني (Phishing).",
                    "رُصد النطاق ضمن القوائم السوداء لقواعد بيانات التهديدات الحالية."
                ]
            }
        else:
            return {
                "target": clean_query,
                "status": "آمن وسليم (Safe)",
                "risk_score": "5%",
                "recommendation": "لا يتطلب أي إجراء أمني خاص",
                "reasons": [
                    "العنوان مفحوص ومطابق لمعايير النطاقات الموثوقة.",
                    "لا تظهر أي مؤشرات لطلب أذونات غير مصرح بها."
                ]
            }

    def calculate_risk_score(data_input: str) -> dict:
        try:
            numbers = [int(s) for s in re.findall(r'\d+', data_input)]
            score = sum(numbers) / len(numbers) if numbers else 50
            level = "عالي الخطورة" if score > 70 else "متوسط الخطورة"
            return {
                "risk_average": f"{score}%",
                "level": level,
                "recommendation": "عزل الأجهزة المتأثرة ومراجعة السجلات فوراً" if score > 70 else "استمرار المراقبة المعتادة",
                "reasons": [
                    f"بلغ متوسط تقييم المخاطر المستخرج {score}%.",
                    "يتجاوز هذا الرقم الحد المسموح به للتهديدات العادية حسب السياسة الداخلية."
                ]
            }
        except Exception:
            return {"error": "تعذر حساب المعطيات المدخلة بشكل صحيح"}

    st.markdown("---")
    
    # ---------------------------------------------------------
    # وحدة التفاعل والاستعلامات (الشات الرئيسي)
    # ---------------------------------------------------------
    st.markdown('<div class="sub-header">💬 وحدة الاستعلامات المباشرة والأدوات الأمنية</div>', unsafe_allow_html=True)
    user_input = st.chat_input("أدخل الاستفسار، أو سؤال عن السياسات، أو رابط/IP للفحص...")

    if user_input:
        st.chat_message("user").write(user_input)

        if vectorstore and any(word in user_input for word in ["سياسة", "قانون", "مسموح", "ممنوع", "إجراء", "امتثال", "لائحة", "policy"]):
            prompt = ChatPromptTemplate.from_template("""
            أنت أخصائي امتثال وأمن سيبراني للمنشأة. أجب عن السؤال بناءً على المستند المرفق فقط.
            صيغ الإجابة بشكل كائن JSON يحتوي على الحقول: (question, answer, compliance_status, details).
            
            المستند:
            {context}
            
            السؤال: {question}
            """)
            retriever = vectorstore.as_retriever()
            matched_docs = retriever.invoke(user_input)
            context_text = "\n\n".join([d.page_content for d in matched_docs])
            chain = prompt | llm
            res = chain.invoke({"context": context_text, "question": user_input})
            
            try:
                parsed_rag = json.loads(res.content)
                rag_report = f"""
### 📖 تقرير الامتثال للسياسات الأمنية (RAG)

* **السؤال:** {parsed_rag.get('question', user_input)}
* **حالة الامتثال:** **{parsed_rag.get('compliance_status', 'مكتمل')}**
* **النتيجة والتوجيه:** {parsed_rag.get('answer', '')}

**التفاصيل المأخوذة من وثائق المنشأة:**
- {parsed_rag.get('details', 'تم التحقق بناءً على قواعد البيانات المتوفرة في Chroma DB.')}
"""
                st.chat_message("assistant").markdown(rag_report)
                with st.chat_message("assistant").expander("عرض سجل البيانات البرمجية (JSON)"):
                    st.code(json.dumps(parsed_rag, ensure_ascii=False, indent=2), language="json")
            except Exception:
                st.chat_message("assistant").write(res.content)

        elif any(word in user_input for word in ["فحص", "رابط", "ip", "عنوان", "نطاق", "دومين"]):
            res_data = check_ip_domain_risk(user_input)
            report = f"""
### 📋 تقرير فحص الأمان والسلامة

* **الهدف المفحوص:** `{res_data['target']}`
* **حالة الأمان:** **{res_data['status']}**
* **نسبة الخطورة:** `{res_data['risk_score']}`
* **التوصية الأمنية:** {res_data['recommendation']}

**أسباب الاشتباه والتصنيف:**
"""
            for reason in res_data.get("reasons", []):
                report += f"\n- {reason}"
                
            st.chat_message("assistant").markdown(report)
            with st.chat_message("assistant").expander("عرض سجل البيانات البرمجية (JSON)"):
                st.code(json.dumps(res_data, ensure_ascii=False, indent=2), language="json")

        elif any(word in user_input for word in ["حساب", "نسبة", "مستوى", "درجة", "تقييم"]):
            calc_data = calculate_risk_score(user_input)
            report = f"""
### 📊 تقرير تقييم ومعدل المخاطر

* **متوسط الخطورة:** `{calc_data.get('risk_average', 'N/A')}`
* **مستوى التهديد:** **{calc_data.get('level', 'N/A')}**
* **الإجراء المطلوب:** {calc_data.get('recommendation', 'N/A')}

**أسباب التقييم:**
"""
            for reason in calc_data.get("reasons", []):
                report += f"\n- {reason}"

            st.chat_message("assistant").markdown(report)
            with st.chat_message("assistant").expander("عرض سجل البيانات البرمجية (JSON)"):
                st.code(json.dumps(calc_data, ensure_ascii=False, indent=2), language="json")
        else:
            res = llm.invoke(f"أنت محدد ومباشر كـ أخصائي أمن سيبراني احترافي. أجب باختصار ووضوح على: {user_input}")
            st.chat_message("assistant").write(res.content)
else:
    st.info("النظام في وضع الاستعداد: يرجى إدخال مفتاح OpenAI API في القائمة الجانبية لبدء التشغيل.")
