import streamlit as st
import pandas as pd
from datetime import date
import os

# পেজের নাম ও আইকন সেট করা
st.set_page_config(page_title="Smart Hazira App", page_icon="📝")
st.title("🏗️ Smart Hazira & Worker Management")

# ১. প্রাথমিক ডেটা সেটআপ (যাতে রিফ্রেশ হলে মুছে না যায়)
if "workers_data" not in st.session_state:
    st.session_state.workers_data = pd.DataFrame({
        "Name": ["Raju", "Ramesh", "Suresh"],
        "Role": ["Mistry", "Labour", "Labour"],
        "Rate (₹)": [800, 500, 500],
        "Status": [True, True, True]
    })

# ==========================================
# ➕ নতুন ওয়ার্কার অ্যাড করার ফর্ম
# ==========================================
with st.expander("➕ Notun Worker Add Korun (এখানে ক্লিক করুন)"):
    new_name = st.text_input("Notun Worker er Naam:")
    new_role = st.selectbox("Role Select Korun:", ["Labour", "Mistry"])
    
    # রোলের উপর ভিত্তি করে রেট ঠিক করা
    default_r = 800 if new_role == "Mistry" else 500
    new_rate = st.number_input("Hazira Rate (₹):", value=default_r)
    
    if st.button("List e Add Korun"):
        if new_name != "":
            new_worker = pd.DataFrame({
                "Name": [new_name],
                "Role": [new_role],
                "Rate (₹)": [new_rate],
                "Status": [True]
            })
            st.session_state.workers_data = pd.concat([st.session_state.workers_data, new_worker], ignore_index=True)
            st.success(f"✅ {new_name} ke list e add kora hoyeche!")
            st.rerun() # পেজ রিফ্রেশ করার জন্য
        else:
            st.error("⚠️ Worker er naam dite hobe!")

st.write("---")

# ==========================================
# 📋 দৈনিক হাজিরা খাতা ও ডিলিট অপশন
# ==========================================
today = st.date_input("Ajker Tarikh (Date):", date.today())
st.write("### 📋 Ajker Hazira Khata")
st.info("💡 **Tip:** কোনো ওয়ার্কারকে ডিলিট করতে চাইলে, টেবিলের বাম দিকের নম্বরে ক্লিক করে পুরো সারিটি (row) সিলেক্ট করুন এবং কীবোর্ডের 'Delete' চাপুন বা ডিলিট আইকনে ক্লিক করুন।")

# এডিটেবল টেবিল 
edited_df = st.data_editor(
    st.session_state.workers_data,
    column_config={
        "Status": st.column_config.CheckboxColumn(
            "Present? ✅",
            help="Tick thakle Present, na thakle Absent",
        )
    },
    num_rows="dynamic", # টেবিল থেকে ডিলিট/অ্যাড করার অপশন
    hide_index=False,
)

# ডেটা আপডেট করা
st.session_state.workers_data = edited_df

# ==========================================
# 💾 ডেটা পার্মানেন্ট সেভ সিস্টেম (CSV File)
# ==========================================
if st.button("💾 Sobar Hazira Save Korun"):
    present_workers = edited_df[edited_df["Status"] == True].copy()
    total_bill = present_workers["Rate (₹)"].sum()
    
    # ডেটাতে তারিখ যুক্ত করা
    present_workers["Date"] = today
    file_name = "hazira_record.csv"
    
    # CSV ফাইলে সেভ করা
    if not os.path.exists(file_name):
        present_workers.to_csv(file_name, index=False)
    else:
        present_workers.to_csv(file_name, mode='a', header=False, index=False)
    
    st.success(f"✅ Hazira Permanent Vabe Save Hoyeche! Date: {today}")
    
    col1, col2 = st.columns(2)
    col1.metric("Aj Present", len(present_workers))
    col2.metric("Ajker Mot Bill", f"₹ {total_bill}")

st.write("---")

# ==========================================
# 📊 পুরনো হিসেব ও মাসিক রিপোর্ট
# ==========================================
st.write("## 📊 Purono Hazirar Hiseb (History & Report)")
file_name = "hazira_record.csv"

if os.path.exists(file_name):
    df_history = pd.read_csv(file_name)
    
    with st.expander("📝 Puro Hazirar Khata Dekhun (পুরো খাতা)"):
        st.dataframe(df_history, use_container_width=True)
    
    st.write("### 🔍 Nirdishto Worker er Hiseb (Monthly Report)")
    
    worker_list = df_history["Name"].unique()
    selected_worker = st.selectbox("Worker er Naam Select Korun:", ["Sobai"] + list(worker_list))
    
    if selected_worker != "Sobai":
        filtered_df = df_history[df_history["Name"] == selected_worker]
        
        st.write(f"**{selected_worker} er Hazirar Details:**")
        st.dataframe(filtered_df, use_container_width=True)
        
        total_din = len(filtered_df)
        total_taka = filtered_df["Rate (₹)"].sum()
        
        col1, col2 = st.columns(2)
        col1.metric("Mot Kaj Koreche", f"{total_din} Din")
        col2.metric("Mot Prapapyo Taka", f"₹ {total_taka}")
else:
    st.info("ℹ️ Ekhono kono hazira save kora hoyni. Prothom hazira save korle ekhane history dekhabe.")
