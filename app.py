import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

# ---------- DATABASE SETUP ----------
conn = sqlite3.connect("school.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no INTEGER,
    name TEXT,
    class_name TEXT,
    fee_amount INTEGER,
    fee_date TEXT,
    note TEXT
)
""")
conn.commit()


# ---------- FUNCTIONS ----------
def add_student(roll, name, class_name):
    cur.execute("INSERT INTO students (roll_no, name, class_name) VALUES (?, ?, ?)",
                (roll, name, class_name))
    conn.commit()

def add_fee(student_id, amount, note):
    today = str(date.today())
    cur.execute("UPDATE students SET fee_amount=?, fee_date=?, note=? WHERE id=?",
                (amount, today, note, student_id))
    conn.commit()

def delete_fee(student_id):
    cur.execute("UPDATE students SET fee_amount=NULL, fee_date=NULL, note=NULL WHERE id=?", (student_id,))
    conn.commit()

def delete_student(student_id):
    cur.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()

def get_class_students(class_name):
    return pd.read_sql_query(
        "SELECT id, roll_no, name, fee_amount, fee_date, note FROM students WHERE class_name=? ORDER BY roll_no",
        conn, params=(class_name,)
    )

def all_classes():
    return [c[0] for c in cur.execute("SELECT DISTINCT class_name FROM students")]

def total_school_fee():
    result = cur.execute("SELECT SUM(fee_amount) FROM students").fetchone()[0]
    return result if result else 0

def class_total_fee(class_name):
    result = cur.execute("SELECT SUM(fee_amount) FROM students WHERE class_name=?", (class_name,)).fetchone()[0]
    return result if result else 0

def get_monthly_record(month):
    return pd.read_sql_query(
        "SELECT roll_no, name, class_name, fee_amount, fee_date FROM students WHERE strftime('%Y-%m', fee_date)=? ORDER BY class_name, roll_no",
        conn, params=(month,)
    )


# ---------- STREAMLIT UI ----------
st.title("🏫 The Tecrix AI School Fee Management System")

menu = st.sidebar.selectbox("Select Option", [
    "Add Student",
    "Add Fee",
    "Show Class Record",
    "Total School Fee",
    "Previous Months Record",
    "Delete Student Fee",
    "Delete Student"
])


# ---------------- ADD STUDENT ----------------
if menu == "Add Student":
    st.subheader("➕ Add New Student")

    roll = st.number_input("Roll Number", 1)
    name = st.text_input("Student Name")
    class_name = st.text_input("Class (e.g. Class 6)")

    if st.button("Save"):
        add_student(roll, name, class_name)
        st.success("Student Added Successfully!")


# ---------------- ADD FEE ----------------
elif menu == "Add Fee":
    st.subheader("💰 Add Monthly Fee")

    classes = all_classes()
    selected_class = st.selectbox("Select Class", classes)

    student_id = None

    if selected_class:
        df_students = get_class_students(selected_class)
        student_options = {f"{row['roll_no']} - {row['name']}": row['id'] for index, row in df_students.iterrows()}
        student_label = st.selectbox("Select Student", list(student_options.keys()))
        student_id = student_options[student_label]

    amount = st.number_input("Enter Fee Amount")
    note = st.selectbox("Fee Type", ["Full", "Less"])

    if st.button("Add Fee"):
        if student_id:
            add_fee(student_id, amount, note)
            st.success("Fee Added Successfully!")
        else:
            st.error("Please select class and student first!")


# ---------------- SHOW CLASS DATA ----------------
elif menu == "Show Class Record":
    st.subheader("📘 Class Wise Fee Record")

    classes = all_classes()
    selected_class = st.selectbox("Select Class", classes)

    if st.button("Show Record"):
        df = get_class_students(selected_class)
        st.table(df)

        total_fee = class_total_fee(selected_class)
        st.success(f"💰 **Total Fee Collected for {selected_class}: {total_fee} Rs**")


# ---------------- TOTAL SCHOOL FEE ----------------
elif menu == "Total School Fee":
    st.subheader("🏦 Total School Fee Collection")

    total = total_school_fee()
    st.success(f"💰 **Total Fee Collected: {total} Rs**")


# ---------------- PREVIOUS MONTHS RECORD ----------------
elif menu == "Previous Months Record":
    st.subheader("📅 Previous Monthly Fee Records")

    selected_month = st.text_input("Enter Month (Format: YYYY-MM) Example: 2025-01")

    if st.button("Show Month Record"):
        df_month = get_monthly_record(selected_month)

        if df_month.empty:
            st.warning("No record found for this month!")
        else:
            st.table(df_month)

            total_month_fee = df_month['fee_amount'].sum()
            st.success(f"💰 **Total Fee Collected in {selected_month}: {total_month_fee} Rs**")



# ---------------- DELETE FEE ----------------
elif menu == "Delete Student Fee":
    st.subheader("❌ Delete Student Fee")

    classes = all_classes()
    selected_class = st.selectbox("Select Class", classes)

    if selected_class:
        df_students = get_class_students(selected_class)
        student_options = {f"{row['roll_no']} - {row['name']}": row['id'] for index, row in df_students.iterrows()}
        student_label = st.selectbox("Select Student", list(student_options.keys()))
        student_id = student_options[student_label]

        if st.button("Delete Fee Record"):
            delete_fee(student_id)
            st.success("Student Fee Deleted Successfully!")


# ---------------- DELETE STUDENT ----------------
elif menu == "Delete Student":
    st.subheader("🗑️ Delete Student From System")

    classes = all_classes()
    selected_class = st.selectbox("Select Class", classes)

    if selected_class:
        df_students = get_class_students(selected_class)
        student_options = {f"{row['roll_no']} - {row['name']}": row['id'] for index, row in df_students.iterrows()}
        student_label = st.selectbox("Select Student", list(student_options.keys()))
        student_id = student_options[student_label]

        if st.button("Delete Student"):
            delete_student(student_id)
            st.success("Student Deleted Successfully!")

