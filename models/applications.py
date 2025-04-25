# 4. models/applications.py (ملف إدارة الطلبات)

# A. Dynamic database path

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

# B. Create 'applications' table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS applications (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    opening_id INTEGER NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (opening_id) REFERENCES openings(opening_id)
)
""")
conn.commit()
conn.close()

# C. Main application functions

def add_application(student_id, opening_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO applications (student_id, opening_id)
    VALUES (?, ?)
    """, (student_id, opening_id))
    conn.commit()
    conn.close()

# ترجع كل طلبات الطالب
def get_student_applications(student_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM applications WHERE student_id = ?
    """, (student_id,))
    result = cursor.fetchall()
    conn.close()
    return result

# ترجع كل طلبات الفرصة للشركة
def get_opening_applications(opening_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM applications WHERE opening_id = ?
    """, (opening_id,))
    result = cursor.fetchall()
    conn.close()
    return result
