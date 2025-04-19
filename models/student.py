# MC3 USE THIS: add_student()
# You can also use: delete_student(student_id) or view_students() for testing

"""
MC1: Database – Student Profile Table

This file connects to the SQLite database and does two main things:
1. Creates the 'students' table (if it doesn't exist already)
2. Provides the function 'add_student()' for MC3 to insert student data

To use: call add_student(student_id, name, mobile_number, email, gpa, specialization, preferred_locations, skills)
"""

import sqlite3

# Create the 'students' table if it doesn't exist
conn = sqlite3.connect("database/apprenticeship")
cursor = conn.cursor()

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


# FUNCTION MC3 will use to add new students
def add_student(student_id, name, mobile_number, email, gpa, specialization, preferred_locations, skills):
    conn = sqlite3.connect("database/apprenticeship")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO students (
        student_id, name, mobile_number, email, gpa, specialization, preferred_locations, skills
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (student_id, name, mobile_number, email, gpa, specialization, preferred_locations, skills))

    conn.commit()
    conn.close()


# 🧹 Utility functions (for testing only)
def delete_student(student_id):
    conn = sqlite3.connect("database/apprenticeship")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()

def view_students():
    conn = sqlite3.connect("database/apprenticeship")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()