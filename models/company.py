# MC1 USE THIS: add_opening(), add_company()
# You can also use: delete_opening(opening_id), view_openings(),
#                   delete_company(company_id), view_companies() ← for testing only

"""
MC1: Database – Apprenticeship Opening Management

This file connects to the SQLite database and handles two main tables:
1. 'openings'  – stores internship openings posted by companies
2. 'companies' – stores company account information (name, email, password)

✅ For MC3 (logic teammate):
You can call these functions directly to insert new data:
- add_opening(specialization, location, stipend, required_skills)
- add_company(company_name, company_email, company_password)

NOTE: All data is saved in database/apprenticeship.db
"""

import sqlite3

# Create the 'openings' and 'companies' tables if they don't exist
conn = sqlite3.connect("C:/Users/user/Documents/GitHub/apprenticeship-application/database/apprenticeship.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS openings (
    opening_id INTEGER PRIMARY KEY AUTOINCREMENT,
    specialization TEXT NOT NULL,
    location TEXT NOT NULL,
    stipend INTEGER NOT NULL CHECK(stipend > 0),
    required_skills TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    company_email TEXT UNIQUE NOT NULL,
    company_password TEXT NOT NULL
)
""")

conn.commit()
conn.close()

# MC3 FUNCTION – Add new internship opening
def add_opening(specialization, location, stipend, required_skills):
    conn = sqlite3.connect("C:/Users/user/Documents/GitHub/apprenticeship-application/database/apprenticeship.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO openings (
        specialization, location, stipend, required_skills
    ) VALUES (?, ?, ?, ?)
    """, (specialization, location, stipend, required_skills))

    conn.commit()
    conn.close()

# MC3 FUNCTION – Add company account
def add_company(company_name, company_email, company_password):
    conn = sqlite3.connect("C:/Users/user/Documents/GitHub/apprenticeship-application/database/apprenticeship.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO companies (
        company_name, company_email, company_password
    ) VALUES (?, ?, ?)
    """, (company_name, company_email, company_password))

    conn.commit()
    conn.close()

# 🧹 Utility functions for testing
def delete_opening(opening_id):
    conn = sqlite3.connect("C:/Users/user/Documents/GitHub/apprenticeship-application/database/apprenticeship.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM openings WHERE opening_id = ?", (opening_id,))
    conn.commit()
    conn.close()

def view_openings():
    conn = sqlite3.connect("C:/Users/user/Documents/GitHub/apprenticeship-application/database/apprenticeship.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM openings")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()

def delete_company(company_id):
    conn = sqlite3.connect("C:/Users/user/Documents/GitHub/apprenticeship-application/database/apprenticeship.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM companies WHERE company_id = ?", (company_id,))
    conn.commit()
    conn.close()

def view_companies():
    conn = sqlite3.connect("C:/Users/user/Documents/GitHub/apprenticeship-application/database/apprenticeship.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()
