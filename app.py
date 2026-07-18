import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

# إعدادات شاشة الجوال الأساسية
st.set_page_config(page_title="مدى نت", page_icon="📶", layout="centered")

# هندسة التصميم بالكامل باستخدام CSS مخصص لجعل الواجهة مبرهة ومرتبة ومكبرة
st.markdown("""
    <style>
    /* دعم اللغة العربية والخطوط */
    body, .stApp { direction: RTL; text-align: right; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f7f9fc; }
    
    /* تصميم الهيدر العلوي */
    .header-container { display: flex; align-items: center; justify-content: flex-start; padding: 10px 0px; margin-bottom: 5px; }
    .header-logo { font-size: 42px; margin-left: 15px; color: #1E3A8A; }
    .header-title { font-size: 32px; font-weight: 900; color: #1E3A8A; margin: 0; line-height: 1.2; }
    
    /* تصميم شريط النقاط والنجمة */
    .nav-bar { display: flex; align-items: center; justify-content: flex-start; gap: 30px; margin-bottom: 25px; padding-right: 5px; }
    .nav-item-dots { font-size: 26px; color: #6B7280; cursor: pointer; font-weight: bold; }
    .nav-item-star { font-size: 24px; color: #F59E0B; cursor: pointer; }
    .nav-text { font-size: 16px; color: #4B5563; font-weight: 500; }
    
    /* تصميم الأيقونات والأقسام الكبيرة في أسطر */
    .grid-button { display: block; width: 100%; padding: 22px 10px; border-radius: 16px; text-align: center; font-weight: bold; font-size: 18px; border: none; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    
    /* تصميم جدول الخلاصة المالية المبهب */
    .finance-table { width: 100%; border-collapse: collapse; margin-top: 20px; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .finance-table th { background-color: #1E3A8A; color: white; padding: 14px; text-align: center; font-size: 16px; }
    .finance-table td { padding: 14px; text-align: center; border-bottom: 1px solid #E5E7EB; font-size: 18px; font-weight: bold; background-color: white; }
    .finance-table tr:nth-child(even) td { background-color: #F9FAFB; }
    .val-cash { color: #10B981; }
    .val-profit { color: #3B82F6; }
    .val-exp { color: #EF4444; }
    
    /* تعديلات عامة لمدخلات بايثون لتناسب التنسيق */
    .stTextInput, .stNumberInput, .stSelectbox { text-align: right; direction: RTL; }
    div.stButton > button { width: 100%; font-size: 18px; font-weight: bold; border-radius: 12px; padding: 10px; }
    </style>
""", unsafe_allow_html=True)

# نظام حماية الدخول للتطبيق بكلمة السر الخاصة بك
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown('<div class="header-container"><div class="header-logo">📶</div><div><h1 class="header-title">شبكة مدى نت</h1></div></div>', unsafe_allow_html=True)
    st.subheader("🔐 تسجيل الدخول للنظام")
    password = st.text_input("أدخل كلمة المرور السرية لشبكة مدى نت:", type="password")
    if st.button("دخول"):
        if password == "m711528241":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ كلمة المرور غير صحيحة!")
    st.stop()

# إنشاء مجلد حفظ فواتير وصور الشبكة
if not os.path.exists("documents"):
    os.makedirs("documents")

# الاتصال بقاعدة البيانات لمدى نت
conn = sqlite3.connect("network_accounting.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS assets (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, item TEXT, cost REAL, paid_me REAL, paid_partner REAL, image_path TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, shop TEXT, card_type TEXT, qty INTEGER, total REAL, comm REAL, net REAL)")
cursor.execute("CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, statement TEXT, amount REAL, image_path TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS partner_tx (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, party TEXT, tx_type TEXT, amount REAL, image_path TEXT)")
conn.commit()

# --- بناء الهيدر العلوي المطور والشعار الفاخر بأقصى اليمين ---
st.markdown("""
<div class="header-container">
    <div class="header-logo">📶</div>
    <div>
        <h1 class="header-title">شبكة مدى نت</h1>
    </div>
</div>
""", unsafe_allow_html=True)

# --- بناء شريط الرموز بمسافات متساوية (الثلاث نقاط ثم النجمة وما يتبعها) ---
st.markdown("""
<div class="nav-bar">
    <div class="nav-item-dots" title="القائمة المتقدمة">⋮</div>
    <div class="nav-item-star" title="المفضلة والروابط السريعة">⭐</div>
    <div class="nav-text">| الحسابات والخرج والاصول مفصلة بدقة</div>
</div>
""", unsafe_allow_html=True)

# إدارة التنقل بين الصفحات عبر أزرار الواجهة المباشرة
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "الرئيسية"

current_date = datetime.now().strftime("%Y-%m-%d %H:%M")

# جلب البيانات لعمل العمليات الرياضية التلقائية في جدول الخلاصة
sales_df = pd.read_sql_query("SELECT * FROM sales", conn)
exp_df = pd.read_sql_query("SELECT * FROM expenses", conn)
tx_df = pd.read_sql_query("SELECT * FROM partner_tx", conn)
assets_df = pd.read_sql_query("SELECT * FROM assets", conn)

