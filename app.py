import streamlit as st
import pandas as pd
import sqlite3
import datetime
from io import BytesIO

# ==========================================
# 1. إعداد الصفحة والتصميم الاحترافي (RTL & CSS & Responsive A4)
# ==========================================
st.set_page_config(
    page_title="نظام المتابعة الصفية والإشرافية - مدارس الثغر النموذجية",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# كود التنسيق الجمالي المتقدم ودعم الجوال والطباعة A4
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Tajawal', sans-serif !important;
    direction: rtl;
    text-align: right;
    background-color: #f8fafc;
}

/* ترويسة رئيسية جذابة */
.header-box {
    background: linear-gradient(135deg, #1e3a8a 0%, #0d9488 100%);
    color: white;
    padding: 22px;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0 8px 20px rgba(13, 148, 136, 0.2);
}
.header-box h1 {
    color: #ffffff;
    font-weight: 900;
    margin: 0;
    font-size: 26px;
}
.header-box h3 {
    color: #fef08a;
    margin-top: 8px;
    font-weight: 700;
    font-size: 18px;
}

/* بطاقات التنسيق الممركزة والبيانات الأساسية */
.centered-card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 24px;
    margin: 0 auto 25px auto;
    max-width: 1000px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
}
.centered-header {
    text-align: center;
    color: #1e3a8a;
    font-weight: 700;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e2e8f0;
}

/* شكل جمالي متطور للقوائم المنسدلة والحقول */
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 10px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
}
div[data-baseweb="select"] > div:hover {
    border-color: #0d9488 !important;
    box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15) !important;
}
div[data-baseweb="select"] span {
    font-family: 'Tajawal', sans-serif !important;
    font-weight: 600 !important;
    color: #1e293b !important;
}

/* مدخلات النصوص والتواريخ */
.stTextInput input, .stDateInput input, .stTextArea textarea {
    border-radius: 10px !important;
    border: 1.5px solid #cbd5e1 !important;
    font-family: 'Tajawal', sans-serif !important;
    text-align: right !important;
}

