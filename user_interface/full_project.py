# =====================================
# Database Setup Section (students, companies, applications)
# =====================================

import sys
import os
import sqlite3
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

# -------------------------------------
# Database Path Configuration
# -------------------------------------
db_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        'database', 'apprenticeship.db'
    )
)

# Create students table if it does not exist
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
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
conn.commit()

# Create companies table if it does not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    company_email TEXT UNIQUE NOT NULL,
    company_password TEXT NOT NULL
)
""")

# Create openings table if it does not exist
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

# Create applications table if it does not exist
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

# -------------------------------------
# Database Operation Functions
# -------------------------------------

def add_student(student_id, name, mobile_number, email, password, gpa, specialization, preferred_locations, skills):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO students (student_id, name, mobile_number, email, password, gpa, specialization, preferred_locations, skills)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (student_id, name, mobile_number, email, password, gpa, specialization, preferred_locations, skills))
    conn.commit()
    conn.close()

def get_student_info(student_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_student_by_email_and_password(email, password):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT student_id FROM students WHERE email = ? AND password = ?", (email, password))
    result = cursor.fetchone()
    conn.close()
    return result

# Function to update student info
def update_student(student_id, **kwargs):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    updates = ", ".join(f"{key} = ?" for key in kwargs)
    values = list(kwargs.values()) + [student_id]
    cursor.execute(f"UPDATE students SET {updates} WHERE student_id = ?", values)
    conn.commit()
    conn.close()


def add_company(company_name, company_email, company_password):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO companies (company_name, company_email, company_password)
    VALUES (?, ?, ?)
    """, (company_name, company_email, company_password))
    conn.commit()
    conn.close()

# =====================================
# UI Sections (Login, Signups, Dashboards)
# =====================================

# -------------------------------------
# Student Signup Window
# -------------------------------------
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
            add_student(student_id, name, mobile, email, password, gpa, specialization, locations, skills)
            QMessageBox.information(self, "Success", "Student registered successfully")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

# -------------------------------------
# Company Signup Window
# -------------------------------------
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
            add_company(company_name, company_email, company_password)
            QMessageBox.information(self, "Success", "Company registered successfully")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

# -------------------------------------
# Login Window
# -------------------------------------
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(__file__), "login.ui"), self)

        self.login_button.clicked.connect(self.handle_login)
        self.student_signup_button.clicked.connect(self.open_student_signup)
        self.company_signup_button.clicked.connect(self.open_company_signup)
        self.password_input.setEchoMode(QLineEdit.Password)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter both email and password.")
            return

        if self.student_radio.isChecked():
            student = get_student_by_email_and_password(email, password)
            if student:
                self.close()
                self.dashboard_window = StudentDashboard(student_id=student[0])
                self.dashboard_window.show()
            else:
                QMessageBox.warning(self, "Error", "Invalid email or password")
        else:
            QMessageBox.warning(self, "Error", "Please select your user type.")

    def open_student_signup(self):
        self.student_signup_window = StudentSignup()
        self.student_signup_window.exec_()

    def open_company_signup(self):
        self.company_signup_window = CompanySignup()
        self.company_signup_window.exec_()

# -------------------------------------
# Student Dashboard
# -------------------------------------
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
        student_info = get_student_info(self.current_student_id)

        if student_info:
            headers = [
                "Student ID", "Name", "Mobile Number", "Email", "Password",
            "GPA", "Specialization", "Preferred Locations", "Skills"
            ]

            self.student_info_table.clear()
            self.student_info_table.setRowCount(len(headers))
            self.student_info_table.setColumnCount(2)
            self.student_info_table.setHorizontalHeaderLabels(["Field", "Value"])

            for row, (field, value) in enumerate(zip(headers, student_info)):
                self.student_info_table.setItem(row, 0, QTableWidgetItem(field))
                self.student_info_table.setItem(row, 1, QTableWidgetItem(str(value)))

            self.student_info_table.resizeColumnsToContents()
            self.student_info_table.horizontalHeader().setStretchLastSection(True)
            self.student_info_table.verticalHeader().setVisible(False)
            self.student_info_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            QMessageBox.warning(self, "Error", "Could not load student information.")

    def load_edit_info(self):
        student_info = get_student_info(self.current_student_id)
        
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
    # Read values from LineEdits
        name = self.edit_name_input.text()
        mobile = self.edit_mobile_input.text()
        email = self.edit_email_input.text()
        password = self.edit_password_input.text()
        gpa = self.edit_gpa_input.text()
        specialization = self.edit_specialization_input.text()
        locations = self.edit_locations_input.text()
        skills = self.edit_skills_input.text()

        # Validate that all fields are filled
        if not all([name, mobile, email, password, gpa, specialization, locations, skills]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields before saving.")
            return

        # Validate that GPA is a number
        try:
            gpa = float(gpa)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "GPA must be a valid number.")
            return

        # Prepare the updated data
        updated_data = {
            "name": name,
            "mobile_number": mobile,
            "email": email,
            "password": password,
            "gpa": gpa,
            "specialization": specialization,
            "preferred_locations": locations,
            "skills": skills
        }

        try:
            update_student(self.current_student_id, **updated_data)
            QMessageBox.information(self, "Success", "Your information has been updated successfully!")

            # Reload info tab to show updated information
            self.load_student_info()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update information: {str(e)}")



# -------------------------------------
# Company Dashboard
# -------------------------------------
class CompanyDashboard(QMainWindow):
    def __init__(self, company_id=None):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(__file__), "company_dashboard.ui"), self)

        self.company_id = company_id
        self.view_info_button.clicked.connect(self.view_company_info)
        self.view_openings_button.clicked.connect(self.view_company_openings)
        self.add_opening_button.clicked.connect(self.add_new_opening)
        self.logout_button.clicked.connect(self.logout)

    def view_company_info(self):
        QMessageBox.information(self, "Company Info", f"Showing info for company ID: {self.company_id}")

    def view_company_openings(self):
        QMessageBox.information(self, "Company Openings", "Here are your current openings.")

    def add_new_opening(self):
        QMessageBox.information(self, "Add Opening", "Opening a form to add a new opportunity.")

    def logout(self):
        self.close()

# =====================================
# Application Entry Point (main)
# =====================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginDialog()
    window.show()
    sys.exit(app.exec_())
