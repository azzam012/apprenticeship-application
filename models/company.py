#MC3 USE THIS: add_opening

"""
MC1: Database – Apprenticeship Openings Table

This file connects to the SQLite database and does two main things:
1. Creates the 'openings' table (if it doesn't exist already)
2. Provides the function 'add_opening()' for MC3 to insert company data

To use: call add_opening(specialization, location, stipend, required_skills)
"""
import sqlite3

#Connects to database file
conn = sqlite3.connect("database/apprenticeship")
cursor = conn.cursor()


# Create the 'openings' table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS openings (
    opening_id INTEGER PRIMARY KEY AUTOINCREMENT,
    specialization TEXT NOT NULL,
    location TEXT NOT NULL,
    stipend INTEGER NOT NULL CHECK(stipend > 0),
    required_skills TEXT NOT NULL
)
""")


# Save and close connection
conn.commit
conn.close

def add_opening (specialization,location,stipend,required_skills):
    conn = sqlite3.connect("database/apprenticeship")
    cursor = conn.cursor

    cursor.execute("""
    INSERT INTO openings (specilazation, location, stipend, required_skills)
    VALUES (?,?,?,?) """, (specialization, location, stipend, required_skills))
    conn.commit
    conn.close