/* شارات وشريط دلالات مستويات التقييم */
.badge-container {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    gap: 12px;
    margin-bottom: 15px;
    padding: 10px 15px;
    background-color: #f1f5f9;
    border-radius: 10px;
    direction: rtl;
}
.badge-item {
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 14px;
}
.badge-1 { background-color: #fee2e2; color: #dc2626; }
.badge-2 { background-color: #fef9c3; color: #ca8a04; }
.badge-3 { background-color: #e0f2fe; color: #0369a1; }
.badge-4 { background-color: #dbeafe; color: #1e40af; }
.badge-5 { background-color: #dcfce7; color: #16a34a; }

/* جدول عناصر التقييم الصفي محاذى لليمين بالكامل */
.eval-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
    background-color: #ffffff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    direction: rtl !important;
}
.eval-table th {
    background-color: #eff6ff;
    color: #1e3a8a;
    padding: 12px 15px;
    font-weight: 800;
    font-size: 15px;
    border-bottom: 2px solid #dbeafe;
    text-align: right !important;
}
.eval-table td {
    padding: 12px 15px;
    border-bottom: 1px solid #f1f5f9;
    text-align: right !important;
}

/* محاذاة أزرار الخيارات الراديو (Radio buttons) لليمين */
div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row-reverse !important;
    justify-content: flex-end !important;
    gap: 15px !important;
}

/* التوافق مع الجوال */
@media (max-width: 768px) {
    .header-box h1 { font-size: 20px; }
    .header-box h3 { font-size: 15px; }
    .centered-card { padding: 15px; }
    div[data-testid="column"] { width: 100% !important; margin-bottom: 10px; }
    div[role="radiogroup"] { gap: 8px !important; }
}

/* التنسيق المخصص للطباعة بحجم ورقة A4 portrait */
@media print {
    @page {
        size: A4 portrait;
        margin: 8mm 8mm 8mm 8mm;
    }
    body, .stApp {
        background-color: white !important;
        color: black !important;
    }
    .no-print, header, footer, [data-testid="stSidebar"], .stTabs [role="tablist"], button {
        display: none !important;
    }
    .centered-card {
        box-shadow: none !important;
        border: 1px solid #666 !important;
        max-width: 100% !important;
        width: 100% !important;
        padding: 8px !important;
        margin: 0 !important;
    }
    .header-box {
        background: #1e3a8a !important;
        color: white !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
        padding: 12px !important;
        border-radius: 6px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. إنشاء قاعدة البيانات الدائمة (SQLite)
# ==========================================
DB_FILE = "thagher_evaluations_v7.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT,
            specialization TEXT,
            assigned_subjects TEXT,
            selected_subject TEXT,
            grade TEXT,
            class_name TEXT,
            semester TEXT,
            session_num TEXT,
            visit_num TEXT,
            eval_date TEXT,
            q1_score INTEGER, q2_score INTEGER, q3_score INTEGER, q4_score INTEGER,
            q5_score INTEGER, q6_score INTEGER, q7_score INTEGER, q8_score INTEGER,
            q9_score INTEGER, q10_score INTEGER, q11_score INTEGER, q12_score INTEGER,
            q13_score INTEGER, q14_score INTEGER, q15_score INTEGER, q16_score INTEGER,
            q17_score INTEGER, q18_score INTEGER, q19_score INTEGER, q20_score INTEGER,
            total_score INTEGER,
            notes TEXT,
            signed_teacher TEXT,
            signed_vp TEXT,
            signed_principal TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS custom_teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT UNIQUE,
            specialization TEXT,
            assigned_subjects TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 3. البيانات الأساسية لقائمة المعلمين والإدارة
# ==========================================
DEFAULT_TEACHERS = {
    "محمد سامي السعيد": {"spec": "مهارات رقمية", "subjects": ["مهارات رقمية"]},
    "علي محمد معوض": {"spec": "علوم", "subjects": ["علوم"]},
    "أحمد عبد الحميد سعيد": {"spec": "علوم", "subjects": ["علوم"]},
    "محمد عبد المنعم أبو كيلة": {"spec": "لغة انجليزية", "subjects": ["تربية فنية", "لغة انجليزية"]},
    "هيثم رضا عطية": {"spec": "لغة انجليزية", "subjects": ["تربية فنية", "لغة انجليزية"]},
    "عماد الدين نصر كرم": {"spec": "لغة عربية", "subjects": ["مهارات حياتية", "لغة عربية"]},
    "السيد الغريب بدوي": {"spec": "لغة عربية", "subjects": ["مهارات حياتية", "لغة عربية"]},
    "محمد إبراهيم عبد الرحمن": {"spec": "رياضيات", "subjects": ["رياضيات"]},
    "أسامة أحمد سالم": {"spec": "رياضيات", "subjects": ["مهارات رقمية", "رياضيات"]},
    "عماد بكر عارف": {"spec": "تربية بدنية", "subjects": ["اجتماعيات", "تربية بدنية"]},
    "إبراهيم علي العتيبي": {"spec": "دراسات اسلامية", "subjects": ["اجتماعيات", "اسلامية"]},
    "عيسى خالد العويس": {"spec": "لغة عربية", "subjects": ["اسلامية"]},
    "زيد بن علي التميمي": {"spec": "شريعة اسلامية", "subjects": ["اسلامية"]}
}

def get_all_teachers():
    teachers = DEFAULT_TEACHERS.copy()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT teacher_name, specialization, assigned_subjects FROM custom_teachers")
    rows = c.fetchall()
    conn.close()
    for r in rows:
        name, spec, subs = r[0], r[1], r[2]
        sub_list = [s.strip() for s in subs.split('+') if s.strip()] if '+' in subs else [subs]
        teachers[name] = {"spec": spec, "subjects": sub_list}
    return teachers

GRADE_CLASSES_MAP = {
    "الأول المتوسط": ["1/1", "1/2"],
    "الثاني المتوسط": ["2/1", "2/2", "2/3"],
    "الثالث المتوسط": ["3/1", "3/2", "3/3"]
}

SEMESTERS_LIST = ["الفصل الدراسي الأول", "الفصل الدراسي الثاني"]
SESSIONS_LIST = ["الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة", "السابعة"]
VISITS_LIST = ["الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة", "السابعة", "الثامنة"]

# تهيئة عداد إعادة الضبط للاستمارة الجديدة
if 'form_reset_count' not in st.session_state:
    st.session_state['form_reset_count'] = 0

# ==========================================
# 4. ترويسة البرنامج الرئيسية
# ==========================================
st.markdown("""
<div class="header-box">
    <h1>مدارس الثغر النموذجية الأهلية - القسم المتوسط</h1>
    <h3>نظام المتابعة الصفية والإشرافية للمعلمين</h3>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 استمارة تقييم جديدة",
    "🔍 استرجاع وتعديل / حذف استمارة",
    "➕ إضافة معلم جديد",
    "📊 التقارير العامة (Excel / PDF)"
])

# ==========================================
# التبويب الأول: تقييم معلم جديد
# ==========================================
with tab1:
    st.markdown('<div class="centered-card">', unsafe_allow_html=True)
    
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown('<h2 style="color:#1e3a8a; font-weight:800; margin:0;">📋 البيانات الأساسية للزيارة الصفية</h2>', unsafe_allow_html=True)
    with col_h2:
        if st.button("🔄 بدء استمارة جديدة (100 درجة)", type="secondary", use_container_width=True, key="reset_form_btn"):
            st.session_state['form_reset_count'] += 1
            if 'notes_input_text' in st.session_state:
                st.session_state['notes_input_text'] = ""
            st.rerun()

    teachers_data = get_all_teachers()
    teacher_names = list(teachers_data.keys())
    
    cnt = st.session_state['form_reset_count']
    
    # اختيار المعلم والربط الديناميكي الفوري بالتخصص والمواد
    col_top1, col_top2, col_top3 = st.columns(3)
    
    with col_top1:
        selected_teacher = st.selectbox("اختر اسم المعلم:", teacher_names, key=f"eval_teacher_sel_{cnt}")
        teacher_info = teachers_data[selected_teacher]
        teacher_spec = teacher_info['spec']
        st.text_input("التخصص (مرتبط تلقائياً باسم المعلم):", value=teacher_spec, disabled=True, key=f"spec_in_{selected_teacher}_{cnt}")
        
    with col_top2:
        subjects_list = teacher_info['subjects']
        if len(subjects_list) > 1:
            selected_subject = st.selectbox("المادة المراد تقييمها في هذه الزيارة:", subjects_list, key=f"sub_sel_{selected_teacher}_{cnt}")
        else:
            selected_subject = subjects_list[0]
            st.text_input("المادة المسندة:", value=selected_subject, disabled=True, key=f"sub_in_{selected_teacher}_{cnt}")
            
        selected_semester = st.selectbox("الفصل الدراسي:", SEMESTERS_LIST, key=f"eval_sem_sel_{cnt}")
        
    with col_top3:
        selected_grade = st.selectbox("الصف الدراسي:", list(GRADE_CLASSES_MAP.keys()), key=f"eval_g_sel_{cnt}")
        available_classes = GRADE_CLASSES_MAP[selected_grade]
        selected_class = st.selectbox("الفصل:", available_classes, key=f"class_sel_{selected_grade}_{cnt}")
        
    col_sub1, col_sub2 = st.columns(2)
    with col_sub1:
        selected_session = st.selectbox("الحصة الدراسية:", SESSIONS_LIST, key=f"eval_sess_sel_{cnt}")
    with col_sub2:
        selected_visit = st.selectbox("رقم الزيارة:", VISITS_LIST, key=f"eval_v_sel_{cnt}")
        today_date = st.date_input("التاريخ (ميلادي):", datetime.date.today(), key=f"eval_date_sel_{cnt}")

    st.markdown("---")
    st.markdown('<h3>🎯 عناصر التقييم الصفي الـ 20 (افتراضياً 5 درجات لكل بند = 100/100)</h3>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="badge-container">
        <span style="font-weight:800; color:#1e3a8a; margin-left:15px;">مستويات الأداء والدرجات (من 1 إلى 5 درجات لكل بند):</span>
        <span class="badge-item badge-1">1: ضعيف</span>
        <span class="badge-item badge-2">2: مقبول</span>
        <span class="badge-item badge-3">3: جيد</span>
        <span class="badge-item badge-4">4: جيد جداً</span>
        <span class="badge-item badge-5">5: متميز</span>
    </div>
    """, unsafe_allow_html=True)
    
    # قائمة البنود الـ 20 الكاملة من المصدر
    rubric_items = [
        # المجال الأول: التخطيط
        {"id": "q1", "domain": "التخطيط", "num": 1, "text": "يخطط المعلم/ة للدرس على المنصة تخطيطا متوافقا مع الخطة الفصلية للمقرر."},
        {"id": "q2", "domain": "التخطيط", "num": 2, "text": "متابعة الواجبات المنزلية وتقديم التغذية الراجعة لها."},
        {"id": "q3", "domain": "التخطيط", "num": 3, "text": "ادارة مشاركة الطالب/ة الصوتية والمكتوبة بكفاءة."},
        {"id": "q4", "domain": "التخطيط", "num": 4, "text": "متابعة الطالب/ة وتسجيل الحضور ورصد حالات الغياب في المنصة أو الصف."},
        
        # المجال الثاني: التعلم والتعليم
        {"id": "q5", "domain": "التعلم والتعليم", "num": 5, "text": "ينفذ المعلم/ة إجراءات الدرس وفق خارطة سير الدرس (التمهيد، أنشطة التعلم والتقويم، التقويم الختامي)."},
        {"id": "q6", "domain": "التعلم والتعليم", "num": 6, "text": "الالتزام باللغة العربية الفصحى عند طرح الأسئلة الصفية."},
        {"id": "q7", "domain": "التعلم والتعليم", "num": 7, "text": "يطبق المعلم/ة إستراتيجيات تدريس تراعي قدرات المتعلمين والفروق الفردية بينهم وتتسق مع الموقف التعليمي."},
        {"id": "q8", "domain": "التعلم والتعليم", "num": 8, "text": "يستخدم المعلم/ة أساليب تحفيز تعزز الدافعية لدى المتعلمين."},
        {"id": "q9", "domain": "التعلم والتعليم", "num": 9, "text": "ينخرط المتعلمون في أنشطة تعلم متنوعة ومتمايزة ويجيبون عن أسئلة صفية تنمي مهارات التفكير العليا."},
        {"id": "q10", "domain": "التعلم والتعليم", "num": 10, "text": "يحصل المتعلمون على تغذية راجعة تركز على تحسن أدائهم وفق الموقف التعليمي."},
        {"id": "q11", "domain": "التعلم والتعليم", "num": 11, "text": "يمارس المتعلمون أنشطة أدائية تقيس مدى فهمهم وتمكنهم من المهارات (أنشطة كتابية/ ملفات/ مطويات/ أوراق عمل/ مجسمات /تجارب عملية، إلخ)."},
        {"id": "q12", "domain": "التعلم والتعليم", "num": 12, "text": "يستخدم المتعلمون أدوات رقمية لجمع المعلومات ويوظفونها في عملية التعلم."},
        {"id": "q13", "domain": "التعلم والتعليم", "num": 13, "text": "يربط المتعلمون أنشطة التعلم بتطبيقات عملية من واقع الحياة."},
        {"id": "q14", "domain": "التعلم والتعليم", "num": 14, "text": "يظهر المتعلمون تمكنا من مهارات القراءة والكتابة والحساب، وينمون ثروتهم اللغوية."},
        {"id": "q15", "domain": "التعلم والتعليم", "num": 15, "text": "يتمكن المتعلمون من المعارف والمهارات في المقرر الدراسي بنسبة ما لا يقل عن 85% (اختبار الوحدات والمقننة - اختبار الفترة – الاختبار النهائي)."},
        
        # المجال الثالث: الشخصية المتوازنة
        {"id": "q16", "domain": "الشخصية المتوازنة", "num": 16, "text": "يتمثل المتعلمون القيم الإسلامية والمواطنة والسلوك الصفي الحسن."},
        {"id": "q17", "domain": "الشخصية المتوازنة", "num": 17, "text": "يتحمل المتعلمون مسؤولية تعلمهم ويمارسون التوجه الذاتي (القيادة، التنسيق. الخ) – الصف المقلوب."},
        {"id": "q18", "domain": "الشخصية المتوازنة", "num": 18, "text": "يشارك المتعلمون في أنشطة جماعية ويعملون بروح الفريق ويسود الاحترام المتبادل والتعاطف بينهم."},
        {"id": "q19", "domain": "الشخصية المتوازنة", "num": 19, "text": "يبادر المتعلمون للتعبير عن أفكارهم وآرائهم بثقة ووضوح في بيئة التعلم."},
        {"id": "q20", "domain": "الشخصية المتوازنة", "num": 20, "text": "القدرة على إدارة وضبط النظام داخل الصف وفق القواعد التنظيمية."}
    ]
    
    scores = {}
    
    st.markdown("""
    <table class="eval-table">
        <thead>
            <tr>
                <th style="width: 15%;">المجال</th>
                <th style="width: 5%;">م</th>
                <th style="width: 50%;">عناصر التقييم</th>
                <th style="width: 30%;">الدرجة المحددة (من 1 إلى 5 درجات)</th>
            </tr>
        </thead>
    </table>
    """, unsafe_allow_html=True)
    
    for item in rubric_items:
        col_t1, col_t2, col_t3, col_t4 = st.columns([1.5, 0.5, 5.0, 3.0])
        with col_t1:
            st.markdown(f"<div style='text-align:right; font-weight:700; color:#1e3a8a; padding-top:8px;'>{item['domain']}</div>", unsafe_allow_html=True)
        with col_t2:
            st.markdown(f"<div style='text-align:right; font-weight:700; padding-top:8px;'>{item['num']}</div>", unsafe_allow_html=True)
        with col_t3:
            st.markdown(f"<div style='text-align:right; padding-top:8px; color:#1e293b; line-height:1.5;'>{item['text']}</div>", unsafe_allow_html=True)
        with col_t4:
            # افتراضياً على الخيار رقم 5 (متميز - index 4) لتظهر الدرجة كاملة 100/100
            scores[item['id']] = st.radio(
                f"الدرجة {item['num']}",
                options=[1, 2, 3, 4, 5],
                index=4, # الخيار رقم 5 بشكل افتراضي كامل
                horizontal=True,
                key=f"radio_item_{item['id']}_cnt_{cnt}",
                label_visibility="collapsed"
            )
        st.markdown("<hr style='margin: 3px 0; border: 0.5px solid #f1f5f9;'>", unsafe_allow_html=True)

    # احتساب المجموع النهائي من 100 درجة (20 بند × 5 درجات = 100)
    total_val = sum(scores.values())
    max_val = 100
    percentage = (total_val / max_val) * 100
    
    st.markdown(f"""
    <div style="background-color:#f0fdf4; border:2px solid #bbf7d0; border-radius:14px; padding:18px; text-align:center !important; margin-top:20px; box-shadow:0 4px 12px rgba(22, 163, 74, 0.1);">
        <span style="font-size:22px; font-weight:900; color:#166534;">🌟 المجموع الكلي لدرجات المعلم: {total_val} من {max_val} درجات ({percentage:.1f}%)</span>
    </div>
    """, unsafe_allow_html=True)

    notes_input = st.text_area("توصيات وملحوظات المشرف الزائر:", key=f"notes_input_text_{cnt}")

    st.markdown("---")
    st.subheader("✍️ الاعتمادات والتوقيعات الرسمية")
    
    col_sig1, col_sig2, col_sig3 = st.columns(3)
    
    with col_sig1:
        st.markdown(f"""
        <div style="text-align:right; background:#f8fafc; padding:15px; border-radius:12px; border:1px solid #cbd5e1;">
            <h5 style="color:#1e3a8a; font-weight:800; margin-bottom:8px; text-align:right;">المعلم المطلع</h5>
            <p style="font-weight:700; color:#0f172a; margin-bottom:15px; text-align:right;">{selected_teacher}</p>
            <p style="color:#64748b; margin:0; text-align:right;">التوقيع: __________________</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_sig2:
        st.markdown("""
        <div style="text-align:right; background:#f8fafc; padding:15px; border-radius:12px; border:1px solid #cbd5e1;">
            <h5 style="color:#1e3a8a; font-weight:800; margin-bottom:8px; text-align:right;">وكيل المدرسة للشؤون التعليمية</h5>
            <p style="font-weight:700; color:#0f172a; margin-bottom:15px; text-align:right;">محمد مبروك محمد السيد</p>
            <p style="color:#64748b; margin:0; text-align:right;">التوقيع: __________________</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_sig3:
        st.markdown("""
        <div style="text-align:right; background:#f8fafc; padding:15px; border-radius:12px; border:1px solid #cbd5e1;">
            <h5 style="color:#1e3a8a; font-weight:800; margin-bottom:8px; text-align:right;">مدير المدرسة</h5>
            <p style="font-weight:700; color:#0f172a; margin-bottom:15px; text-align:right;">إبراهيم بن موسى التميمي</p>
            <p style="color:#64748b; margin:0; text-align:right;">التوقيع: __________________</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_save_btn1, col_save_btn2 = st.columns(2)
    with col_save_btn1:
        submit_save = st.button("💾 حفظ استمارة التقييم الحالية (من 100)", type="primary", use_container_width=True, key=f"save_eval_btn_{cnt}")
    with col_save_btn2:
        if st.button("🖨️ طباعة الاستمارة مباشرة (A4)", type="secondary", use_container_width=True, key=f"print_eval_btn_{cnt}"):
            st.components.v1.html("""<script>setTimeout(function() { window.parent.print(); }, 300);</script>""", height=0)

    if submit_save:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        all_subs_str = ", ".join(teacher_info['subjects'])
        c.execute('''
            INSERT INTO evaluations (
                teacher_name, specialization, assigned_subjects, selected_subject, grade, class_name,
                semester, session_num, visit_num, eval_date,
                q1_score, q2_score, q3_score, q4_score, q5_score, q6_score, q7_score, q8_score, q9_score, q10_score,
                q11_score, q12_score, q13_score, q14_score, q15_score, q16_score, q17_score, q18_score, q19_score, q20_score,
                total_score, notes, signed_teacher, signed_vp, signed_principal
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            selected_teacher, teacher_spec, all_subs_str, selected_subject, selected_grade, selected_class,
            selected_semester, selected_session, selected_visit, str(today_date),
            scores['q1'], scores['q2'], scores['q3'], scores['q4'], scores['q5'], scores['q6'], scores['q7'], scores['q8'], scores['q9'], scores['q10'],
            scores['q11'], scores['q12'], scores['q13'], scores['q14'], scores['q15'], scores['q16'], scores['q17'], scores['q18'], scores['q19'], scores['q20'],
            total_val, notes_input, selected_teacher, "محمد مبروك محمد السيد", "إبراهيم بن موسى التميمي"
        ))
        conn.commit()
        conn.close()
        st.success(f"✅ تم حفظ استمارة تقييم المعلم ({selected_teacher}) للتخصص ({teacher_spec}) بنجاح! المجموع: {total_val} من 100.")
        # تعيين استمارة جديدة فارغة ومحددة على 100 درجات تلقائياً بعد الحفظ
        st.session_state['form_reset_count'] += 1
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# التبويب الثاني: استرجاع وتعديل / حذف استمارة
# ==========================================
with tab2:
    st.markdown('<div class="centered-card">', unsafe_allow_html=True)
    st.subheader("🔍 البحث عن استمارة تقييم وإدارتها (تعديل / حذف / طباعة)")
    
    teachers_data = get_all_teachers()
    t_list = list(teachers_data.keys())
    
    if t_list:
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            search_teacher = st.selectbox("اختر اسم المعلم:", t_list, key="search_t_tab2_v7")
        with col_f2:
            search_visit = st.selectbox("اختر رقم الزيارة:", VISITS_LIST, key="search_v_tab2_v7")
        with col_f3:
            st.markdown("<br>", unsafe_allow_html=True)
            btn_start = st.button("🚀 ابدأ البحث", type="primary", use_container_width=True, key="btn_search_tab2_v7")

        if btn_start or st.session_state.get('last_searched_id_v7'):
            conn = sqlite3.connect(DB_FILE)
            df_search = pd.read_sql_query(
                "SELECT * FROM evaluations WHERE teacher_name = ? AND visit_num = ? ORDER BY id DESC LIMIT 1", 
                conn, params=(search_teacher, search_visit)
            )
            conn.close()
            
            if not df_search.empty:
                rec = df_search.iloc[0]
                rec_id = int(rec['id'])
                st.session_state['last_searched_id_v7'] = rec_id
                
                # عرض بطاقة الاستمارة المسترجعة بشكل برمجى نظيف ودون أي تسريب لأكواد HTML
                st.markdown("""
                <div style="border: 2px solid #1e3a8a; border-radius:14px; padding:22px; background-color:#ffffff; direction:rtl; text-align:right;">
                    <h2 style="text-align:center; color:#1e3a8a; font-weight:900; margin-bottom:5px;">مدارس الثغر النموذجية الأهلية - القسم المتوسط</h2>
                    <h4 style="text-align:center; color:#0d9488; font-weight:700; margin-top:0;">بطاقة تقييم الأداء الصفي والزيارة الإشرافية (20 بنداً - 100 درجة)</h4>
                    <hr style="border-top: 2px solid #0d9488; margin: 15px 0;">
                </div>
                """, unsafe_allow_html=True)

                # عرض تفاصيل البيانات الأساسية باستخدام أعمدة Streamlit النظيفة بدلاً من جداول HTML المعقدة
                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.write(f"👤 **اسم المعلم:** {rec['teacher_name']}")
                    st.write(f"🏫 **الصف:** {rec['grade']}")
                    st.write(f"⏱️ **الحصة:** {rec['session_num']}")
                with col_info2:
                    st.write(f"📌 **التخصص:** {rec['specialization']}")
                    st.write(f"🚪 **الفصل:** {rec['class_name']}")
                    st.write(f"🔢 **رقم الزيارة:** {rec['visit_num']}")
                with col_info3:
                    st.write(f"📘 **المادة المزارة:** {rec['selected_subject']}")
                    st.write(f"📅 **الفصل الدراسي:** {rec.get('semester', 'الأول')}")
                    st.write(f"📆 **التاريخ:** {rec['eval_date']}")

                st.markdown("---")
                st.markdown(f"""
                <div style="background-color:#f0fdf4; border:1.5px solid #bbf7d0; border-radius:10px; padding:12px; text-align:right;">
                    <h4 style="color:#166534; margin:0;">📊 ملخص التقييم النهائي:</h4>
                    <p style="font-size:20px; font-weight:800; color:#15803d; margin:5px 0 0 0;">المجموع الكلي: {rec['total_score']} من 100 درجات ({(int(rec['total_score'])):.1f}%)</p>
                    <p style="color:#334155; margin-top:8px;"><b>التوصيات والملحوظات:</b> {rec['notes'] if rec['notes'] else 'لا يوجد'}</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                
                # الاعتمادات الرسمية للتوقيع
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    st.markdown(f"**المعلم المطلع:**\n\n{rec['signed_teacher']}\n\n__________________")
                with col_s2:
                    st.markdown(f"**وكيل الشؤون التعليمية:**\n\n{rec.get('signed_vp', 'محمد مبروك محمد السيد')}\n\n__________________")
                with col_s3:
                    st.markdown(f"**مدير المدرسة:**\n\n{rec.get('signed_principal', 'إبراهيم بن موسى التميمي')}\n\n__________________")

                st.markdown("<br>", unsafe_allow_html=True)
                col_act1, col_act2, col_act3 = st.columns(3)
                
                with col_act1:
                    if st.button("🖨️ طباعة الاستمارة (A4)", type="secondary", use_container_width=True, key="print_rec_btn_v7"):
                        st.components.v1.html("""<script>setTimeout(function() { window.parent.print(); }, 300);</script>""", height=0)
                
                with col_act2:
                    show_edit = st.button("✏️ تعديل هذه الاستمارة", type="primary", use_container_width=True, key="btn_show_edit_v7")
                
                with col_act3:
                    show_delete = st.button("🗑️ حذف هذه الاستمارة", type="primary", use_container_width=True, key="btn_show_del_v7")

                # إجراء الحذف
                if show_delete:
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("DELETE FROM evaluations WHERE id = ?", (rec_id,))
                    conn.commit()
                    conn.close()
                    st.success("✅ تم حذف استمارة التقييم بنجاح من قاعدة البيانات!")
                    st.session_state.pop('last_searched_id_v7', None)
                    st.rerun()

                # إجراء التعديل
                if show_edit or st.session_state.get(f'editing_v7_{rec_id}'):
                    st.session_state[f'editing_v7_{rec_id}'] = True
                    st.markdown("---")
                    st.subheader("✏️ نموذج تعديل الاستمارة")
                    
                    with st.form(f"edit_form_v7_{rec_id}"):
                        new_notes = st.text_area("التوصيات والملحوظات الجديدة:", value=rec['notes'])
                        new_total = st.number_input("المجموع الكلي المعدل (من 100):", min_value=0, max_value=100, value=int(rec['total_score']))
                        save_changes = st.form_submit_button("💾 حفظ التعديلات", type="primary")
                        
                        if save_changes:
                            conn = sqlite3.connect(DB_FILE)
                            c = conn.cursor()
                            c.execute("UPDATE evaluations SET notes = ?, total_score = ? WHERE id = ?", (new_notes, new_total, rec_id))
                            conn.commit()
                            conn.close()
                            st.success("✅ تم تحديث بيانات الاستمارة بنجاح!")
                            st.session_state.pop(f'editing_v7_{rec_id}', None)
                            st.rerun()
            else:
                st.warning("⚠️ لم يتم العثور على استمارة تقييم مسجلة لهذا المعلم في الزيارة المحددة.")
    else:
        st.info("ℹ️ لا توجد بيانات معلمين مسجلة.")
        
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# التبويب الثالث: إضافة معلم جديد
# ==========================================
with tab3:
    st.markdown('<div class="centered-card">', unsafe_allow_html=True)
    st.subheader("➕ إضافة معلم جديد إلى قائمة النظام")
    
    with st.form("add_teacher_form_v7", clear_on_submit=True):
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            new_t_name = st.text_input("اسم المعلم الثلاثي/الرباعي:")
        with col_t2:
            new_t_spec = st.text_input("التخصص:")
        with col_t3:
            new_t_subj = st.text_input("المواد المسندة (افصل بين المواد بـ +):")
            
        btn_add_t = st.form_submit_button("➕ حفظ المعلم الجديد", type="primary", use_container_width=True)
        
        if btn_add_t:
            if new_t_name.strip() and new_t_spec.strip():
                try:
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("INSERT INTO custom_teachers (teacher_name, specialization, assigned_subjects) VALUES (?, ?, ?)",
                              (new_t_name.strip(), new_t_spec.strip(), new_t_subj.strip()))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ تم إدراج المعلم ({new_t_name}) وتخصصه ({new_t_spec}) بنجاح إلى قائمة المعلمين!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("⚠️ هذا المعلم مسجل بالفعل في القائمة.")
            else:
                st.warning("⚠️ يرجى إدخال اسم المعلم وتخصصه على الأقل.")
                
    st.markdown("---")
    st.subheader("📋 قائمة المعلمين المسجلين حالياً والربط بالتخصص والمواد")
    teachers_dict = get_all_teachers()
    if teachers_dict:
        t_df = pd.DataFrame([
            {"اسم المعلم": k, "التخصص": v['spec'], "المواد المسندة": ", ".join(v['subjects'])} 
            for k, v in teachers_dict.items()
        ])
        st.dataframe(t_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# التبويب الرابع: التقارير العامة (Excel / PDF)
# ==========================================
with tab4:
    st.markdown('<div class="centered-card">', unsafe_allow_html=True)
    st.subheader("📑 التقرير العام لجميع المعلمين والتصدير")
    
    conn = sqlite3.connect(DB_FILE)
    df_all = pd.read_sql_query("SELECT * FROM evaluations ORDER BY id DESC", conn)
    conn.close()

    if not df_all.empty:
        st.dataframe(df_all, use_container_width=True)
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            output_excel = BytesIO()
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                df_all.to_excel(writer, index=False, sheet_name='تقييمات المعلمين')
            excel_bytes = output_excel.getvalue()
            
            st.download_button(
                label="📊 تحميل تقرير كافة المعلمين (Excel)",
                data=excel_bytes,
                file_name=f"تقرير_تقييم_معلمي_الثغر_{datetime.date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
        with col_exp2:
            if st.button("🖨️ طباعة وتصدير التقرير الكلي (PDF)", use_container_width=True, key="print_all_btn_v7"):
                st.components.v1.html("""<script>setTimeout(function() { window.parent.print(); }, 300);</script>""", height=0)
    else:
        st.info("ℹ️ لا توجد بيانات مسجلة في قاعدة البيانات حتى الآن.")
        
    st.markdown('</div>', unsafe_allow_html=True)

       
