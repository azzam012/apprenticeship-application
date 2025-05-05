
import sys
import os
import sqlite3
import random


from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from functools import partial

import smtplib                                   # for the emails
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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
    status TEXT DEFAULT 'pending',
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (opening_id) REFERENCES openings(opening_id)
)
""")


conn.commit()
conn.close()


# =====================================
# Email function
# =====================================


def send_email(to_email, subject, body):
    from_email = "watson.bogisich@ethereal.email"
    from_password = "4BmCGmu1EQvTnYPdQe"

    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.ethereal.email", 587)
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(message)
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


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
        self.forgot_password_button.clicked.connect(self.open_reset_password)

        

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

    def open_reset_password(self):
        self.reset_window = ResetPasswordDialog()
        self.reset_window.exec_()


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

            send_email(to_email=email,subject="Confirming Register", body=f"Hello {name}, Welcom to our apprenticeship system")
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
# Reset Password
# =====================================


class ResetPasswordDialog(QDialog):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(__file__), "reset_password_wendow.ui"), self)

        self.reset_tab_widget.tabBar().setVisible(False)

        self.send_code_button.clicked.connect(self.send_code)
        self.reset_password_button.clicked.connect(self.reset_password)

        self.generated_code = None
        self.reset_email = None

    def send_code(self):
        email = self.email_confirm_input.text().strip()
        if not email:
            QMessageBox.warning(self, "Input Error", "Please enter your email.")
            return

        # make sure that the student have the email
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT student_id FROM students WHERE email = ?", (email,))
        student = cursor.fetchone()
        conn.close()

        if not student:
            QMessageBox.warning(self, "Error", "No account found with this email.")
            return

        self.generated_code = str(random.randint(100000, 999999))
        self.reset_email = email

        # sending the email
        send_email(
            to_email=email,
            subject="Password Reset Code",
            body=f"Your password reset code is: {self.generated_code}"
        )

        QMessageBox.information(self, "Success", "Code sent to your email.")
        self.reset_tab_widget.setCurrentIndex(1)

    def reset_password(self):
        entered_code = self.code_input.text().strip()
        new_password = self.new_password_input.text().strip()

        if not entered_code or not new_password:
            QMessageBox.warning(self, "Input Error", "Please enter the code and new password.")
            return

        if entered_code != self.generated_code:
            QMessageBox.critical(self, "Error", "Incorrect code.")
            return

        if not student_auth.is_strong_password(new_password):
            QMessageBox.warning(self, "Weak Password", "Password must be at least 8 characters with letters and numbers.")
            return

        hashed = student_auth.hash_password(new_password)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET password = ? WHERE email = ?", (hashed, self.reset_email))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Password has been reset.")
        self.close()

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
        self.load_applications()

    def open_oppourtunities_tab(self):
        self.student_tabWidget.setCurrentIndex(2)
        self.load_opportunities()

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


    def load_opportunities(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # studen info
        cursor.execute("SELECT * FROM students WHERE student_id = ?", (self.current_student_id,))
        student = cursor.fetchone()
        if not student:
            QMessageBox.warning(self, "Error", "Student info not found.")
            return

        specialization = student[6].strip().lower()
        skills = set(s.strip().lower() for s in student[8].split(","))
        locations = set(l.strip().lower() for l in student[7].split(","))

        if not skills or not locations:
            QMessageBox.warning(self, "Error", "Your profile is incomplete.")
            return

        # the oppertunities that the student applied to
        cursor.execute("SELECT opening_id FROM applications WHERE student_id = ?", (self.current_student_id,))
        applied = set(row[0] for row in cursor.fetchall())

        # all oppertunities
        cursor.execute("SELECT opening_id, company_name, specialization, location, stipend, required_skills FROM openings")
        openings = cursor.fetchall()
        conn.close()

        matching = []
        for opening in openings:
            opening_id, company_name, required_specialization, required_location, stipend_amount, required_skills_text = opening

            if opening_id in applied:
                continue

            if required_specialization.strip().lower() != specialization:
                continue

            if required_location.strip().lower() not in locations:
                continue

            required_skills_set = set(skill.strip().lower() for skill in required_skills_text.split(","))
            if not skills & required_skills_set:
                continue

            matching.append(opening)

        headers = ["Company", "Specialization", "Location", "Stipend", "Required Skills", "Apply"]
        self.student_oppourtunities_table.setRowCount(len(matching))
        self.student_oppourtunities_table.setColumnCount(len(headers))
        self.student_oppourtunities_table.setHorizontalHeaderLabels(headers)

        for row, data in enumerate(matching):
            for col in range(1, 6):  
                self.student_oppourtunities_table.setItem(row, col - 1, QTableWidgetItem(str(data[col])))

            btn = QPushButton("Apply")
            btn.clicked.connect(partial(self.apply_to_opening, data[0]))
            self.student_oppourtunities_table.setCellWidget(row, 5, btn)

        self.student_oppourtunities_table.resizeColumnsToContents()
        self.student_oppourtunities_table.horizontalHeader().setStretchLastSection(True)


    def apply_to_opening(self, opening_id):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO applications (student_id, opening_id) VALUES (?, ?)",
                (self.current_student_id, opening_id)
            )
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "You applied successfully.")
            self.load_opportunities()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Warning", "You already applied for this opening.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Something went wrong: {e}")

    def load_applications(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.company_name, o.specialization, o.location, o.stipend, o.required_skills, a.status
            FROM applications a
            JOIN openings o ON a.opening_id = o.opening_id
            WHERE a.student_id = ?
        """, (self.current_student_id,))
        applications = cursor.fetchall()
        conn.close()

        headers = ["Company", "Specialization", "Location", "Stipend", "Skills", "Status"]
        self.student_applications_table.setRowCount(len(applications))
        self.student_applications_table.setColumnCount(len(headers))
        self.student_applications_table.setHorizontalHeaderLabels(headers)

        for row, app in enumerate(applications):
            for col, value in enumerate(app):
                self.student_applications_table.setItem(row, col, QTableWidgetItem(str(value)))

        self.student_applications_table.resizeColumnsToContents()
        self.student_applications_table.horizontalHeader().setStretchLastSection(True)



