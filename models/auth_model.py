# auth_models.py
import sqlite3
import bcrypt
from datetime import datetime


class AuthModel:
    def __init__(self, db_path):
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        """Create necessary tables for authentication"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create access logs table if not exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            user_type TEXT NOT NULL,
            login_time TEXT NOT NULL,
            logout_time TEXT,
            status TEXT NOT NULL
        )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def check_password(hashed_password, user_password):
        """Check if the provided password matches the hashed password"""
        return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def is_strong_password(password):
        """Check if password meets strength requirements"""
        if len(password) < 8:
            return False
        if not any(char.isdigit() for char in password):
            return False
        if not any(char.isalpha() for char in password):
            return False
        return True

    def log_access(self, user_id, user_type, status):
        """Log access attempts to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        INSERT INTO access_logs (user_id, user_type, login_time, status)
        VALUES (?, ?, ?, ?)
        """, (user_id, user_type, login_time, status))
        conn.commit()
        conn.close()


class StudentAuthModel(AuthModel):
    def add_student(self, student_id, name, mobile_number, email, password, gpa, specialization, preferred_locations,
                    skills):
        """Add a new student with hashed password"""
        if not self.is_strong_password(password):
            raise ValueError("Password must be at least 8 characters with letters and numbers")

        hashed_password = self.hash_password(password)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO students (student_id, name, mobile_number, email, password, gpa, specialization, preferred_locations, skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
            student_id, name, mobile_number, email, hashed_password, gpa, specialization, preferred_locations, skills))
            conn.commit()
            self.log_access(student_id, "student", "success")
        except sqlite3.IntegrityError as e:
            if "email" in str(e):
                raise ValueError("Email already exists")
            raise
        finally:
            conn.close()

    def get_student_by_email_and_password(self, email, password):
        """Authenticate student using email and password"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, password FROM students WHERE email = ?", (email,))
        result = cursor.fetchone()
        conn.close()

        if result and self.check_password(result[1], password):
            self.log_access(result[0], "student", "success")
            return (result[0],)  # Return tuple with student_id
        else:
            self.log_access(email, "student", "failed")
            return None


class CompanyAuthModel(AuthModel):
    def add_company(self, company_name, company_email, company_password):
        """Add a new company with hashed password"""
        if not self.is_strong_password(company_password):
            raise ValueError("Password must be at least 8 characters with letters and numbers")

        hashed_password = self.hash_password(company_password)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO companies (company_name, company_email, company_password)
            VALUES (?, ?, ?)
            """, (company_name, company_email, hashed_password))
            conn.commit()
            company_id = cursor.lastrowid
            self.log_access(str(company_id), "company", "success")
        except sqlite3.IntegrityError as e:
            if "company_email" in str(e):
                raise ValueError("Company email already exists")
            raise
        finally:
            conn.close()

    def get_company_by_email_and_password(self, email, password):
        """Authenticate company using email and password"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT company_id, company_password FROM companies WHERE company_email = ?", (email,))
        result = cursor.fetchone()
        conn.close()

        if result and self.check_password(result[1], password):
            self.log_access(str(result[0]), "company", "success")
            return (result[0],)  # Return tuple with company_id
        else:
            self.log_access(email, "company", "failed")
            return None
