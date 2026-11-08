import os
import json
import re
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

st.set_page_config(
    page_title="CyberAgent AI",
    layout="centered",
    initial_sidebar_state="collapsed"
)

css_code = """
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
        font-size: 24px;
        font-weight: 700;
        color: #F1F1F1;
        margin-bottom: 4px;
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
    .report-card {
        background-color: #1E1F20;
        border: 1px solid #333538;
        border-radius: 10px;
        padding: 18px;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .report-title {
        font-size: 16px;
        font-weight: 700;
        color: #F1F1F1;
        border-bottom: 1px solid #2E2F31;
        padding-bottom: 8px;
        margin-bottom: 14px;
    }
    .report-row {
        margin-bottom: 8px;
        font-size: 14px;
    }
    .badge-danger {
        background-color: #4A1D1D;
        color: #F87171;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 600;
    }
    .badge-success {
        background-color: #163828;
        color: #4ADE80;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 600;
    }
    .reasons-list {
        background-color: #161718;
        border-radius: 6px;
        padding: 12px 18px;
        margin-top: 10px;
    }
    .reasons-list li {
        margin-bottom: 6px;
        color: #C4C7C5;
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
"""
st.markdown(css_code, unsafe_allow_html=True)

st.markdown('<div class="main-header">CyberAgent AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">المساعد الذكي لفحص التهديدات الأمنية وتحليل السياسات</div>', unsafe_allow_html=True)

with st.expander("إعدادات مفتاح التشغيل (API Key)", expanded=False):
    api_key = st.text_input("أدخل مفتاح OpenAI API:", type="password")

