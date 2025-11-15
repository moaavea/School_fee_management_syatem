import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

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

def delete_student(student_id):
    cur.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()

def get_class_students(class_name):
    return pd.read_sql_query(
        "SELECT id, roll_no, name FROM students WHERE class_name=? ORDER BY roll_no",
        conn, params=(class_name,)
    )

def all_classes():
    return [c[0] for c in cur.execute("SELECT DISTINCT class_name FROM students")]


# ---------- STREAMLIT UI ----------
st.title("🏫 School Fee Management System")

menu = st.sidebar.selectbox("Select Option", ["Add Student", "Add Fee", "Show Class Record", "Delete Student"])


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
        student_options = {f"{row['roll_no']} - {row['name']}": row['id'] for _, row in df_students.iterrows()}
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
        df = pd.read_sql_query(
            "SELECT roll_no, name, fee_amount, fee_date, note FROM students WHERE class_name=? ORDER BY roll_no",
            conn, params=(selected_class,)
        )
        st.table(df)


# ---------------- DELETE STUDENT ----------------
elif menu == "Delete Student":
    st.subheader("🗑️ Delete Student")

    classes = all_classes()
    selected_class = st.selectbox("Select Class", classes)

    if selected_class:
        df_students = get_class_students(selected_class)

        student_options = {f"{row['roll_no']} - {row['name']}": row['id'] for _, row in df_students.iterrows()}
        selected_student = st.selectbox("Select Student to Delete", list(student_options.keys()))

        student_id = student_options[selected_student]

        if st.button("Delete"):
            delete_student(student_id)
            st.success("Student Deleted Successfully!")
