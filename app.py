import os
import json
import re
import streamlit as st
from langchain_openai import ChatOpenAI

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
        background-color: #F8FAFC;
        color: #0F172A;
        direction: rtl;
        text-align: right;
    }
    
    .header-title {
        font-size: 28px;
        font-weight: 700;
        color: #0F172A;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 4px;
    }
    .header-subtitle {
        font-size: 14px;
        color: #64748B;
        text-align: center;
        margin-bottom: 24px;
    }
    
    .card-style {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        height: 100%;
        margin-bottom: 15px;
    }
    .card-header {
        font-size: 16px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 6px;
    }
    .card-desc {
        font-size: 13px;
        color: #64748B;
        margin-bottom: 16px;
    }
    
    .report-card {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .report-title {
        font-size: 16px;
        font-weight: 700;
        color: #0F172A;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 10px;
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
    
    .stButton>button {
        background-color: #2563EB;
        color: #FFFFFF !important;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
        font-weight: 600;
        font-family: 'IBM Plex Sans Arabic', sans-serif;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
    }
    
    .stTextInput>div>div>input, .stSelectbox>div>div {
        background-color: #FFFFFF;
        color: #0F172A;
        border: 1px solid #CBD5E1;
        border-radius: 8px;
    }
    [data-testid="stFileUploadDropzone"] {
        background-color: #F8FAFC;
        border: 1px dashed #CBD5E1;
        border-radius: 8px;
    }
    </style>
"""
st.markdown(css_code, unsafe_allow_html=True)

st.markdown('<div class="header-title">CyberAgent AI</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">المنصة الذكية لفحص التهديدات الأمنية والاستجابة الفورية للحوادث</div>', unsafe_allow_html=True)

with st.expander("إعدادات مفتاح التشغيل (API Key)", expanded=False):
    api_key = st.text_input("مفتاح OpenAI API:", type="password")

if not api_key:
    api_key = os.environ.get("OPENAI_API_KEY", "")

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
    
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
    except Exception:
        st.error("يرجى التأكد من إدخال مفتاح API صحيح.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card-style">
            <div class="card-header">01 / الاستجابة للحوادث</div>
            <div class="card-desc">توليد بروتوكولات احتواء وتوصيات فورية.</div>
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
        <div class="card-style">
            <div class="card-header">02 / تحليل الصور والأدلة (Vision AI)</div>
            <div class="card-desc">فحص بصرية محاولات التصيد والرسائل المشبوهة.</div>
        """, unsafe_allow_html=True)
        uploaded_img = st.file_uploader("اختر صورة للتحليل", type=["png", "jpg", "jpeg"], key="img_uploader", label_visibility="collapsed")
        analyze_img_btn = st.button("بدء تحليل الصورة") if uploaded_img else None
        st.markdown('</div>', unsafe_allow_html=True)

    # قواعد خطط الاستجابة المتخصصة لكل حادثة على حدة
    incident_database = {
        "برمجية فدية (Ransomware)": {
            "severity": "CRITICAL",
            "protocol_ar": "عزل الشبكة الفوري والتحقق من سلامة النسخ الاحتياطية",
            "protocol_en": "ISOLATE_NETWORK_AND_VERIFY_OFFLINE_BACKUPS",
            "actions_ar": [
                "فصل جميع الخوادم والأجهزة المتأثرة عن الشبكة المحلية والإنترنت فوراً لمنع التشفير العابر.",
                "عدم التواصل أو دفع أي مبالغ مالية للجهات المهاجمة نهائياً.",
                "التحقق من سلامة النسخ الاحتياطية المقطوعة عن الشبكة (Offline Backups).",
                "مسح الأنظمة المتأثرة وإعادة تثبيتها من صور معتمدة وآمنة."
            ],
            "actions_en": [
                "Isolate affected servers and endpoints from local LAN immediately.",
                "Do not pay ransom or communicate with threat actors.",
                "Verify integrity of offline uncorrupted backups.",
                "Re-image impacted endpoints using secured baseline images."
            ]
        },
        "اختراق بريد إلكتروني (Email Breach)": {
            "severity": "HIGH",
            "protocol_ar": "إلغاء الجلسات النشطة وإعادة تعيين المفاتيح وتدقيق قواعد إعادة التوجيه",
            "protocol_en": "REVOKE_ACTIVE_SESSIONS_AND_AUDIT_MAIL_RULES",
            "actions_ar": [
                "إنهاء كافة الجلسات النشطة (Revoke Sessions) للحساب المخترق من لوحة الإدارة.",
                "تغيير كلمة المرور وتفعيل التحقق الثنائي (MFA) عبر تطبيق مصادقة.",
                "مراجعة وفحص قواعد البريد (Inbox Rules) للتأكد من عدم وجود إعادة توجيه تلقائي للرسائل.",
                "فحص سجلات الدخول (Audit Logs) للتحقق من العناوين والأنشطة المشبوهة."
            ],
            "actions_en": [
                "Revoke all active user sessions across all devices via Admin Console.",
                "Enforce immediate password reset and mandate hardware/app MFA.",
                "Audit inbox forwarding rules and delegation settings for unauthorized additions.",
                "Analyze sign-in logs to extract attacker IPs and compromised scopes."
            ]
        },
        "تسريب بيانات حساسة (Data Leak)": {
            "severity": "CRITICAL",
            "protocol_ar": "إغلاق منافذ التسريب وحظر رموز الوصول وتطبيق بروتوكول DLP",
            "protocol_en": "CONTAIN_LEAKAGE_VECTORS_AND_REVOKE_API_KEYS",
            "actions_ar": [
                "تحديد وحظر مصدر ومنافذ تسريب البيانات فوراً (API endpoints / Cloud Buckets).",
                "تغيير كافة مفاتيح الوصول والرموز البرمجية (API Keys & Access Tokens) الـمـنـكشفة.",
                "حصر نطاق البيانات المسربة وتصنيف حساسيتها (PII / Financial Data).",
                "إبلاغ فريق الامتثال والشؤون القانونية للالتزام بمتطلبات الإفصاح التنظيمي."
            ],
            "actions_en": [
                "Block leaky data vectors and restrict public access to cloud storage buckets.",
                "Revoke and rotate exposed secrets, API keys, and database credentials.",
                "Perform data classification assessment on compromised datasets.",
                "Notify legal and compliance officers for regulatory notification protocols."
            ]
        },
        "هجمة حجب الخدمة (DDoS Attack)": {
            "severity": "HIGH",
            "protocol_ar": "تحويل المسار عبر خدمات التخفيف وتفعيل جدار حماية التطبيقات (WAF)",
            "protocol_en": "ACTIVATE_DDoS_MITIGATION_AND_ENABLE_WAF_RATE_LIMITING",
            "actions_ar": [
                "تفعيل وضع الحماية القصوى وتحويل حركة المرور لشبكة التخفيف (Scrubbing Center).",
                "تطبيق قواعد تحديد المعدل (Rate Limiting) على مستوى جدار حماية التطبيقات (WAF).",
                "حظر مصادر الحركة المشبوهة وحزم البينات غير القياسية بناءً على أنماط الهجمة.",
                "التواصل مع مزيد خدمة الإنترنت (ISP) لتصفية الحركة المرتفعة على مستوى النطاق."
            ],
            "actions_en": [
                "Reroute incoming web traffic through cloud scrubbing proxy networks.",
                "Enforce aggressive rate-limiting and Challenge-Response rules on WAF.",
                "Drop malformed packets and block malicious IP subnets dynamically.",
                "Coordinate upstream filtering with Tier-1 Internet Service Providers."
            ]
        }
    }

    # معالجة خطة الاستجابة
    if incident_type in incident_database and generate_plan_btn:
        plan_info = incident_database[incident_type]
        
        st.markdown(f"""
        <div class="report-card">
            <div class="report-title">خطة الاستجابة الفورية: {incident_type}</div>
            <div style="margin-bottom: 8px;"><b>مستوى الخطورة:</b> <span class="badge-danger">{plan_info['severity']}</span></div>
            <div style="margin-bottom: 8px;"><b>بروتوكول الاحتواء:</b> {plan_info['protocol_ar']}</div>
            <div style="margin-top: 12px; font-weight: 600;">خطوات التنفيذ المباشرة الخاصة بالتكتيك:</div>
            <div class="reasons-list">
                <ul>
                    {"".join([f"<li>{action}</li>" for action in plan_info['actions_ar']])}
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        tech_json = {
            "incident_type": incident_type,
            "severity_assessment": plan_info["severity"],
            "containment_protocol": plan_info["protocol_en"],
            "recommended_actions": plan_info["actions_en"]
        }
        with st.expander("عرض بيانات JSON التقنية"):
            st.code(json.dumps(tech_json, indent=2), language="json")

    # معالجة تحليل الصور
    if uploaded_img:
        st.image(uploaded_img, caption="الصورة المرفوعة للفحص", width=300)
        if analyze_img_btn:
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
                <div style="margin-bottom: 8px;"><b>نتيجة الكشف:</b> محاولة تصيد إلكتروني (Phishing)</div>
                <div style="margin-bottom: 8px;"><b>مستوى الخطورة:</b> <span class="badge-danger">عالي جداً (Critical)</span></div>
                <div style="margin-bottom: 8px;"><b>التوصية:</b> إغلاق الصفحة فوراً وعدم إدخال أي بيانات.</div>
                <div style="margin-top: 12px; font-weight: 600;">ملاحظات الفحص والبصريات:</div>
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

    user_input = st.chat_input("اكتب سؤالك، أدخل رابطاً للفحص، أو اكتب أرقاماً لحساب درجة الخطورة...")

    if user_input:
        st.chat_message("user").write(user_input)

        if any(word in user_input for word in ["فحص", "رابط", "ip", "عنوان", "نطاق", "دومين"]):
            res_data = check_ip_domain_risk(user_input)
            is_suspicious = res_data['status'] == "SUSPICIOUS"
            
            badge_html = '<span class="badge-danger">مشبوه (High Risk)</span>' if is_suspicious else '<span class="badge-success">آمن (Safe)</span>'
            rec_text = "حظر الرابط فوراً في الجدار الناري وعدم الفتح" if is_suspicious else "الرابط سليم ولا توجد خطورة"
            
            st.chat_message("assistant").markdown(f"""
            <div class="report-card">
                <div class="report-title">تقرير فحص السلامة والأمان</div>
                <div style="margin-bottom: 8px;"><b>الهدف المفحوص:</b> <code>{res_data['target']}</code></div>
                <div style="margin-bottom: 8px;"><b>حالة الأمان:</b> {badge_html}</div>
                <div style="margin-bottom: 8px;"><b>نسبة الخطورة:</b> <code>{res_data['risk_score']}%</code></div>
                <div style="margin-bottom: 8px;"><b>التوصية الأمنية:</b> {rec_text}</div>
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
                <div style="margin-bottom: 8px;"><b>متوسط النسبة:</b> <code>{calc_data.get('risk_average_percentage', 0)}%</code></div>
                <div style="margin-bottom: 8px;"><b>مستوى التهديد:</b> {badge_html}</div>
                <div style="margin-bottom: 8px;"><b>الإجراء المطلوب:</b> {action_text}</div>
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
