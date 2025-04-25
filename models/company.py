# 2. models/company.py (ملف إدارة بيانات الشركات)

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
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    company_email TEXT UNIQUE NOT NULL,
    company_password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS openings (
    opening_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    specialization TEXT NOT NULL,
    location TEXT NOT NULL,
    stipend INTEGER NOT NULL CHECK(stipend > 0),
    required_skills TEXT NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
)
""")

conn.commit()
conn.close()

"""
ج. يكتب الدوال الأساسية:
"""

# شركات
def add_company(company_name, company_email, company_password):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO companies (company_name, company_email, company_password)
    VALUES (?, ?, ?)
    """, (company_name, company_email, company_password))
    conn.commit()
    conn.close()

def get_company_info(company_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies WHERE company_id = ?", (company_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_company(company_id, **kwargs):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    updates = ", ".join(f"{key} = ?" for key in kwargs)
    values = list(kwargs.values()) + [company_id]
    cursor.execute(f"UPDATE companies SET {updates} WHERE company_id = ?", values)
    conn.commit()
    conn.close()

def get_all_companies():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies")
    result = cursor.fetchall()
    conn.close()
    return result

# الفرص
def add_opening(company_id, specialization, location, stipend, required_skills):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO openings (
        company_id, specialization, location, stipend, required_skills
    ) VALUES (?, ?, ?, ?, ?)
    """, (company_id, specialization, location, stipend, required_skills))
    conn.commit()
    conn.close()

def get_all_openings():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM openings")
    result = cursor.fetchall()
    conn.close()
    return result

def delete_opening(opening_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM openings WHERE opening_id = ?", (opening_id,))
    conn.commit()
    conn.close()

def view_openings():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM openings")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()