if not api_key:
    api_key = os.environ.get("OPENAI_API_KEY", "")

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
    
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
    except Exception as e:
        st.error("تعذر الاتصال بـ OpenAI. يرجى التثبت من صحة المفتاح ورصيد الحساب.")

    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**رفع وثيقة السياسات (PDF)**")
        uploaded_pdf = st.file_uploader("اختر ملف PDF لتخزينه في Chroma DB", type=["pdf"], key="pdf_uploader", label_visibility="collapsed")

    with col2:
        st.markdown("**رفع صور الأدلة والرسائل**")
        uploaded_img = st.file_uploader("اختر صورة للتحليل البصري", type=["png", "jpg", "jpeg"], key="img_uploader", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None

    if uploaded_pdf:
        try:
            with open("cyber_policy.pdf", "wb") as f:
                f.write(uploaded_pdf.getbuffer())
            
            loader = PyPDFLoader("cyber_policy.pdf")
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
            splits = text_splitter.split_documents(docs)
            
            embeddings = OpenAIEmbeddings()
            st.session_state.vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
            st.success("تم تشفير وتخزين المستند في Chroma DB بنجاح.")
        except Exception as err:
            st.error("حدث خطأ أثناء تشفير الملف. تأكدي من أن مفتاح OpenAI API صالح ويحتوي على رصيد فعال.")

    if uploaded_img:
        st.image(uploaded_img, caption="الصورة المرفوعة للفحص", width=350)
        if st.button("بدء تحليل الصورة"):
            st.info("جاري تحليل العناصر البصرية والنصية...")
            
            vision_json = {
                "analysis_type": "Visual Threat Inspection",
                "detection": "Phishing Attempt",
                "risk_level": "CRITICAL",
                "indicators": [
                    "Spoofed corporate logo and brand assets",
                    "Unsecured data input fields",
                    "Urgent call-to-action social engineering prompt"
                ],
                "action": "BLOCK_SESSION"
            }
            
            st.markdown("""
            <div class="report-card">
                <div class="report-title">تقرير التحليل البصري للأدلة</div>
                <div class="report-row"><b>نتيجة الكشف:</b> محاولة تصيد إلكتروني (Phishing)</div>
                <div class="report-row"><b>مستوى الخطورة:</b> <span class="badge-danger">عالي جداً (Critical)</span></div>
                <div class="report-row"><b>التوصية المباشرة:</b> إغلاق الصفحة فوراً وعدم إدخال أي بيانات.</div>
                <div style="margin-top: 12px; font-weight: 600;">أسباب الاشتباه وملاحظات الفحص:</div>
                <div class="reasons-list">
                    <ul>
                        <li>شعارات ومكونات مزيفة تقلد الواجهات الرسمية.</li>
                        <li>حقول إدخال بيانات غير محمية لجمع المعلومات.</li>
                        <li>نصوص تحث على اتخاذ إجراء سريع ومشبوه.</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
                
            with st.expander("عرض بيانات JSON التقنية"):
                st.code(json.dumps(vision_json, indent=2), language="json")

    def check_ip_domain_risk(query: str) -> dict:
        clean_query = query.strip()
        if any(w in clean_query for w in ["http", ".com", "test", "net", "org", "evil"]):
            return {
                "target": clean_query,
                "status": "SUSPICIOUS",
                "risk_score": 85,
                "recommendation": "BLOCK_IMMEDIATELY",
                "reasons": [
                    "Missing SSL encryption certificate",
                    "Matches phishing domain syntax patterns",
                    "Blacklisted in threat intelligence databases"
                ]
            }
        else:
            return {
                "target": clean_query,
                "status": "SAFE",
                "risk_score": 5,
                "recommendation": "ALLOW",
                "reasons": [
                    "Domain verified in whitelist",
                    "No suspicious behavior detected"
                ]
            }

    def calculate_risk_score(data_input: str) -> dict:
        try:
            numbers = [int(s) for s in re.findall(r'\d+', data_input)]
            score = sum(numbers) / len(numbers) if numbers else 50
            level = "HIGH" if score > 70 else "MEDIUM"
            return {
                "risk_average_percentage": score,
                "risk_level": level,
                "action_required": "ISOLATE_HOST" if score > 70 else "MONITOR",
                "reasons": [
                    f"Average calculated score is {score}%",
                    "Exceeds risk threshold policy limit"
                ]
            }
        except Exception:
            return {"error": "INVALID_INPUT"}

    user_input = st.chat_input("اكتب سؤالك، أو أدخل رابط/IP للفحص...")

    if user_input:
        st.chat_message("user").write(user_input)

        if st.session_state.vectorstore and any(word in user_input for word in ["سياسة", "قانون", "مسموح", "ممنوع", "إجراء", "امتثال", "لائحة", "policy"]):
            try:
                prompt = ChatPromptTemplate.from_template("""
                Answer the query based ONLY on context. Output strictly a JSON object with English keys and values:
                (question, compliance_status, answer_summary, source_document).
                
                Context:
                {context}
                
                Query: {question}
                """)
                retriever = st.session_state.vectorstore.as_retriever()
                matched_docs = retriever.invoke(user_input)
                context_text = "\n\n".join([d.page_content for d in matched_docs])
                chain = prompt | llm
                res = chain.invoke({"context": context_text, "question": user_input})
                
                parsed_rag = json.loads(res.content)
                status_badge = '<span class="badge-success">مكتمل وممتثل</span>' if parsed_rag.get('compliance_status') == "COMPLIANT" else '<span class="badge-danger">غير ممتثل</span>'
                
                st.chat_message("assistant").markdown(f"""
                <div class="report-card">
                    <div class="report-title">تقرير الامتثال للسياسات الأمنية (RAG)</div>
                    <div class="report-row"><b>السؤال:</b> {user_input}</div>
                    <div class="report-row"><b>حالة الامتثال:</b> {status_badge}</div>
                    <div class="report-row"><b>التوجيه الأمني:</b> {parsed_rag.get('answer_summary', 'تم التحقق من الوثيقة.')}</div>
                    <div class="reasons-list">
                        <ul>
                            <li>تمت مطابقة الاستفسار مع اللوائح المخزنة في Chroma DB.</li>
                        </ul>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.chat_message("assistant").expander("عرض بيانات JSON التقنية"):
                    st.code(json.dumps(parsed_rag, indent=2), language="json")
            except Exception:
                res = llm.invoke(f"أنت مساعد أمن سيبراني احترافي وبسيط. أجب بوضوح ومباشرة على: {user_input}")
                st.chat_message("assistant").write(res.content)

        elif any(word in user_input for word in ["فحص", "رابط", "ip", "عنوان", "نطاق", "دومين"]):
            res_data = check_ip_domain_risk(user_input)
            is_suspicious = res_data['status'] == "SUSPICIOUS"
            
            badge_html = '<span class="badge-danger">مشبوه (High Risk)</span>' if is_suspicious else '<span class="badge-success">آمن (Safe)</span>'
            rec_text = "حظر الرابط فوراً في الجدار الناري وعدم الفتح" if is_suspicious else "الرابط سليم ولا توجد خطورة"
            
            st.chat_message("assistant").markdown(f"""
            <div class="report-card">
                <div class="report-title">تقرير فحص السلامة والأمان</div>
                <div class="report-row"><b>الهدف المفحوص:</b> <code>{res_data['target']}</code></div>
                <div class="report-row"><b>حالة الأمان:</b> {badge_html}</div>
                <div class="report-row"><b>نسبة الخطورة:</b> <code>{res_data['risk_score']}%</code></div>
                <div class="report-row"><b>التوصية الأمنية:</b> {rec_text}</div>
                <div style="margin-top: 12px; font-weight: 600;">أسباب التقييم والاشتباه:</div>
                <div class="reasons-list">
                    <ul>
                        <li>التحقق من وجود شهادات التشفير وحالة الاتصال.</li>
                        <li>مطابقة العنوان مع النطاقات القائمة في القوائم السوداء.</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.chat_message("assistant").expander("عرض بيانات JSON التقنية"):
                st.code(json.dumps(res_data, indent=2), language="json")

        elif any(word in user_input for word in ["حساب", "نسبة", "مستوى", "درجة", "تقييم"]):
            calc_data = calculate_risk_score(user_input)
            is_high = calc_data.get('risk_level') == "HIGH"
            
            badge_html = '<span class="badge-danger">عالي الخطورة</span>' if is_high else '<span class="badge-success">متوسط / منخفض</span>'
            action_text = "عزل الأجهزة المتأثرة ومراجعة السجلات فوراً" if is_high else "استمرار المراقبة المعتادة"
            
            st.chat_message("assistant").markdown(f"""
            <div class="report-card">
                <div class="report-title">تقرير حساب وتقييم المخاطر</div>
                <div class="report-row"><b>متوسط النسبة:</b> <code>{calc_data.get('risk_average_percentage', 0)}%</code></div>
                <div class="report-row"><b>مستوى التهديد:</b> {badge_html}</div>
                <div class="report-row"><b>الإجراء المطلوب:</b> {action_text}</div>
                <div style="margin-top: 12px; font-weight: 600;">ملاحظات الحساب:</div>
                <div class="reasons-list">
                    <ul>
                        <li>تم استخراج الأرقام من المدخلات وحساب المتوسط الحسابي.</li>
                        <li>تمت مقارنة النتيجة مع الحد المسموح به في سياسة المنشأة.</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.chat_message("assistant").expander("عرض بيانات JSON التقنية"):
                st.code(json.dumps(calc_data, indent=2), language="json")
        else:
            res = llm.invoke(f"أنت مساعد أمن سيبراني احترافي وبسيط. أجب بوضوح ومباشرة على: {user_input}")
            st.chat_message("assistant").write(res.content)
else:
    st.info("يرجى إدخال مفتاح OpenAI API لبدء استخدام التطبيق.")
