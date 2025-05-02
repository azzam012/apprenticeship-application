# =====================================
# Database Setup Section (students, companies, applications)
# =====================================

import sys
import os
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt

# -------------------------------------
# Database Path Configuration
# -------------------------------------
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'database', 'apprenticeship.db'))

# =====================================
# Authentication Setup (MC4 Role)
# =====================================

from datetime import datetime
import bcrypt

# Define auth classes
class AuthModel:
    def __init__(self, db_path):
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
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
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def check_password(hashed_password, user_password):
        return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def is_strong_password(password):
        if len(password) < 8:
            return False
        if not any(char.isdigit() for char in password):
            return False
        if not any(char.isalpha() for char in password):
            return False
        return True

    def log_access(self, user_id, user_type, status):
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
    def add_student(self, student_id, name, mobile_number, email, password, gpa, specialization, preferred_locations, skills):
        if not self.is_strong_password(password):
            raise ValueError("Password must be at least 8 characters with letters and numbers")

        hashed_password = self.hash_password(password)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO students (student_id, name, mobile_number, email, password, gpa, specialization, preferred_locations, skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (student_id, name, mobile_number, email, hashed_password, gpa, specialization, preferred_locations, skills))
            conn.commit()
            self.log_access(student_id, "student", "success")
        
        except sqlite3.IntegrityError as e:
            if "email" in str(e):
                raise ValueError("Email already exists")
            raise
        
        finally:
            conn.close()

    def get_student_by_email_and_password(self, email, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, password FROM students WHERE email = ?", (email,))
        result = cursor.fetchone()
        conn.close()
        if result and self.check_password(result[1], password):
            self.log_access(result[0], "student", "success")
            return (result[0],)
        else:
            self.log_access(email, "student", "failed")
            return None

class CompanyAuthModel(AuthModel):
    
    def add_company(self, company_name, company_email, company_password):
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
            self.log_access(company_name, "company", "success")
        
        except sqlite3.IntegrityError as e:
            if "company_email" in str(e):
                raise ValueError("Company email already exists")
            raise
        
        finally:
            conn.close()

    def get_company_by_email_and_password(self, email, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT company_name, company_password FROM companies WHERE company_email = ?", (email,))
        result = cursor.fetchone()
        conn.close()
        
        if result and self.check_password(result[1], password):
            self.log_access(result[0], "company", "success")
            return (result[0],)
        
        else:
            self.log_access(email, "company", "failed")
            return None

# Initialize authentication handlers
student_auth = StudentAuthModel(db_path)
company_auth = CompanyAuthModel(db_path)
# ==========================
# Create all tables
# ==========================
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Students Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    mobile_number TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    gpa REAL NOT NULL CHECK(gpa >= 0 AND gpa <= 5),
    specialization TEXT NOT NULL,
    preferred_locations TEXT NOT NULL,
    skills TEXT NOT NULL
)
""")

# Companies Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS companies (
    company_name TEXT PRIMARY KEY,
    company_email TEXT UNIQUE NOT NULL,
    company_password TEXT NOT NULL
)
""")

