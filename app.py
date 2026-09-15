import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="برنامج تدوين ومعالجة المخالفات السلوكية",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"], div, span, label {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 22px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .main-header h1 {
        font-size: 22px;
        font-weight: 800;
        margin: 0 0 10px 0;
        color: #ffffff;
    }
    .main-header h2 {
        font-size: 16px;
        font-weight: 600;
        margin: 0 0 8px 0;
        color: #e0e8f5;
    }
    .main-header p.developer-credit {
        font-size: 14px;
        font-weight: 700;
        margin: 8px 0 0 0;
        color: #ffd700;
    }
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e1e8ed;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .stButton>button {
        background-color: #2a5298;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 8px 24px;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1e3c72;
        color: white;
    }
    .print-report {
        background-color: #fff;
        border: 2px solid #1e3c72;
        padding: 30px;
        border-radius: 10px;
        color: #000;
        font-family: 'Cairo', sans-serif;
    }
    .signature-box {
        border-top: 1px dashed #777;
        margin-top: 40px;
        padding-top: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Database Connection Helper
DB_PATH = '/workspace/scratch/school_discipline.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def fetch_teachers():
    conn = get_connection()
    df = pd.read_sql_query("SELECT name FROM teachers ORDER BY name", conn)
    conn.close()
    return df['name'].tolist()

def fetch_students(grade=None, section=None):
    conn = get_connection()
    query = "SELECT id, name, grade, section FROM students WHERE 1=1"
    params = []
    if grade:
        query += " AND grade = ?"
        params.append(grade)
    if section:
        query += " AND section = ?"
        params.append(section)
    query += " ORDER BY name"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Initialize Session State
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Code of Conduct Violation Degrees Data according to Saudi Ministry of Education Discipline Rules
VIOLATION_RULES = {
    "الدرجة الأولى (المخالفات البسيطة)": [
        "عدم الالتزام بالزي المدرسي أو المظهر العام",
        "التأخر عن الحضور لصلاة الجماعة أو الدخول للحصة",
        "النوم داخل الفصل أو أثناء النشاط المدرسي",
        "استخدام الهاتف المحمول دون إذن داخل الصف",
        "تناول الأطعمة أو المشروبات داخل الفصل أثناء الشرح"
    ],
    "الدرجة الثانية (المخالفات متوسطة الشدة)": [
        "الهروب من الفصل أو عدم حضور بعض الحصص",
        "الشجار اللفظي أو التنابز بالألقاب مع الزملاء",
        "إثارة الفوضى داخل الصف أو في ساحات المدرسة",
        "إلحاق الضرر الخفيف بممتلكات المدرسة أو الزملاء",
        "إحضار الأجهزة الإلكترونية والشاشات غير المصرح بها"
    ],
    "الدرجة الثالثة (المخالفات الخطيرة)": [
        "التغيب عن المدرسة بدون عذر مقبول لأيام متتالية",
        "التلفظ بألفاظ غير لائمة أو الخروج عن الأدب مع المعلم/الكادر",
        "الاعتداء الجسدي الخفيف أو المشاجرة مع زميل",
        "إلحاق تلفيات متعمدة بالأجهزة والممتلكات المدرسية",
        "التوقيع عن ولي الأمر أو تزوير الإشعارات المدرسية"
    ],
    "الدرجة الرابعة (المخالفات شديدة الخطورة)": [
        "الاعتداء الجسدي الصريح على أحد الزملاء أو إلحاق أذى جسدي",
        "التنمر والتعدي السلوكي الممنهج على الطلاب",
        "سرقة ممتلكات المدرسة أو المعلمين أو الزملاء",
        "إحضار السجائر/السجائر الإلكترونية أو تدخينها داخل المدرسة",
        "مغادرة المدرسة والهروب من السور أثناء اليوم الدراسي"
    ],
    "الدرجة الخامسة والسادسة (المخالفات بالغ الخطورة)": [
        "إحضار أدوات حادة أو خطرة إلى مقر المدرسة",
        "الاعتداء بالقول أو الفعل على أحد من الكادر التعليمي أو الإداري",
        "التعمد الشديد في إتلاف وتخريب التجهيزات والمنشآت المدرسية",
        "الجرائم الإلكترونية كالابتزاز أو التصوير بدون إذن داخل المدرسة"
    ]
}

PROCEDURES_BY_DEGREE = {
    "الدرجة الأولى (المخالفات البسيطة)": [
        "التنبيه الشفهي الأول وإشعار الطالب بمخالفته",
        "التنبيه الشفهي الثاني مع كتابة تعهد خطي على الطالب",
        "إشعار ولي الأمر هاتفياً بالواقعة وتوثيق ذلك",
        "خصم درجة واحدة من درجات السلوك والمواظبة"
    ],
    "الدرجة الثانية (المخالفات متوسطة الشدة)": [
        "أخذ تعهد خطي على الطالب بالتزام السلوك الحسني",
        "استدعاء ولي أمر الطالب وتوقيعه على بالعلم بالإجراء",
        "تحويل الطالب للموجه الطلابي لدراسة حالته السلوكية",
        "خصم درجتين من درجات السلوك وتأدية خدمات مدرسة إيجابية"
    ],
    "الدرجة الثالثة (المخالفات الخطيرة)": [
        "استدعاء فوري لولي الأمر وأخذ تعهد خطي مشدد",
        "إحالة الطالب المباشرة للموجه الطلابي لوضع برنامج تعديل سلوك",
        "نقل الطالب إلى فصل آخر داخل المدرسة",
        "خصم (3) درجات من درجات السلوك وإشعار ولي الأمر رسمياً"
    ],
    "الدرجة الرابعة (المخالفات شديدة الخطورة)": [
        "انعقاد لجنة التوجيه والطلاب بالمدرسة لاتخاذ القرار",
        "خصم (5) درجات من درجات السلوك",
        "إيقاف الطالب عن الدراسة لمدة لا تتجاوز 3 أيام مع إشعار ولي الأمر",
        "تحويل الطالب إلى مركز التوجيه والإرشاد بالإدارة التعليمية"
    ],
    "الدرجة الخامسة والسادسة (المخالفات بالغ الخطورة)": [
        "الرفع الفوري لإدارة التعليم بالمنطقة لاتخاذ الإجراء النظامي الشامل",
        "خصم (10) درجات من مادة السلوك",
        "نقل الطالب إلى مدرسة أخرى أو الحرمان من الدراسة وفق القواعد"
    ]
}

# App Header
st.markdown("""
<div class="main-header">
    <h1>تدوين ومعالجة المخالفات السلوكية والانضباط المدرسي والمحافظة على حقوق المتعلم</h1>
    <h2>متوسطة الثغر النموذجية الأهلية - بنين</h2>
    <p class="developer-credit">✨ تصميم وتطوير: أ. محمد سامي السعيد ✨</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("📌 القائمة الرئيسية")
page = st.sidebar.radio(
    "اختر الشاشة المطلوب الانتقال إليها:",
    ["👨‍🏫 شاشة المعلم (رصد مخالفة)", "👨‍💼 شاشة وكيل الشؤون المدرسية", "🔍 البحث الشامل عن طالب", "⚙️ إدارة بيانات الطلاب", "🖨️ طباعة وتصدير التقرير"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align: center; background-color: #f0f4f9; padding: 10px; border-radius: 8px; border: 1px solid #d0d7de;">
    <p style="margin: 0; font-size: 13px; color: #333; font-weight: bold;">💻 تصميم وتطوير البرمجية:</p>
    <p style="margin: 3px 0 0 0; font-size: 15px; color: #1e3c72; font-weight: 800;">محمد سامي السعيد</p>
</div>
""", unsafe_allow_html=True)

# Login handling for Vice Principal & Admin Screens
if page in ["👨‍💼 شاشة وكيل الشؤون المدرسية", "⚙️ إدارة بيانات الطلاب"]:
    if not st.session_state.authenticated:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔒 تسجيل دخول وكيل المدرسة")
        password_input = st.sidebar.text_input("رمز الدخول / كلمة المرور:", type="password", key="pwd_input")
        if st.sidebar.button("تسجيل الدخول"):
            if password_input == "9009":
                st.session_state.authenticated = True
                st.sidebar.success("تم تسجيل الدخول بنجاح!")
                st.rerun()
            else:
                st.sidebar.error("كلمة المرور غير صحيحة! (الرمز الصحيح هو 9009)")

# PAGE 1: Teacher Screen
if page == "👨‍🏫 شاشة المعلم (رصد مخالفة)":
    st.subheader("📋 شاشة المعلم - رصد المخالفة السلوكية")
    
    teachers_list = fetch_teachers()
    
    with st.form("incident_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            selected_teacher = st.selectbox("اختر اسم المعلم الراصد:", teachers_list)
            selected_grade = st.selectbox("اختر الصف الدراسي:", ["الصف الأول المتوسط", "الصف الثاني المتوسط", "الصف الثالث المتوسط"])
            selected_section = st.selectbox("اختر الفصل (الشعبة):", ["فصل 1", "فصل 2", "فصل 3"])
            selected_period = st.selectbox("اختر الحصة الدراسية:", [f"الحصة {i}" for i in range(1, 8)])
        
        with col2:
            students_df = fetch_students(selected_grade, selected_section)
            student_options = [f"{row['name']} ({row['id']})" for _, row in students_df.iterrows()]
            
            if student_options:
                selected_student_str = st.selectbox("اختر اسم الطالب المخالف:", student_options)
            else:
                st.warning("لا يوجد طلاب مسجلون في هذا الصف والفصل.")
                selected_student_str = None
                
            selected_degree = st.selectbox("درجة المشكلة السلوكية:", list(VIOLATION_RULES.keys()))
            selected_violation = st.selectbox("المشكلة السلوكية:", VIOLATION_RULES[selected_degree])
            
        description = st.text_area("وصف المشكلة التفصيلي (تدوين واقعة المخالفة):", placeholder="يكتب المعلم هنا وصفاً دقيقاً ومفصلاً لما حدث أثناء الحصة...")
        
        submitted = st.form_submit_button("📤 إرسال البلاغ لوكيل الشؤون المدرسية")
        
        if submitted:
            if not selected_student_str:
                st.error("يرجى اختيار الطالب قبل إرسال البلاغ.")
            elif not description.strip():
                st.error("يرجى تدوين وصف المشكلة السلوكية.")
            else:
                # Extract Student ID and Name
                student_name = selected_student_str.split(" (")[0]
                student_id = selected_student_str.split("(")[1].replace(")", "")
                
                conn = get_connection()
                c = conn.cursor()
                c.execute('''
                INSERT INTO incidents 
                (teacher_name, student_id, student_name, grade, section, period, incident_degree, incident_type, description, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (selected_teacher, student_id, student_name, selected_grade, selected_section, selected_period, selected_degree, selected_violation, description, 'معلقة (بانتظار الإجراء)'))
                conn.commit()
                conn.close()
                st.success("✅ تم إرسال البلاغ بنجاح وتوثيقه في قاعدة البيانات لوكيل الشؤون المدرسية!")

# PAGE 2: Vice Principal Screen
elif page == "👨‍💼 شاشة وكيل الشؤون المدرسية":
    if not st.session_state.authenticated:
        st.warning("🔒 هذه الشاشة محمية بكلمة مرور. يرجى إدخال كلمة المرور (9009) في الشريط الجانبي لتسجيل الدخول.")
    else:
        st.subheader("👨‍💼 شاشة وكيل الشؤون المدرسية - معالجة البلاغات واتخاذ الإجراءات")
        
        conn = get_connection()
        incidents_df = pd.read_sql_query("SELECT * FROM incidents ORDER BY id DESC", conn)
        conn.close()
        
        if incidents_df.empty:
            st.info("لا توجد مخالفات سلوكية مرصودة حالياً.")
        else:
            pending_df = incidents_df[incidents_df['status'] == 'معلقة (بانتظار الإجراء)']
            processed_df = incidents_df[incidents_df['status'] != 'معلقة (بانتظار الإجراء)']
            
            tab1, tab2 = st.tabs([f"📥 البلاغات الواردة الجديدة ({len(pending_df)})", f"✅ البلاغات المعالجة والمكتملة ({len(processed_df)})"])
            
            with tab1:
                if pending_df.empty:
                    st.success("لا توجد بلاغات معلقة جديدة.")
                else:
                    for _, row in pending_df.iterrows():
                        with st.expander(f"🚨 بلاغ رقم #{row['id']} - الطالب: {row['student_name']} ({row['grade']} - {row['section']})"):
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.write(f"**المعلم الراصد:** {row['teacher_name']}")
                                st.write(f"**الصف والفصل:** {row['grade']} - {row['section']}")
                                st.write(f"**الحصة:** {row['period']}")
                                st.write(f"**تاريخ الرصد:** {row['created_at']}")
                            with col_b:
                                st.write(f"**درجة المخالفة:** {row['incident_degree']}")
                                st.write(f"**نوع المخالفة:** {row['incident_type']}")
                                st.write(f"**وصف المعلم للمشكلة:** {row['description']}")
                            
                            st.markdown("---")
                            st.subheader("⚖️ اتخاذ الإجراء النظامي بحسب قواعد السلوك والمواظبة:")
                            
                            deg = row['incident_degree']
                            procedures_list = PROCEDURES_BY_DEGREE.get(deg, ["تنبيه شفهي", "تعهد خطي", "إشعار ولي الأمر"])
                            
                            with st.form(f"process_form_{row['id']}"):
                                selected_proc = st.selectbox("اختر الإجراء المطلوب اتخاذه:", procedures_list, key=f"proc_{row['id']}")
                                vice_notes = st.text_area("تدوين ملاحظات وتوجيهات الوكيل:", placeholder="يكتب الوكيل هنا توجيهاته وملاحظاته الخصوصية...", key=f"notes_{row['id']}")
                                
                                btn_proc = st.form_submit_button("حفظ وتأكيد الإجراء")
                                if btn_proc:
                                    conn = get_connection()
                                    c = conn.cursor()
                                    c.execute('''
                                    UPDATE incidents 
                                    SET action_taken = ?, vice_notes = ?, status = 'تم اتخاذ الإجراء', updated_at = CURRENT_TIMESTAMP
                                    WHERE id = ?
                                    ''', (selected_proc, vice_notes, row['id']))
                                    conn.commit()
                                    conn.close()
                                    st.success("تم اعتماد الإجراء بنجاح وتحديث حالة التقرير!")
                                    st.rerun()

            with tab2:
                if processed_df.empty:
                    st.info("لا توجد بلاغات معالجة حتى الآن.")
                else:
                    for _, row in processed_df.iterrows():
                        with st.expander(f"✅ بلاغ رقم #{row['id']} - الطالب: {row['student_name']} (تم اتخاذ الإجراء)"):
                            st.write(f"**المعلم الراصد:** {row['teacher_name']} | **الحصة:** {row['period']}")
                            st.write(f"**المخالفة:** {row['incident_degree']} - {row['incident_type']}")
                            st.write(f"**الإجراء المتخذ:** {row['action_taken']}")
                            st.write(f"**ملاحظات الوكيل:** {row['vice_notes']}")

# PAGE 3: Student Search
elif page == "🔍 البحث الشامل عن طالب":
    st.subheader("🔍 البحث الشامل عن سجل طالب سلوكي")
    
    search_query = st.text_input("أدخل اسم الطالب أو رقم هويته للبحث في القاعدة:")
    
    if search_query.strip():
        conn = get_connection()
        st_df = pd.read_sql_query(
            "SELECT * FROM students WHERE name LIKE ? OR id LIKE ?",
            conn, params=[f"%{search_query}%", f"%{search_query}%"]
        )
        
        if st_df.empty:
            st.warning("لم يتم العثور على طالب مطابق لكلمة البحث.")
        else:
            for _, student in st_df.iterrows():
                st.markdown(f"### 👤 الطالب: {student['name']} (رقم الهوية/الطالب: `{student['id']}`)")
                st.write(f"**الصف:** {student['grade']} | **الفصل:** {student['section']}")
                
                inc_df = pd.read_sql_query(
                    "SELECT * FROM incidents WHERE student_id = ? ORDER BY id DESC",
                    conn, params=[student['id']]
                )
                
                if inc_df.empty:
                    st.success("✨ هذا الطالب ليس لديه أي مخالفات سلوكية مرصودة في السجل.")
                else:
                    st.error(f"⚠️ يوجد عدد ({len(inc_df)}) مخالفة سلوكية مرصودة بحق الطالب:")
                    st.dataframe(inc_df[['id', 'teacher_name', 'period', 'incident_degree', 'incident_type', 'action_taken', 'status', 'created_at']], use_container_width=True)
        conn.close()

# PAGE 4: Student Management (Add, Delete, Transfer)
elif page == "⚙️ إدارة بيانات الطلاب":
    if not st.session_state.authenticated:
        st.warning("🔒 هذه الشاشة محمية بكلمة مرور. يرجى إدخال كلمة المرور (9009) في الشريط الجانبي لتسجيل الدخول.")
    else:
        st.subheader("⚙️ إدارة الطلاب (إضافة - حذف - نقل)")
        
        m_tab1, m_tab2, m_tab3 = st.tabs(["➕ إضافة طالب جديد", "❌ حذف طالب", "🔄 نقل طالب من فصل لآخر"])
        
        with m_tab1:
            st.markdown("#### إضافة طالب جديد لقاعدة البيانات")
            with st.form("add_student_form", clear_on_submit=True):
                new_id = st.text_input("رقم الهوية / رقم الطالب (فريد):")
                new_name = st.text_input("اسم الطالب الرباعي:")
                new_grade = st.selectbox("الصف الدراسي:", ["الصف الأول المتوسط", "الصف الثاني المتوسط", "الصف الثالث المتوسط"], key="add_g")
                new_section = st.selectbox("الفصل (الشعبة):", ["فصل 1", "فصل 2", "فصل 3"], key="add_s")
                
                btn_add = st.form_submit_button("حفظ الطالب الجديد")
                if btn_add:
                    if not new_id.strip() or not new_name.strip():
                        st.error("يرجى ملء جميع الحقول المطلوب إدخالها.")
                    else:
                        conn = get_connection()
                        c = conn.cursor()
                        try:
                            c.execute("INSERT INTO students (id, name, grade, section) VALUES (?, ?, ?, ?)", (new_id.strip(), new_name.strip(), new_grade, new_section))
                            conn.commit()
                            st.success(f"تمت إضافة الطالب ({new_name}) بنجاح!")
                        except sqlite3.IntegrityError:
                            st.error("رقم الطالب/الهوية هذا موجود مسبقاً في قاعدة البيانات!")
                        conn.close()
                        
        with m_tab2:
            st.markdown("#### حذف طالب من قاعدة البيانات")
            all_st = fetch_students()
            st_list = [f"{r['name']} ({r['id']})" for _, r in all_st.iterrows()]
            
            selected_del = st.selectbox("اختر الطالب المراد حذفه:", st_list, key="del_st")
            if st.button("🔴 حذف الطالب نهائياً"):
                del_id = selected_del.split("(")[1].replace(")", "")
                del_name = selected_del.split(" (")[0]
                conn = get_connection()
                c = conn.cursor()
                c.execute("DELETE FROM students WHERE id = ?", (del_id,))
                conn.commit()
                conn.close()
                st.success(f"تم حذف الطالب ({del_name}) نهائياً من قاعدة البيانات!")
                st.rerun()

        with m_tab3:
            st.markdown("#### نقل طالب من فصل إلى فصل آخر")
            all_st = fetch_students()
            st_list_tr = [f"{r['name']} ({r['id']}) - حالياً: {r['grade']} ({r['section']})" for _, r in all_st.iterrows()]
            
            selected_tr = st.selectbox("اختر الطالب المراد نقله:", st_list_tr, key="tr_st")
            target_grade = st.selectbox("الصف الدراسي الجديد:", ["الصف الأول المتوسط", "الصف الثاني المتوسط", "الصف الثالث المتوسط"], key="tr_g")
            target_section = st.selectbox("الفصل الجديد:", ["فصل 1", "فصل 2", "فصل 3"], key="tr_s")
            
            if st.button("🔄 نقل الطالب للفصل الجديد"):
                tr_id = selected_tr.split("(")[1].split(")")[0]
                tr_name = selected_tr.split(" (")[0]
                conn = get_connection()
                c = conn.cursor()
                c.execute("UPDATE students SET grade = ?, section = ? WHERE id = ?", (target_grade, target_section, tr_id))
                conn.commit()
                conn.close()
                st.success(f"تم نقل الطالب ({tr_name}) إلى ({target_grade} - {target_section}) بنجاح!")
                st.rerun()

# PAGE 5: Printing & Exporting Reports
elif page == "🖨️ طباعة وتصدير التقرير":
    st.subheader("🖨️ طباعة التقرير الرسمي للمخالفة السلوكية")
    
    conn = get_connection()
    inc_df = pd.read_sql_query("SELECT * FROM incidents ORDER BY id DESC", conn)
    conn.close()
    
    if inc_df.empty:
        st.info("لا توجد تقارير مخالفات مسجلة للطباعة.")
    else:
        report_options = [f"تقرير #{r['id']} - الطالب: {r['student_name']} - تاريخ: {r['created_at']}" for _, r in inc_df.iterrows()]
        selected_rep = st.selectbox("اختر التقرير المراد معاينته وطباعته:", report_options)
        
        selected_id = int(selected_rep.split("#")[1].split(" -")[0])
        conn = get_connection()
        rep_data = pd.read_sql_query("SELECT * FROM incidents WHERE id = ?", conn, params=[selected_id]).iloc[0]
        conn.close()
        
        st.markdown("---")
        
        # Display Official Report Layout
        st.markdown(f"""
        <div class="print-report">
            <div style="text-align: center; border-bottom: 2px solid #1e3c72; padding-bottom: 15px; margin-bottom: 20px;">
                <h3 style="margin:0; color:#1e3c72; font-size: 20px;">المملكة العربية السعودية - وزارة التعليم</h3>
                <h4 style="margin:5px 0; color:#333;">الإدارة العامة للتعليم بمنطقة الرياض</h4>
                <h4 style="margin:5px 0; color:#333;">متوسطة الثغر النموذجية الأهلية - بنين</h4>
                <hr style="border: 1px solid #1e3c72; margin: 15px 0;">
                <h2 style="color:#1e3c72; font-size: 20px; font-weight: 800; margin:10px 0;">
                    تقرير تدوين ومعالجة المخالفات السلوكية والانضباط المدرسي والمحافظة على حقوق المتعلم
                </h2>
            </div>
            
            <table style="width:100%; border-collapse: collapse; margin-bottom: 20px; font-size: 15px;" border="1" cellpadding="8">
                <tr style="background-color: #f2f5f9;">
                    <th style="width: 20%;">رقم التقرير:</th>
                    <td style="width: 30%;">{rep_data['id']}</td>
                    <th style="width: 20%;">تاريخ الرصد:</th>
                    <td style="width: 30%;">{rep_data['created_at']}</td>
                </tr>
                <tr>
                    <th>اسم الطالب:</th>
                    <td><b>{rep_data['student_name']}</b></td>
                    <th>رقم الطالب / الهوية:</th>
                    <td>{rep_data['student_id']}</td>
                </tr>
                <tr style="background-color: #f2f5f9;">
                    <th>الصف الدراسي:</th>
                    <td>{rep_data['grade']}</td>
                    <th>الفصل (الشعبة):</th>
                    <td>{rep_data['section']}</td>
                </tr>
                <tr>
                    <th>المعلم الراصد:</th>
                    <td>{rep_data['teacher_name']}</td>
                    <th>الحصة الدراسية:</th>
                    <td>{rep_data['period']}</td>
                </tr>
                <tr style="background-color: #f2f5f9;">
                    <th>درجة المشكلة:</th>
                    <td colspan="3"><b style="color: #c0392b;">{rep_data['incident_degree']}</b></td>
                </tr>
                <tr>
                    <th>المشكلة السلوكية:</th>
                    <td colspan="3">{rep_data['incident_type']}</td>
                </tr>
                <tr style="background-color: #f2f5f9;">
                    <th>وصف المعلم للمشكلة:</th>
                    <td colspan="3">{rep_data['description']}</td>
                </tr>
                <tr>
                    <th>الإجراء المتخذ (الوكيل):</th>
                    <td colspan="3"><b style="color: #27ae60;">{rep_data['action_taken'] if rep_data['action_taken'] else 'قيد المعالجة'}</b></td>
                </tr>
                <tr style="background-color: #f2f5f9;">
                    <th>ملاحظات الوكيل:</th>
                    <td colspan="3">{rep_data['vice_notes'] if rep_data['vice_notes'] else 'لا توجد ملاحظات إضافية'}</td>
                </tr>
            </table>
            
            <div style="margin-top: 30px; border: 1px solid #ddd; padding: 15px; border-radius: 8px; background-color: #fafafa;">
                <h4 style="margin-top:0; color:#1e3c72; text-align: center;">الاعتمادات والتوقيعات الرسمية</h4>
                <div style="display: flex; justify-content: space-between; text-align: center; margin-top: 25px;">
                    <div style="width: 23%;">
                        <p style="font-weight: bold; margin-bottom: 5px;">المعلم الراصد</p>
                        <p style="margin: 0; color: #555;">{rep_data['teacher_name']}</p>
                        <p style="margin-top: 35px; border-top: 1px solid #999; padding-top: 5px;">التوقيع: .....................</p>
                    </div>
                    <div style="width: 23%;">
                        <p style="font-weight: bold; margin-bottom: 5px;">الطالب المخالف</p>
                        <p style="margin: 0; color: #555;">{rep_data['student_name']}</p>
                        <p style="margin-top: 35px; border-top: 1px solid #999; padding-top: 5px;">التوقيع: .....................</p>
                    </div>
                    <div style="width: 25%;">
                        <p style="font-weight: bold; margin-bottom: 5px;">وكيل شؤون الطلاب</p>
                        <p style="margin: 0; color: #555;">صالح بن عبدالله الدعجاني</p>
                        <p style="margin-top: 35px; border-top: 1px solid #999; padding-top: 5px;">التوقيع: .....................</p>
                    </div>
                    <div style="width: 25%;">
                        <p style="font-weight: bold; margin-bottom: 5px;">مدير المدرسة</p>
                        <p style="margin: 0; color: #555;">إبراهيم بن موسى التميمي</p>
                        <p style="margin-top: 35px; border-top: 1px solid #999; padding-top: 5px;">التوقيع: .....................</p>
                    </div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 25px; padding-top: 12px; border-top: 1px dashed #bbb; font-size: 13px; color: #555;">
                <b>إعداد وتصميم البرمجية:</b> المعلم / محمد سامي السعيد
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 لطباعة التقرير أعلاه بصيغة ورقية أو حفظه كملف PDF، يرجى الضغط على زر (Ctrl + P) في لوحة المفاتيح واختيار الحفظ كـ PDF.")