# =====================================
# Company Dashboard UI (CompanyDashboard)
# =====================================

class CompanyDashboard(QMainWindow):
    def __init__(self, company_name):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(__file__), "company_dashboard.ui"), self)

        self.company_tabWidget.tabBar().setVisible(False)
        self.current_company_name = company_name
        self.handle_company_buttons()

    def handle_company_buttons(self):
        self.view_company_info_button.clicked.connect(self.open_company_info_tab)
        self.view_company_openings_button.clicked.connect(self.open_company_openings_tab)
        self.view_company_addopenings_button.clicked.connect(self.open_company_addopenings_tab)
        self.view_company_applications_button.clicked.connect(self.open_company_applications_tab)
        self.company_save_changes_button.clicked.connect(self.save_company_changes)
        self.add_opening_button.clicked.connect(self.handle_add_opening)
        self.view_company_applications_button.clicked.connect(self.open_company_applications_tab)
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
        self.load_applications()

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

            headers = ["ID", "Specialization", "Location", "Stipend", "Skills", "Delete"]
            self.company_openings_table.setColumnCount(len(headers))
            self.company_openings_table.setRowCount(len(openings))
            self.company_openings_table.setHorizontalHeaderLabels(headers)
            self.company_openings_table.horizontalHeader().setStretchLastSection(True)               # To make the shape better
            self.company_openings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            for row_index, row_data in enumerate(openings):
                for col_index, value in enumerate(row_data):
                    self.company_openings_table.setItem(row_index, col_index, QTableWidgetItem(str(value)))
                    delete_btn = QPushButton("Delete")
                    delete_btn.clicked.connect(partial(self.delete_opening, row_data[0]))  
                    self.company_openings_table.setCellWidget(row_index, 5, delete_btn)


            self.company_openings_table.resizeColumnsToContents()
            self.company_openings_table.horizontalHeader().setStretchLastSection(True)
            self.company_openings_table.verticalHeader().setVisible(False)
            self.company_openings_table.horizontalHeader().setVisible(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load openings: {str(e)}")


    def load_applications(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.application_id, s.name, s.email, s.gpa, o.opening_id, o.specialization, o.location, a.status
            FROM applications a
            JOIN students s ON a.student_id = s.student_id
            JOIN openings o ON a.opening_id = o.opening_id
            WHERE o.company_name = ?
            ORDER BY s.gpa DESC
        """, (self.current_company_name,))

        applications = cursor.fetchall()
        conn.close()

        headers = ["Student Name", "Email", "GPA", "Specialization", "Location", "Status", "Action"]
        self.company_applications_table.setColumnCount(len(headers))
        self.company_applications_table.setRowCount(len(applications))
        self.company_applications_table.setHorizontalHeaderLabels(headers)

        for row, app in enumerate(applications):
            name, email, gpa, spec, loc, status = app[1], app[2], app[3], app[5], app[6], app[7]
            self.company_applications_table.setItem(row, 0, QTableWidgetItem(name))
            self.company_applications_table.setItem(row, 1, QTableWidgetItem(email))
            self.company_applications_table.setItem(row, 2, QTableWidgetItem(str(gpa)))
            self.company_applications_table.setItem(row, 3, QTableWidgetItem(spec))
            self.company_applications_table.setItem(row, 4, QTableWidgetItem(loc))
            self.company_applications_table.setItem(row, 5, QTableWidgetItem(status))

                    # the accept action will be only if the status is pending
            if status == "pending":
                accept_btn = QPushButton("Accept")
                accept_btn.clicked.connect(partial(self.accept_application, app[0], email, name))
                self.company_applications_table.setCellWidget(row, 6, accept_btn)

        self.company_applications_table.resizeColumnsToContents()
        self.company_applications_table.horizontalHeader().setStretchLastSection(True)




    def accept_application(self, application_id, student_email, student_name):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE applications SET status = 'accepted' WHERE application_id = ?", (application_id,))
            conn.commit()
            conn.close()

                # inform the student if accepted
            send_email(to_email=student_email,  subject="Congrats!, you have been accepted in the apprenticeship",  body=f"Hi {student_name}, you have been accepted for {self.current_company_name}.")

            QMessageBox.information(self, "Success", "Student accepted and notified.")
            self.load_applications()  # update the table

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to accept application: {str(e)}")

    def delete_opening(self, opening_id):
        confirm = QMessageBox.question(self, "Confirm", "Are you sure you want to delete this opening?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute("DELETE FROM applications WHERE opening_id = ?", (opening_id,))
                cursor.execute("DELETE FROM openings WHERE opening_id = ?", (opening_id,))

                conn.commit()
                conn.close()
                QMessageBox.information(self, "Success", "Opening and related applications deleted successfully.")
                self.load_company_openings()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete opening: {e}")




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
