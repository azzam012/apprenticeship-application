# 1. models/student.py (ملف إدارة بيانات الطلاب)

"""
أ. يتأكد من ملف القاعدة ويسويه ديناميكياً
يحفظ مسار الـ SQLite بحيث يشتغل على أي جهاز
"""

import os
import sqlite3

db_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..', 'database', 'apprenticeship.db'
    )
)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ب. يتأكد من إنشاء الجدول عند أول تشغيل
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    mobile_number TEXT NOT NULL,
    email TEXT NOT NULL,
    gpa REAL NOT NULL CHECK(gpa >= 0 AND gpa <= 5),
    specialization TEXT NOT NULL,
    preferred_locations TEXT NOT NULL,
    skills TEXT NOT NULL
)
""")
conn.commit()
conn.close()

"""
ج. يكتب الدوال الأساسية:
"""

def add_student(student_id, name, mobile_number, email, gpa, specialization, preferred_locations, skills):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO students (
        student_id, name, mobile_number, email, gpa, specialization, preferred_locations, skills
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (student_id, name, mobile_number, email, gpa, specialization, preferred_locations, skills))
    conn.commit()
    conn.close()

def get_student_info(student_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_student(student_id, **kwargs):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    updates = ", ".join(f"{key} = ?" for key in kwargs)
    values = list(kwargs.values()) + [student_id]
    cursor.execute(f"UPDATE students SET {updates} WHERE student_id = ?", values)
    conn.commit()
    conn.close()

def get_all_students():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    result = cursor.fetchall()
    conn.close()
    return result

# if __name__ == "__main__":
#     add_student("S1001", "Sara Ahmed", "0551234567", "sara@gmail.com", 4.3, "IT", "Riyadh,Jeddah,Dammam", "Python,Excel")
#     print(get_student_info("S1001"))
#     print(get_all_students())
