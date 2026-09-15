import streamlit as st
import sqlite3
import pandas as pd
import datetime

# --- Page Config ---
st.set_page_config(
    page_title="برنامج تدوين ومعالجة المخالفات السلوكية - متوسطة الثغر النموذجية الأهلية",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom RTL CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    .main-title {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        margin-bottom: 25px;
    }
    .main-title h1 {
        font-size: 24px;
        font-weight: 800;
        margin: 0;
        color: #ffffff;
    }
    .main-title h3 {
        font-size: 16px;
        font-weight: 600;
        margin-top: 8px;
        color: #e0e6ed;
    }

    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-right: 5px solid #2a5298;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }
    
    .status-pending {
        background-color: #fff3cd;
        color: #856404;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }
    
    .status-completed {
        background-color: #d4edda;
        color: #155724;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }

    /* Print Styles */
    @media print {
        body * {
            visibility: hidden;
        }
        #printable-report, #printable-report * {
            visibility: visible;
        }
        #printable-report {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            padding: 20px;
            font-size: 14pt;
        }
        .no-print {
            display: none !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Database Setup & Helper Functions ---
DB_PATH = "school_discipline.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Saudi Behavioral Rules Dictionary
RULES_DICT = {
    "الدرجة الأولى (مخالفات بسيطة)": [
        "عدم الالتزام بالزي المدرسي أو الترتيب العام",
        "التأخر عن الاصطفاف الصباحي أو الحصص الدراسية دون عذر",
        "النوم داخل الفصل أو الاستلقاء أثناء الشرح",
        "العبث بالأجهزة أو أدوات الفصل البسيطة",
        "تناول الأطعمة والمشروبات أثناء الحصص",
        "استخدام الهواتف والأجهزة الذكية دون إذن"
    ],
    "الدرجة الثانية (مخالفات متوسطة)": [
        "الغياب عن المدرسة بدون عذر مقبول",
        "الخروج من الفصل دون استئذان معلم الحصة",
        "إثارة الفوضى داخل الفصل أو الفناء المدرسي",
        "الشجار والمشادات الكلامية مع الزملاء",
        "السلوك العدواني البسيط تجاه الآخرين",
        "الكتابة على الجدران أو الطاولات المدرسية"
    ],
    "الدرجة الثالثة (مخالفات جسيمة)": [
        "الهروب من المدرسة أثناء اليوم الدراسي",
        "التنمر والتنمر الإلكتروني ضد الطلاب",
        "حيازة أجهزة أو مواد ممنوعة داخل المدرسة",
        "التلفظ بألفاظ غير لائقة على المعلمين أو الإداريين",
        "المشاجرات الجماعية أو التحريض عليها",
        "إلحاق الضرر المتعمد بممتلكات المدرسة أو زملائه"
    ],
    "الدرجة الرابعة إلى السادسة (مخالفات خطيرة)": [
        "حيازة السجائر الإلكترونية أو مواد التدخين",
        "الاعتداء الجسدي الصريح على أحد منسوبي المدرسة",
        "إحضار أدوات حادة أو خطرة إلى المدرسة",
        "تزوير الوثائق أو التوقيعات الرسمية",
        "السرقة أو التعدي المتعمد على ممتلكات المدرسة"
    ]
}

PROCEDURES_DICT = {
    "الدرجة الأولى (مخالفات بسيطة)": [
        "تنبيه شفهي انفرادي من المعلم للطالب",
        "توقيع تعهد خطي على الطالب بعدم التكرار",
        "التواصل الهاتفي مع ولي الأمر وإشعاره بالمخالفة",
        "أخذ التزام خطي وتحويله للموجه الطلابي للدراسة"
    ],
    "الدرجة الثانية (مخالفات متوسطة)": [
        "إشعار ولي الأمر كتابياً وتوقيع التعهد السلوكي",
        "خصم (درجة واحدة) من درجات الانضباط والسلوك",
        "خصم (درجتان) من درجات الانضباط وحسم ساعات التأخر",
        "إحالة الطالب للموجه الطلابي لوضع خطة تعديل سلوك"
    ],
    "الدرجة الثالثة (مخالفات جسيمة)": [
        "استدعاء ولي أمر الطالب فوراً للمدرسة لمقابلة الوكيل",
        "خصم (3 إلى 5 درجات) من درجات السلوك وتوقيع العقد السلوكي",
        "حرمان الطالب من المشاركة في الأنشطة المدرسية مؤقتاً",
        "نقل الطالب من فصله الحالي إلى فصل آخر بالمدرسة"
    ],
    "الدرجة الرابعة إلى السادسة (مخالفات خطيرة)": [
        "رفع القضية فوراً إلى لجنة التوجيه الطلابي والإدارة",
        "خصم الدرجات المعتمدة حسب لائحة السلوك الوطنية",
        "نقل الطالب إلى مدرسة أخرى بالتنسيق مع إدارة التعليم",
        "تطبيق إجراءات الفصل المؤقت مع متابعة ولي الأمر"
    ]
}

# Ensure Database Tables Exist
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            grade TEXT NOT NULL,
            section TEXT NOT NULL,
            status TEXT DEFAULT 'نشط'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS vps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            student_name TEXT NOT NULL,
            grade TEXT NOT NULL,
            section TEXT NOT NULL,
            period TEXT NOT NULL,
            teacher_name TEXT NOT NULL,
            violation_degree TEXT NOT NULL,
            problem_title TEXT NOT NULL,
            description TEXT,
            reported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'قيد المعالجة',
            action_taken TEXT,
            vp_notes TEXT,
            vp_name TEXT,
            action_date DATETIME
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- Header ---
st.markdown("""
<div class="main-title">
    <h1>المملكة العربية السعودية - وزارة التعليم</h1>
    <h3>تدوين ومعالجة المخالفات السلوكية والانضباط المدرسي والمحافظة على حقوق المتعلم</h3>
    <p style="margin-top: 5px; font-weight: bold; color: #ffd700;">متوسطة الثغر النموذجية الأهلية - بنين</p>
</div>
""", unsafe_allow_html=True)

# --- Navigation Sidebar ---
st.sidebar.title("📌 القائمة الرئيسية")
page = st.sidebar.radio(
    "اختر الشاشة المطلوب عرضها:",
    [
        "👨‍🏫 شاشة المعلم (رصد المخالفة)",
        "👔 شاشة وكيل الشؤون المدرسية/الطلاب",
        "🔍 البحث عن سجِّل طالب",
        "👥 إدارة الطلاب (إضافة / حذف / نقل)",
        "🖨️ طباعة وتصدير التقارير"
    ]
)

# ---------------------------------------------------------
# Page 1: Teacher Screen (رصد المخالفة)
# ---------------------------------------------------------
if page == "👨‍🏫 شاشة المعلم (رصد المخالفة)":
    st.subheader("👨‍🏫 صفحة المعلم - رصد بلاغ مخالفة سلوكية")
    
    conn = get_db_connection()
    teachers = [row['name'] for row in conn.execute("SELECT name FROM teachers").fetchall()]
    conn.close()
    
    col1, col2 = st.columns(2)
    with col1:
        teacher_name = st.selectbox("اسم المعلم الراصد:", teachers if teachers else ["أحمد عبدالملك السعيد"])
        grade = st.selectbox("الصف الدراسي:", ["الأول المتوسط", "الثاني المتوسط", "الثالث المتوسط"])
    with col2:
        section = st.selectbox("الفصل:", ["1", "2", "3"])
        period = st.selectbox("الحصة الدراسية:", ["الحصة الأولى", "الحصة الثانية", "الحصة الثالثة", "الحصة الرابعة", "الحصة الخامسة", "الحصة السادسة", "الحصة السابعة"])
    
    st.markdown("---")
    st.subheader("🎯 اختيار الطالب المعني")
    
    # Fetch students for selected Grade and Section
    conn = get_db_connection()
    query = "SELECT student_id, name FROM students WHERE grade = ? AND section = ? AND status = 'نشط' ORDER BY name"
    students_list = conn.execute(query, (grade, section)).fetchall()
    conn.close()
    
    # Search box for student
    search_term = st.text_input("🔍 بحث عن اسم طالب في الفصل/الصف (اختياري للتصفية):", "")
    
    filtered_students = {}
    for s in students_list:
        display_str = f"{s['name']} - (رقم الطالب: {s['student_id']})"
        if search_term.strip() == "" or search_term.strip() in s['name'] or search_term.strip() in s['student_id']:
            filtered_students[display_str] = (s['student_id'], s['name'])
            
    if filtered_students:
        selected_student_str = st.selectbox("اختر الطالب من القائمة المنسدلة:", list(filtered_students.keys()))
        selected_student_id, selected_student_name = filtered_students[selected_student_str]
    else:
        st.warning("⚠️ لا يوجد طلاب مطابقون لخيارات الصف والفصل المحددة أو كلمة البحث.")
        selected_student_id, selected_student_name = None, None

    st.markdown("---")
    st.subheader("⚠️ تفاصيل المشكلة السلوكية حسب قواعد السلوك والمواظبة")
    
    col_deg, col_prob = st.columns(2)
    with col_deg:
        violation_degree = st.selectbox("درجة المخالفة السلوكية:", list(RULES_DICT.keys()))
    with col_prob:
        problem_title = st.selectbox("المشكلة السلوكية المرصودة:", RULES_DICT[violation_degree])
        
    description = st.text_area("وصف وتفاصيل المشكلة السلوكية (تفاصيل الواقعة من المعلم):", height=120, placeholder="اكتب هنا ما حدث بالتفصيل داخل الفصل أو الحصة...")

    if st.button("📤 إرسال البلاغ إلى وكيل الشؤون المدرسية", type="primary", use_container_width=True):
        if not selected_student_id:
            st.error("❌ يرجى اختيار الطالب أولاً قبل إرسال البلاغ.")
        elif not description.strip():
            st.error("❌ يرجى كتابة وصف وتفاصيل المشكلة السلوكية.")
        else:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('''
                INSERT INTO violations (student_id, student_name, grade, section, period, teacher_name, violation_degree, problem_title, description, reported_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'قيد المعالجة')
            ''', (selected_student_id, selected_student_name, grade, section, period, teacher_name, violation_degree, problem_title, description, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            violation_id = c.lastrowid
            conn.close()
            
            st.success(f"✅ تم تسجيل ورصد المخالفة بنجاح! الرقم المرجعي للبلاغ: #{violation_id}. تم تحويل البلاغ فوريًا إلى شاشة وكيل الشؤون المدرسية.")

# ---------------------------------------------------------
# Page 2: Vice Principal Screen (شاشة الوكيل)
# ---------------------------------------------------------
elif page == "👔 شاشة وكيل الشؤون المدرسية/الطلاب":
    st.subheader("👔 شاشة وكيل الشؤون المدرسية ووكيل شؤون الطلاب")
    
    conn = get_db_connection()
    vps = [row['name'] for row in conn.execute("SELECT name FROM vps").fetchall()]
    conn.close()
    
    vp_name = st.selectbox("اسم الوكيل المعالج للبلاغ:", vps if vps else ["أ. عبدالرحمن بن سعد الماجد (وكيل شؤون الطلاب)"])
    
    tab_pending, tab_completed = st.tabs(["📋 البلاغات قيد المعالجة والانتظار", "✅ البلاغات المكتملة والمُعقعة"])
    
    with tab_pending:
        conn = get_db_connection()
        pending_violations = conn.execute("SELECT * FROM violations WHERE status = 'قيد المعالجة' ORDER BY id DESC").fetchall()
        conn.close()
        
        if not pending_violations:
            st.info("🎉 لا توجد مخالفات قيد المعالجة حالياً. جميع البلاغات تم اتخاذ الإجراءات اللازمة بشأنها.")
        else:
            for v in pending_violations:
                with st.expander(f"🔴 بلاغ #{v['id']} | الطالب: {v['student_name']} ({v['grade']} - فصل {v['section']}) | المعلم: {v['teacher_name']}"):
                    st.write(f"**رقم الطالب:** {v['student_id']}")
                    st.write(f"**تاريخ ووقت الرصد:** {v['reported_at']}")
                    st.write(f"**الحصة الدراسية:** {v['period']}")
                    st.write(f"**درجة المخالفة:** {v['violation_degree']}")
                    st.write(f"**المشكلة السلوكية:** {v['problem_title']}")
                    st.info(f"**وصف المعلم للواقعة:** {v['description']}")
                    
                    st.markdown("#### ⚖️ اتخاذ الإجراء النظامي حسب قواعد السلوك والمواظبة:")
                    
                    # Available procedures for this degree
                    avail_procedures = PROCEDURES_DICT.get(v['violation_degree'], PROCEDURES_DICT["الدرجة الأولى (مخالفات بسيطة)"])
                    
                    selected_action = st.selectbox(f"اختر الإجراء المطلوب اتخاذه لبلاغ #{v['id']}:", avail_procedures, key=f"act_{v['id']}")
                    vp_notes = st.text_area(f"ملاحظات وكيل الشؤون المدرسية/الطلاب (بلاغ #{v['id']}):", key=f"notes_{v['id']}", placeholder="تدوين توجيهات الوكيل، التوصيات، نتيجة التواصل مع ولي الأمر...")
                    
                    if st.button(f"💾 حفظ وتأكيد الإجراء لبلاغ #{v['id']}", type="primary", key=f"btn_save_{v['id']}"):
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute('''
                            UPDATE violations 
                            SET status = 'تم اتخاذ الإجراء', action_taken = ?, vp_notes = ?, vp_name = ?, action_date = ?
                            WHERE id = ?
                        ''', (selected_action, vp_notes, vp_name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), v['id']))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ تم حفظ الإجراء الإداري والتنفيذي لبلاغ #{v['id']} وتوثيقه بنجاح!")
                        st.rerun()

    with tab_completed:
        conn = get_db_connection()
        completed_violations = conn.execute("SELECT * FROM violations WHERE status = 'تم اتخاذ الإجراء' ORDER BY id DESC").fetchall()
        conn.close()
        
        if not completed_violations:
            st.info("لا توجد بلاغات مكتملة حالياً.")
        else:
            for v in completed_violations:
                with st.expander(f"🟢 بلاغ مـعالج #{v['id']} | الطالب: {v['student_name']} | الإجراء: {v['action_taken']}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**المعلم الراصد:** {v['teacher_name']}")
                        st.write(f"**الصف والفصل:** {v['grade']} - فصل {v['section']}")
                        st.write(f"**المشكلة:** {v['problem_title']}")
                        st.write(f"**وصف المشكلة:** {v['description']}")
                    with col_b:
                        st.write(f"**الوكيل المعالج:** {v['vp_name']}")
                        st.write(f"**الإجراء المتخذ:** {v['action_taken']}")
                        st.write(f"**ملاحظات الوكيل:** {v['vp_notes']}")
                        st.write(f"**تاريخ الإجراء:** {v['action_date']}")

# ---------------------------------------------------------
# Page 3: Search Student Record (البحث عن سجّل طالب)
# ---------------------------------------------------------
elif page == "🔍 البحث عن سجِّل طالب":
    st.subheader("🔍 خيار البحث عن سجل طالب وتاريخ المخالفات")
    
    search_q = st.text_input("أدخل اسم الطالب أو رقم الهوية/رقم الطالب للبحث الشامل:", placeholder="مثال: عبدالرحمن، 1166753291...")
    
    if search_q.strip():
        conn = get_db_connection()
        st_query = "SELECT * FROM students WHERE name LIKE ? OR student_id LIKE ?"
        found_students = conn.execute(st_query, (f"%{search_q}%", f"%{search_q}%")).fetchall()
        
        if not found_students:
            st.warning("⚠️ لم يتم العثور على طالب يطابق البحث.")
        else:
            for student in found_students:
                st.markdown(f"""
                <div class="card">
                    <h4>🎓 الطالب: {student['name']}</h4>
                    <p><b>رقم الطالب:</b> {student['student_id']} | <b>الصف:</b> {student['grade']} | <b>الفصل:</b> {student['section']} | <b>الحالة:</b> {student['status']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                v_query = "SELECT * FROM violations WHERE student_id = ? ORDER BY id DESC"
                st_violations = conn.execute(v_query, (student['student_id'],)).fetchall()
                
                if not st_violations:
                    st.success("🎉 سجل الطالب نظيف خالٍ من أي مخالفات سلوكية مرصودة.")
                else:
                    st.write(f"📊 **عدد المخالفات المسجلة بحق الطالب:** ({len(st_violations)}) مخالفة")
                    df_v = pd.DataFrame([dict(v) for v in st_violations])
                    st.dataframe(
                        df_v[['id', 'reported_at', 'teacher_name', 'period', 'violation_degree', 'problem_title', 'status', 'action_taken', 'vp_notes']],
                        column_config={
                            "id": "رقم البلاغ",
                            "reported_at": "تاريخ الرصد",
                            "teacher_name": "المعلم الراصد",
                            "period": "الحصة",
                            "violation_degree": "الدرجة",
                            "problem_title": "المشكلة السلوكية",
                            "status": "حالة البلاغ",
                            "action_taken": "الإجراء المتخذ",
                            "vp_notes": "ملاحظات الوكيل"
                        },
                        use_container_width=True
                    )
        conn.close()

# ---------------------------------------------------------
# Page 4: Student Management (إضافة / حذف / نقل طالب)
# ---------------------------------------------------------
elif page == "👥 إدارة الطلاب (إضافة / حذف / نقل)":
    st.subheader("👥 شاشة إدارة الطلاب (إضافة طالب - حذف طالب - نقل طالب من فصل لآخر)")
    
    action_type = st.radio("اختر العملية المطلوبة:", ["➕ إضافة طالب جديد", "🚚 نقل طالب من فصل إلى آخر", "❌ حذف طالب من المدرسة"], horizontal=True)
    
    if action_type == "➕ إضافة طالب جديد":
        st.markdown("### ➕ إضافة طالب جديد للقاعدة")
        col_new1, col_new2 = st.columns(2)
        with col_new1:
            new_id = st.text_input("رقم الطالب / الهوية الوطنية:")
            new_name = st.text_input("اسم الطالب الخماسي/الرباعي:")
        with col_new2:
            new_grade = st.selectbox("الصف الدراسي:", ["الأول المتوسط", "الثاني المتوسط", "الثالث المتوسط"], key="add_g")
            new_section = st.selectbox("الفصل:", ["1", "2", "3"], key="add_s")
            
        if st.button("💾 حفظ الطالب الجديد", type="primary"):
            if not new_id.strip() or not new_name.strip():
                st.error("❌ يرجى ملء كافة الحقول المطلوبة (رقم الطالب والاسم).")
            else:
                try:
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("INSERT INTO students (student_id, name, grade, section) VALUES (?, ?, ?, ?)", (new_id.strip(), new_name.strip(), new_grade, new_section))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ تم إضافة الطالب ({new_name}) بنجاح إلى الصف {new_grade} فصل {new_section}!")
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء الإضافة: ربما رقم الطالب موجود سابقاً ({e}).")

    elif action_type == "🚚 نقل طالب من فصل إلى آخر":
        st.markdown("### 🚚 نقل طالب من فصل لآخر")
        
        conn = get_db_connection()
        all_students = conn.execute("SELECT student_id, name, grade, section FROM students WHERE status = 'نشط' ORDER BY name").fetchall()
        conn.close()
        
        student_dict = {f"{s['name']} (رقم: {s['student_id']}) - حالياً: {s['grade']} فصل {s['section']}": s for s in all_students}
        
        if student_dict:
            selected_st_key = st.selectbox("اختر الطالب المراد نقله:", list(student_dict.keys()))
            student_obj = student_dict[selected_st_key]
            
            st.info(f"📍 الطالب المختار: **{student_obj['name']}** | الصف الحالي: **{student_obj['grade']}** | الفصل الحالي: **{student_obj['section']}**")
            
            col_tr1, col_tr2 = st.columns(2)
            with col_tr1:
                target_grade = st.selectbox("الصف الجديد:", ["الأول المتوسط", "الثاني المتوسط", "الثالث المتوسط"], index=["الأول المتوسط", "الثاني المتوسط", "الثالث المتوسط"].index(student_obj['grade']))
            with col_tr2:
                target_section = st.selectbox("الفصل الجديد:", ["1", "2", "3"], key="tr_sec")
                
            if st.button("🔄 تأكيد نقل الطالب", type="primary"):
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("UPDATE students SET grade = ?, section = ? WHERE student_id = ?", (target_grade, target_section, student_obj['student_id']))
                conn.commit()
                conn.close()
                st.success(f"✅ تم نقل الطالب ({student_obj['name']}) بنجاح إلى {target_grade} فصل {target_section}!")
                st.rerun()

    elif action_type == "❌ حذف طالب من المدرسة":
        st.markdown("### ❌ حذف طالب من قاعدة البيانات")
        
        conn = get_db_connection()
        all_students = conn.execute("SELECT student_id, name, grade, section FROM students ORDER BY name").fetchall()
        conn.close()
        
        student_del_dict = {f"{s['name']} - رقم: {s['student_id']} - ({s['grade']} فصل {s['section']})": s for s in all_students}
        
        if student_del_dict:
            selected_del_key = st.selectbox("اختر الطالب المراد حذفه:", list(student_del_dict.keys()))
            student_del_obj = student_del_dict[selected_del_key]
            
            st.warning(f"⚠️ هل أنت تأكد من رغبتك في حذف الطالب: **{student_del_obj['name']}** (رقم الطالب: {student_del_obj['student_id']})؟")
            
            if st.button("🔴 تأكيد الحذف النهائي", type="primary"):
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("DELETE FROM students WHERE student_id = ?", (student_del_obj['student_id'],))
                conn.commit()
                conn.close()
                st.success(f"✅ تم حذف الطالب ({student_del_obj['name']}) بنجاح من النظام.")
                st.rerun()

# ---------------------------------------------------------
# Page 5: Print Report (طباعة وتصدير التقارير)
# ---------------------------------------------------------
elif page == "🖰 طباعة وتصدير التقارير":
    st.subheader("🖨️ معانية وتصدير تقرير المخالفات والإجراء المتخذ للطباعة")
    
    conn = get_db_connection()
    all_v = conn.execute("SELECT * FROM violations ORDER BY id DESC").fetchall()
    teachers_list = [t['name'] for t in conn.execute("SELECT name FROM teachers").fetchall()]
    vps_list = [v['name'] for v in conn.execute("SELECT name FROM vps").fetchall()]
    conn.close()
    
    if not all_v:
        st.info("لا توجد مخالفات مسجلة للطباعة حالياً.")
    else:
        v_dict = {f"بلاغ #{v['id']} - الطالب: {v['student_name']} - المخالفة: {v['problem_title']} ({v['reported_at']})": v for v in all_v}
        selected_v_key = st.selectbox("اختر المخالفة المراد طباعة التقرير الخاص بها:", list(v_dict.keys()))
        rep = v_dict[selected_v_key]
        
        st.markdown("---")
        st.markdown("### 📝 خيارات الاعتمادات والتوقيعات أسفل التقرير:")
        
        col_sig1, col_sig2, col_sig3 = st.columns(3)
        with col_sig1:
            rep_teacher = st.selectbox("اسم المعلم الموثق:", teachers_list if teachers_list else [rep['teacher_name']], index=teachers_list.index(rep['teacher_name']) if rep['teacher_name'] in teachers_list else 0)
        with col_sig2:
            rep_student = st.text_input("اسم الطالب (للتوقيع):", value=rep['student_name'])
        with col_sig3:
            rep_vp = st.selectbox("وكيل شؤون الطلاب (المعتمد):", vps_list if vps_list else [rep['vp_name'] if rep['vp_name'] else "وكيل شؤون الطلاب"], index=vps_list.index(rep['vp_name']) if rep['vp_name'] in vps_list else 0)
            
        # HTML Printable Report Layout
        report_html = f"""
        <div id="printable-report" style="border: 2px solid #1e3c72; padding: 30px; border-radius: 12px; background-color: #ffffff; color: #000; direction: rtl; font-family: 'Cairo', sans-serif;">
            <!-- Header -->
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                <tr>
                    <td style="text-align: right; width: 33%;">
                        <b>المملكة العربية السعودية</b><br>
                        <b>وزارة التعليم</b><br>
                        الإدارة العامة للتعليم بمنطقة الرياض<br>
                        <b>متوسطة الثغر النموذجية الأهلية - بنين</b>
                    </td>
                    <td style="text-align: center; width: 33%;">
                        <h3 style="margin: 0; color: #1e3c72;">تقرير مخالفة سلوكية وإجراء انضباطي</h3>
                        <p style="margin: 5px 0 0 0; font-size: 12px; font-weight: bold;">العام الدراسي 1447 - 1448 هـ</p>
                    </td>
                    <td style="text-align: left; width: 33%;">
                        <b>رقم البلاغ:</b> #{rep['id']}<br>
                        <b>تاريخ الرصد:</b> {rep['reported_at']}<br>
                        <b>حالة البلاغ:</b> {rep['status']}
                    </td>
                </tr>
            </table>

            <hr style="border: 1px solid #1e3c72; margin-bottom: 20px;">

            <!-- Main Title Banner -->
            <div style="background-color: #f0f4f8; padding: 12px; border-radius: 6px; text-align: center; font-weight: bold; font-size: 16px; color: #1e3c72; border: 1px solid #d0dbe5; margin-bottom: 20px;">
                عنوان البرنامج: تدوين ومعالجة المخالفات السلوكية والانضباط المدرسي والمحافظة على حقوق المتعلم في متوسطة الثغر النموذجية الأهلية
            </div>

            <!-- Student Info Table -->
            <h4 style="color: #1e3c72; margin-bottom: 8px;">أولاً: معلومات الطالب</h4>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;" border="1" cellpadding="8">
                <tr style="background-color: #f8f9fa;">
                    <th style="width: 25%;">اسم الطالب</th>
                    <td style="width: 25%;">{rep['student_name']}</td>
                    <th style="width: 25%;">رقم الطالب / الهوية</th>
                    <td style="width: 25%;">{rep['student_id']}</td>
                </tr>
                <tr>
                    <th>الصف الدراسي</th>
                    <td>{rep['grade']}</td>
                    <th>الفصل</th>
                    <td>فصل {rep['section']}</td>
                </tr>
            </table>

            <!-- Incident Details -->
            <h4 style="color: #1e3c72; margin-bottom: 8px;">ثانياً: تفاصيل المخالفة السلوكية المرصودة</h4>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;" border="1" cellpadding="8">
                <tr style="background-color: #f8f9fa;">
                    <th style="width: 25%;">اسم المعلم الراصد</th>
                    <td style="width: 25%;">{rep['teacher_name']}</td>
                    <th style="width: 25%;">الحصة الدراسية</th>
                    <td style="width: 25%;">{rep['period']}</td>
                </tr>
                <tr>
                    <th>درجة المخالفة</th>
                    <td colspan="3">{rep['violation_degree']}</td>
                </tr>
                <tr>
                    <th>المشكلة السلوكية</th>
                    <td colspan="3"><b>{rep['problem_title']}</b></td>
                </tr>
                <tr>
                    <th>وصف المعلم للواقعة</th>
                    <td colspan="3">{rep['description']}</td>
                </tr>
            </table>

            <!-- VP Decision Details -->
            <h4 style="color: #1e3c72; margin-bottom: 8px;">ثالثاً: الإجراء المتخذ من وكيل شؤون الطلاب/المدرسية</h4>
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;" border="1" cellpadding="8">
                <tr style="background-color: #f8f9fa;">
                    <th style="width: 25%;">الإجراء النظامي المعتمد</th>
                    <td colspan="3" style="color: #155724; font-weight: bold;">{rep['action_taken'] if rep['action_taken'] else 'قيد المعالجة'}</td>
                </tr>
                <tr>
                    <th>ملاحظات وتوجيهات الوكيل</th>
                    <td colspan="3">{rep['vp_notes'] if rep['vp_notes'] else 'لا توجد ملاحظات إضافية'}</td>
                </tr>
                <tr>
                    <th>اسم الوكيل المعالج</th>
                    <td>{rep['vp_name'] if rep['vp_name'] else '---'}</td>
                    <th>تاريخ اتخاذ الإجراء</th>
                    <td>{rep['action_date'] if rep['action_date'] else '---'}</td>
                </tr>
            </table>

            <!-- Signatures Section -->
            <h4 style="color: #1e3c72; margin-bottom: 12px; text-align: center;">الاعتمادات والتوقيعات</h4>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; text-align: center;" border="1" cellpadding="12">
                <tr style="background-color: #f0f4f8;">
                    <td style="width: 33%;"><b>المعلم الراصد</b></td>
                    <td style="width: 33%;"><b>الطالب المخالف</b></td>
                    <td style="width: 33%;"><b>وكيل شؤون الطلاب</b></td>
                </tr>
                <tr>
                    <td><b>الاسم:</b> {rep_teacher}</td>
                    <td><b>الاسم:</b> {rep_student}</td>
                    <td><b>الاسم:</b> {rep_vp}</td>
                </tr>
                <tr style="height: 60px; vertical-align: bottom;">
                    <td>التوقيع: ..........................</td>
                    <td>التوقيع: ..........................</td>
                    <td>التوقيع: ..........................</td>
                </tr>
            </table>
        </div>
        """
        
        st.markdown(report_html, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 لطباعة التقرير بصورة رسمية مباشرة: استخدم أمر الطباعة من المتصفح (Ctrl + P أو Cmd + P) أو زر الطباعة أدناه.")
