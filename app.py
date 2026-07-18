import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

# إعدادات شاشة الجوال (تم تعديل الاسم والرمز الافتراضي للشبكة 📶)
st.set_page_config(page_title="مدى نت", page_icon="📶", layout="centered")

# إجبار الواجهة على دعم الاتجاه العربي (من اليمين إلى اليسار)
st.markdown("""
    <style>
    body { direction: RTL; text-align: right; }
    div.stButton > button { width: 100%; font-size: 18px; font-weight: bold; background-color: #4CAF50; color: white; }
    .stTextInput, .stNumberInput, .stSelectbox { text-align: right; direction: RTL; }
    </style>
""", unsafe_allow_html=True)

# نظام حماية الدخول للتطبيق
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 تسجيل الدخول - مدى نت")
    password = st.text_input("أدخل كلمة المرور السرية لشبكة مدى نت:", type="password")
    if st.button("دخول"):
        # تم تعديل كلمة السر بنجاح إلى m711528241
        if password == "m711528241":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ كلمة المرور غير صحيحة!")
    st.stop()

# إنشاء المجلدات الخاصة بحفظ صور الفواتير والسندات لاحقاً
if not os.path.exists("documents"):
    os.makedirs("documents")

# الاتصال بقاعدة البيانات وإنشاء الجداول فارغة
conn = sqlite3.connect("network_accounting.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, item TEXT, cost REAL, paid_me REAL, paid_partner REAL, image_path TEXT
)""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, shop TEXT, card_type TEXT, qty INTEGER, total REAL, comm REAL, net REAL
)""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, type TEXT, statement TEXT, amount REAL, image_path TEXT
)""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS partner_tx (
    id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, party TEXT, tx_type TEXT, amount REAL, image_path TEXT
)""")
conn.commit()

# القائمة الجانبية للتنقل بين الأقسام بداخل التطبيق
menu = ["📊 لوحة التحكم والتقارير", "📦 أصول مدى نت والتأسيس", "💰 المبيعات اليومية (الكروت)", "📉 المصاريف والخرج", "👤 حركات الشركاء والرواتب"]
choice = st.sidebar.radio("انتقل إلى القسم:", menu)

current_date = datetime.now().strftime("%Y-%m-%d %H:%M")

# ----------------- 1. لوحة التحكم والتقارير -----------------
if choice == "📊 لوحة التحكم والتقارير":
    st.title("📊 لوحة التحكم المالية لشبكة مدى نت")
    
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

    col1, col2 = st.columns(2)
    with col1:
        st.metric("💵 السيولة الحالية بالصندوق", f"{current_cash_box:,.2f}")
        st.metric("📈 صافي الأرباح المشتركة", f"{net_profit_distributable:,.2f}")
    with col2:
        st.metric("🛒 إجمالي دخل الكروت الصافي", f"{total_net_sales:,.2f}")
        st.metric("🛠️ إجمالي المصاريف والخرج", f"{total_expenses:,.2f}")
        
    st.divider()
    st.subheader("👤 الوضع المالي الحالي لكل شريك")
    
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"**حسابي الشخصي:**")
        st.write(f"• مستحقات الرواتب: {my_salaries:,.2f}")
        st.write(f"• حصتي من الأرباح (50%): {partner_share:,.2f}")
        st.write(f"• ما تم سحبه فعلياً: {my_drawings:,.2f}")
        my_net_status = (my_salaries + partner_share) - my_drawings
        st.info(f"الرصيد المتبقي لي: {my_net_status:,.2f}")
        
    with col4:
        st.markdown(f"**حساب الشريك المغترب:**")
        st.write(f"• حصته من الأرباح (50%): {partner_share:,.2f}")
        st.write(f"• ما تم تحويله له فعلياً: {partner_drawings:,.2f}")
        partner_net_status = partner_share - partner_drawings
        st.info(f"الرصيد المتبقي للشريك: {partner_net_status:,.2f}")

# ----------------- 2. أصول مدى نت والتأسيس -----------------
elif choice == "📦 أصول مدى نت والتأسيس":
    st.title("📦 رأس مال وأصول شبكة مدى نت")
    with st.form("assets_form", clear_on_submit=True):
        item = st.text_input("اسم الجهاز أو البند (مثل: ستارلينك / أتعاب تركيب):")
        cost = st.number_input("التكلفة الإجمالية للبند:", min_value=0.0)
        paid_me = st.number_input("المبلغ المدفوع منك أنت:")
        paid_partner = st.number_input("المبلغ المدفوع من الشريك:")
        file = st.file_uploader("التقط أو ارفع صورة الفاتورة/السند:", type=['jpg', 'jpeg', 'png'])
        
        if st.form_submit_button("تسجيل أصل جديد"):
            img_path = ""
            if file is not None:
                img_path = f"documents/asset_{int(datetime.now().timestamp())}.png"
                with open(img_path, "wb") as f:
                    f.write(file.getbuffer())
            cursor.execute("INSERT INTO assets (date, item, cost, paid_me, paid_partner, image_path) VALUES (?, ?, ?, ?, ?, ?)", 
                           (current_date, item, cost, paid_me, paid_partner, img_path))
            conn.commit()
            st.success("تم تسجيل بيانات التأسيس بنجاح لشبكة مدى نت!")
            
    df = pd.read_sql_query("SELECT id, date as التاريخ, item as البند, cost as التكلفة, paid_me as المدفوع_مني, paid_partner as المدفوع_من_الشريك, image_path FROM assets", conn)
    if not df.empty:
        st.dataframe(df.drop(columns=['image_path']), use_container_width=True)
        show_img = st.selectbox("اختر رقم الحركة لرؤية الفاتورة:", df['id'].tolist())
        path = df[df['id'] == show_img]['image_path'].values
        if path: st.image(path, caption="صورة سند الشراء")

# ----------------- 3. المبيعات اليومية للكروت -----------------
elif choice == "💰 المبيعات اليومية (الكروت)":
    st.title("💰 مبيعات كروت مدى نت اليومية")
    with st.form("sales_form", clear_on_submit=True):
        shop = st.text_input("اسم السوبرماركت أو البقالة:")
        card_type = st.text_input("فئة الكرت (يومي / أسبوعي / شهري):")
        qty = st.number_input("الكمية المباعة:", min_value=1, step=1)
        total = st.number_input("إجمالي المبلغ من الجمهور:")
        comm = st.number_input("نسبة ربح البقالة المستقطعة:")
        
        if st.form_submit_button("تسجيل الفاتورة"):
            net = total - comm
            cursor.execute("INSERT INTO sales (date, shop, card_type, qty, total, comm, net) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                           (current_date, shop, card_type, qty, total, comm, net))
            conn.commit()
            st.success("تم تسجيل حركة مبيعات الكروت بنجاح!")
            
    df = pd.read_sql_query("SELECT date as التاريخ, shop as البقالة, card_type as الفئة, qty as الكمية, total as الإجمالي, comm as العمولة, net as الصافي FROM sales", conn)
    st.dataframe(df, use_container_width=True)

# ----------------- 4. المصاريف والخرج -----------------
elif choice == "📉 المصاريف والخرج":
    st.title("📉 تسجيل مصاريف وخرج شبكة مدى نت")
    with st.form("exp_form", clear_on_submit=True):
        exp_type = st.selectbox("نوع المصروف:", ["ثابت (ستارلينك / يمن نت)", "متغير (طباعة كروت / صيانة)"])
        statement = st.text_input("البيان بالتفصيل:")
        amount = st.number_input("المبلغ الخارج:")
        file = st.file_uploader("التقط أو ارفع صورة فاتورة الخرج:", type=['jpg', 'jpeg', 'png'])
        
        if st.form_submit_button("تسجيل الخرج"):
            img_path = ""
            if file is not None:
                img_path = f"documents/exp_{int(datetime.now().timestamp())}.png"
                with open(img_path, "wb") as f:
                    f.write(file.getbuffer())
            cursor.execute("INSERT INTO expenses (date, type, statement, amount, image_path) VALUES (?, ?, ?, ?, ?)", 
                           (current_date, exp_type, statement, amount, img_path))
            conn.commit()
            st.success("تم تسجيل مصروف الشبكة بنجاح!")
            
    df = pd.read_sql_query("SELECT id, date as التاريخ, type as النوع, statement as البيان, amount as المبلغ, image_path FROM expenses", conn)
    if not df.empty:
        st.dataframe(df.drop(columns=['image_path']), use_container_width=True)
        show_img = st.selectbox("اختر رقم المصروف لرؤية صورته:", df['id'].tolist())
        path = df[df['id'] == show_img]['image_path'].values
        if path: st.image(path, caption="صورة الفاتورة")

# ----------------- 5. حركات الشركاء والرواتب -----------------
elif choice == "👤 حركات الشركاء والرواتب":
    st.title("👤 إدارة حسابات شركاء مدى نت والرواتب")
    with st.form("tx_form", clear_on_submit=True):
        party = st.selectbox("الطرف المعني:", ["أنا", "الشريك"])
        tx_type = st.selectbox("نوع الحركة الموثقة:", ["راتب مستحق", "سحب أرباح شخصية", "تحويل مالي للشريك"])