# Openings Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS openings (
    opening_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    specialization TEXT NOT NULL,
    location TEXT NOT NULL,
    stipend INTEGER NOT NULL CHECK(stipend > 0),
    required_skills TEXT NOT NULL,
    FOREIGN KEY (company_name) REFERENCES companies(company_name)
)
""")

# Applications Table
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

# =====================================
# Login Window UI (LoginDialog)
# =====================================

class LoginDialog(QDialog):
    
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(__file__), "login.ui"), self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.handel_login_buttons()
    
    def handel_login_buttons(self):
        self.login_button.clicked.connect(self.handle_login)
        self.student_signup_button.clicked.connect(self.open_student_signup)
        self.company_signup_button.clicked.connect(self.open_company_signup)
        

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter both email and password.")
            return

        if self.student_radio.isChecked():
            student = student_auth.get_student_by_email_and_password(email, password)
            
            if student:
                self.close()
                self.dashboard_window = StudentDashboard(student_id=student[0])
                self.dashboard_window.show()
            else:
                QMessageBox.warning(self, "Error", "Invalid email or password")

        elif self.company_radio.isChecked():
            company = company_auth.get_company_by_email_and_password(email, password)
            if company:
                self.close()
                self.dashboard_window = CompanyDashboard(company_name=company[0])
                self.dashboard_window.show()
            else:
                QMessageBox.warning(self, "Error", "Invalid email or password for company.")

        else:
            QMessageBox.warning(self, "Error", "Please select your user type.")

    def open_student_signup(self):
        self.student_signup_window = StudentSignup()
        self.student_signup_window.exec_()

    def open_company_signup(self):
        self.company_signup_window = CompanySignup()
        self.company_signup_window.exec_()

# =====================================
# Student Signup Window UI (StudentSignup)
# =====================================

class StudentSignup(QDialog):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(__file__), "student_signup.ui"), self)
        self.signup_button.clicked.connect(self.register_student)
        self.password_input.setEchoMode(QLineEdit.Password)

    def register_student(self):
        name = self.name_input.text()
        student_id = self.id_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        gpa = self.gpa_input.text()
        mobile = self.mobile_input.text()
        specialization = self.specialization_input.text()
        skills = self.skills_input.text()
        locations = self.locations_input.text()

        if not all([name, student_id, email, password, gpa, mobile, specialization, skills, locations]):
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return

        try:
            gpa = float(gpa)
        except ValueError:
            QMessageBox.warning(self, "Error", "GPA must be a number")
            return

        try:
            student_auth.add_student(student_id, name, mobile, email, password, gpa, specialization, locations, skills)
            QMessageBox.information(self, "Success", "Student registered successfully")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

# =====================================
# Company Signup Window UI (CompanySignup)
# =====================================

class CompanySignup(QDialog):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(__file__), "company_signup.ui"), self)
        self.signup_button.clicked.connect(self.register_company)
        self.password_input.setEchoMode(QLineEdit.Password)

    def register_company(self):
        company_name = self.company_name_input.text()
        company_email = self.email_input.text()
        company_password = self.password_input.text()

        if not all([company_name, company_email, company_password]):
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return

        try:
            company_auth.add_company(company_name, company_email, company_password)
            QMessageBox.information(self, "Success", "Company registered successfully")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

# =====================================
# Student Dashboard UI (StudentDashboard)
# =====================================

class StudentDashboard(QMainWindow):
    def __init__(self, student_id):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(__file__), "student_dashboard.ui"), self)

        self.current_student_id = student_id
        self.student_tabWidget.tabBar().setVisible(False)
        self.handle_student_buttons()

    def handle_student_buttons(self):
        self.student_info_button.clicked.connect(self.open_info_tab)
        self.student_applications_button.clicked.connect(self.open_applications_tab)
        self.student_oppourtunities_button.clicked.connect(self.open_oppourtunities_tab)
        self.student_logout_button.clicked.connect(self.logout)
        self.save_changes_button.clicked.connect(self.save_changes)
        

    def open_info_tab(self):
        self.student_tabWidget.setCurrentIndex(0)
        self.load_student_info()

    def open_applications_tab(self):
        self.student_tabWidget.setCurrentIndex(1)

    def open_oppourtunities_tab(self):
        self.student_tabWidget.setCurrentIndex(2)

    def logout(self):
        QApplication.quit()

    def load_student_info(self):
        student_info = self.get_student_info()

        if student_info:
            headers = [
                "Student ID", "Name", "Mobile Number", "Email", "Password",
                "GPA", "Specialization", "Preferred Locations", "Skills"
            ]

            self.student_info_table.clear()
            self.student_info_table.setRowCount(len(headers))
            self.student_info_table.setColumnCount(2)
            self.student_info_table.setHorizontalHeaderLabels(["Field", "Value"])

            self.zipped = list(zip(headers, student_info))
            for i in range(len(self.zipped)):
                self.student_info_table.setItem(i, 0, QTableWidgetItem(self.zipped[i][0]))
                self.student_info_table.setItem(i, 1, QTableWidgetItem(str(self.zipped[i][1])))

            self.student_info_table.resizeColumnsToContents()
            self.student_info_table.horizontalHeader().setStretchLastSection(True)
            self.student_info_table.verticalHeader().setVisible(False)
            self.student_info_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            QMessageBox.warning(self, "Error", "Could not load student information.")

    def get_student_info(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE student_id = ?", (self.current_student_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def load_edit_info(self):
        student_info = self.get_student_info()

        if student_info:
            self.edit_name_input.setText(student_info[1])
            self.edit_mobile_input.setText(student_info[2])
            self.edit_email_input.setText(student_info[3])
            self.edit_password_input.setText(student_info[4])
            self.edit_gpa_input.setText(str(student_info[5]))
            self.edit_specialization_input.setText(student_info[6])
            self.edit_locations_input.setText(student_info[7])
            self.edit_skills_input.setText(student_info[8])

    def save_changes(self):
        name = self.edit_name_input.text()
        mobile = self.edit_mobile_input.text()
        email = self.edit_email_input.text()
        password = self.edit_password_input.text()
        gpa = self.edit_gpa_input.text()
        specialization = self.edit_specialization_input.text()
        locations = self.edit_locations_input.text()
        skills = self.edit_skills_input.text()

        if not all([name, mobile, email, password, gpa, specialization, locations, skills]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields before saving.")
            return

        try:
            gpa = float(gpa)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "GPA must be a valid number.")
            return
        
        hashed_password = student_auth.hash_password(password)
        updated_data = {
            "name": name,
            "mobile_number": mobile,
            "email": email,
            "password": hashed_password,
            "gpa": gpa,
            "specialization": specialization,
            "preferred_locations": locations,
            "skills": skills
        }

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            updates = ", ".join(f"{key} = ?" for key in updated_data)
            values = list(updated_data.values()) + [self.current_student_id]
            cursor.execute(f"UPDATE students SET {updates} WHERE student_id = ?", values)
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Your information has been updated successfully!")
            self.load_student_info()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update information: {str(e)}")

    from PyQt5.QtCore import Qt

    def load_opportunities(self):
        #  Get student info
        student_info = self.get_student_info()
        if not student_info:
            QMessageBox.warning(self, "Error", "Failed to load student data.")
            return

        specialization = student_info[6].lower().strip()

        skills_text = student_info[8].lower()
        skills = set(s.strip() for s in skills_text.split(","))

        locations_text = student_info[7].lower()
        locations = set(l.strip() for l in locations_text.split(","))


        #  Get all openings
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT company_name, specialization, location, stipend, required_skills FROM openings")
        all_openings = cursor.fetchall()
        conn.close()

        # Filter openings that match student
        matching = []
        for opening in all_openings:
            comp_name, spec, loc, stipend, required_skills = opening

            if spec.strip().lower() != specialization:
                continue

            required = set(s.strip().lower() for s in required_skills.split(","))
            if not skills & required:
                continue

            if loc.strip().lower() not in locations:
                continue

            matching.append(opening)

        # Show in table
        headers = ["Company", "Specialization", "Location", "Stipend", "Required Skills"]
        self.student_oppourtunities_table.setColumnCount(len(headers))
        self.student_oppourtunities_table.setRowCount(len(matching))
        self.student_oppourtunities_table.setHorizontalHeaderLabels(headers)

        for row_index, row_data in enumerate(matching):
            for col_index, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.student_oppourtunities_table.setItem(row_index, col_index, item)

        self.student_oppourtunities_table.resizeColumnsToContents()
        self.student_oppourtunities_table.horizontalHeader().setStretchLastSection(True)
        self.student_oppourtunities_table.verticalHeader().setVisible(False)


# =====================================
# Company Dashboard UI (CompanyDashboard)
# =====================================

class CompanyDashboard(QMainWindow):
    def __init__(self, company_name):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(__file__), "company_dashboard.ui"), self)

        self.current_company_name = company_name
        self.handle_company_buttons()

    def handle_company_buttons(self):
        self.view_company_info_button.clicked.connect(self.open_company_info_tab)
        self.view_company_openings_button.clicked.connect(self.open_company_openings_tab)
        self.view_company_addopenings_button.clicked.connect(self.open_company_addopenings_tab)
        self.view_company_applications_button.clicked.connect(self.open_company_applications_tab)
        self.company_save_changes_button.clicked.connect(self.save_company_changes)
        self.add_opening_button.clicked.connect(self.handle_add_opening)
        self.company_logout_button.clicked.connect(self.company_logout)

    def open_company_info_tab(self):
        self.company_tabWidget.setCurrentIndex(0)
        self.load_company_info()

    def open_company_openings_tab(self):
        self.company_tabWidget.setCurrentIndex(1)
        self.load_company_openings()

    def open_company_addopenings_tab(self):
        self.company_tabWidget.setCurrentIndex(2)

    def open_company_applications_tab(self):
        self.company_tabWidget.setCurrentIndex(3)

    def load_company_info(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE company_name = ?", (self.current_company_name,))
        company_info = cursor.fetchone()
        conn.close()

        if company_info:
            headers = ["Company Name", "Email", "Password"]
            self.company_info_table.clear()
            self.company_info_table.setRowCount(len(headers))
            self.company_info_table.setColumnCount(2)
            self.company_info_table.setHorizontalHeaderLabels(["Field", "Value"])

            for i in range(len(headers)):
                self.company_info_table.setItem(i, 0, QTableWidgetItem(headers[i]))
                self.company_info_table.setItem(i, 1, QTableWidgetItem(str(company_info[i])))

            self.company_info_table.resizeColumnsToContents()
            self.company_info_table.horizontalHeader().setStretchLastSection(True)
            self.company_info_table.verticalHeader().setVisible(False)
            self.company_info_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            QMessageBox.warning(self, "Error", "Failed to load company information.")



    def save_company_changes(self):
        
        name = self.edit_company_name_input.text()
        email = self.edit_company_email_input.text()
        password = self.edit_company_password_input.text()

        if not all([name, email, password]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields before saving.")
            return
        
        hashed_password = company_auth.hash_password(password)

        updated_company_data = {
            "company_name": name,
            "company_email": email,
            "company_password": hashed_password,
        }

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            updates = ", ".join(f"{key} = ?" for key in updated_company_data)
            values = list(updated_company_data.values()) + [self.current_company_name]
            cursor.execute(f"UPDATE companies SET {updates} WHERE company_name = ?", values)
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Company information updated successfully!")
            self.load_company_info()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update information: {str(e)}")



    def handle_add_opening(self):
        specialization = self.requierd_specialization_input.text()
        location = self.requierd_location_input.text()
        stipend = self.stipend_input.text()
        skills = self.requierd_skills_input.text()

        if not all([specialization, location, stipend, skills]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        try:
            stipend = int(stipend)
            if stipend <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Stipend must be a positive number.")
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO openings (company_name, specialization, location, stipend, required_skills)
                VALUES (?, ?, ?, ?, ?)
            """, (self.current_company_name, specialization, location, stipend, skills))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Opening added successfully.")
            self.requierd_specialization_input.clear()
            self.requierd_location_input.clear()
            self.stipend_input.clear()
            self.requierd_skills_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add opening: {str(e)}")

    def load_company_openings(self):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT opening_id, specialization, location, stipend, required_skills
                FROM openings
                WHERE company_name = ?
            """, (self.current_company_name,))
            openings = cursor.fetchall()
            conn.close()

            headers = ["ID", "Specialization", "Location", "Stipend", "Skills"]
            self.company_openings_table.setColumnCount(len(headers))
            self.company_openings_table.setRowCount(len(openings))
            self.company_openings_table.setHorizontalHeaderLabels(headers)
            self.company_openings_table.horizontalHeader().setStretchLastSection(True)               # To make the shape better
            self.company_openings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            for row_index, row_data in enumerate(openings):
                for col_index, value in enumerate(row_data):
                    self.company_openings_table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

            self.company_openings_table.resizeColumnsToContents()
            self.company_openings_table.horizontalHeader().setStretchLastSection(True)
            self.company_openings_table.verticalHeader().setVisible(False)
            self.company_openings_table.horizontalHeader().setVisible(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load openings: {str(e)}")





    def company_logout(self):
        self.close()

# The rest of the UI classes and dashboards are being added next.

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    app = QApplication(sys.argv)
    window = LoginDialog()
    window.show()
    sys.exit(app.exec_())
