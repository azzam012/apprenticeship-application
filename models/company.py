# MC3 USE THIS: add_opening()
# You can also use: delete_opening(opening_id) or view_openings() for testing

"""
MC1: Database – Apprenticeship Openings Table

This file connects to the SQLite database and does two main things:
1. Creates the 'openings' table (if it doesn't exist already)
2. Provides the function 'add_opening()' for MC3 to insert company data

To use: call add_opening(specialization, location, stipend, required_skills)
"""

import sqlite3

# Create the 'openings' table if it doesn't exist
conn = sqlite3.connect("database/apprenticeship")
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

conn.commit()
conn.close()


# FUNCTION MC3 will use to add new openings
def add_opening(specialization, location, stipend, required_skills):
    conn = sqlite3.connect("database/apprenticeship")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO openings (
        specialization, location, stipend, required_skills
    ) VALUES (?, ?, ?, ?)
    """, (specialization, location, stipend, required_skills))

    conn.commit()
    conn.close()


# 🧹 Utility functions (for testing only)
def delete_opening(opening_id):
    conn = sqlite3.connect("database/apprenticeship")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM openings WHERE opening_id = ?", (opening_id,))
    conn.commit()
    conn.close()

def view_openings():
    conn = sqlite3.connect("database/apprenticeship")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM openings")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()