total_net_sales = sales_df['net'].sum() if not sales_df.empty else 0.0
total_expenses = exp_df['amount'].sum() if not exp_df.empty else 0.0
my_salaries = tx_df[(tx_df['party'] == "أنا") & (tx_df['tx_type'] == "راتب مستحق")]['amount'].sum() if not tx_df.empty else 0.0

net_profit_distributable = total_net_sales - total_expenses - my_salaries
partner_share = net_profit_distributable / 2 if net_profit_distributable > 0 else 0.0

my_drawings = tx_df[(tx_df['party'] == "أنا") & (tx_df['tx_type'] == "سحب أرباح شخصية")]['amount'].sum() if not tx_df.empty else 0.0
partner_drawings = tx_df[(tx_df['party'] == "الشريك") & (tx_df['tx_type'] == "تحويل مالي للشريك")]['amount'].sum() if not tx_df.empty else 0.0

total_assets_paid = assets_df['paid_me'].sum() + assets_df['paid_partner'].sum() if not assets_df.empty else 0.0
total_assets_cost = assets_df['cost'].sum() if not assets_df.empty else 0.0
current_cash_box = (total_net_sales + total_assets_paid) - (total_expenses + total_assets_cost + my_drawings + partner_drawings)

# العودة للصفحة الرئيسية إذا لم نكن فيها
if st.session_state["current_page"] != "الرئيسية":
    if st.button("⬅️ العودة للوحة واجهة مدى نت الرئيسية"):
        st.session_state["current_page"] = "الرئيسية"
        st.rerun()

# ------------------- عرض الواجهة الرئيسية المطورة -------------------
if st.session_state["current_page"] == "الرئيسية":
    
    # 📌 السطر الأول من الأيقونات: لوحة التحكم وبجانبها أصول مدى نت والتأسيس
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 لوحة التحكم والتقارير"):
            st.session_state["current_page"] = "التقارير"
            st.rerun()
    with col2:
        if st.button("📦 أصول مدى نت والتأسيس"):
            st.session_state["current_page"] = "الأصول"
            st.rerun()
            
    # 📌 السطر الثاني من الأيقونات: المبيعات اليومية وبجانبها المصاريف والخرج
    col3, col4 = st.columns(2)
    with col3:
        if st.button("💰 المبيعات اليومية - الكروت"):
            st.session_state["current_page"] = "المبيعات"
            st.rerun()
    with col4:
        if st.button("📉 المصاريف والخرج"):
            st.session_state["current_page"] = "المصاريف"
            st.rerun()
            
    # 📌 السطر الثالث من الأيقونات: حركات الشركاء والرواتب لتوثيق كل الأقسام
    col5, col6 = st.columns(2)
    with col5:
        if st.button("👤 حركات الشركاء والرواتب"):
            st.session_state["current_page"] = "الشركاء"
            st.rerun()
    with col6:
        st.write("") # حقل متوازن لملء واجهة السطر تماماً

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 الخلاصة والتقرير المالي الفوري")
    
    # --- عرض الحسابات على شكل جدول مرتب وجميل وأنيق ومبهر ---
    st.markdown(f"""
    <table class="finance-table">
        <tr>
            <th>البيان المالي للشبكة</th>
            <th>المبلغ الحالي الصافي</th>
        </tr>
        <tr>
            <td>💵 السيولة الحالية بالصندوق</td>
            <td class="val-cash">{current_cash_box:,.2f}</td>
        </tr>
        <tr>
            <td>📈 صافي الأرباح المشتركة</td>
            <td class="val-profit">{net_profit_distributable:,.2f}</td>
        </tr>
        <tr>
            <td>🛠️ إجمالي المصاريف والخرج</td>
            <td class="val-exp">{total_expenses:,.2f}</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

# ----------------- تفاصيل الأقسام عند الضغط عليها -----------------
elif st.session_state["current_page"] == "التقارير":
    st.title("📊 تفاصيل التقارير ووضع الشركاء")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"**حسابي الشخصي:**")
        st.write(f"• مستحقات الرواتب لادارتي: {my_salaries:,.2f}")
        st.write(f"• حصتي من الأرباح (50%): {partner_share:,.2f}")
        st.write(f"• ما تم سحبه فعلياً: {my_drawings:,.2f}")
        st.info(f"الرصيد المتبقي لي: {(my_salaries + partner_share) - my_drawings:,.2f}")
    with col4:
        st.markdown(f"**حساب الشريك المغترب:**")
        st.write(f"• حصته من الأرباح (50%): {partner_share:,.2f}")
        st.write(f"• ما تم تحويله له: {partner_drawings:,.2f}")
        st.info(f"الرصيد المتبقي للشريك: {partner_share - partner_drawings:,.2f}")

elif st.session_state["current_page"] == "الأصول":
    st.title("📦 تسجيل أصول مدى نت")
    with st.form("assets_form", clear_on_submit=True):
        item = st.text_input("اسم الجهاز أو البند (مثل: ستارلينك / أتعاب تركيب):")
        cost = st.number_input("التكلفة الإجمالية للبند:", min_value=0.0)
        paid_me = st.number_input("المبلغ المدفوع منك أنت:")
        paid_partner = st.number_input("المبلغ المدفوع من الشريك:")
        file = st.file_uploader("التقط أو ارفع صورة الفاتورة/السند:", type=['jpg', 'jpeg', 'png'])
        if st.form_submit_button("تسجيل الأصل والعودة"):
