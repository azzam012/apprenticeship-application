# full_project.py
import sys
import os
import sqlite3
import bcrypt
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

# Initialize auth models
from models.auth_model import StudentAuthModel, CompanyAuthModel

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'apprenticeship.db'))
student_auth = StudentAuthModel(db_path)
company_auth = CompanyAuthModel(db_path)


# =====================================
# Database Operation Functions
# =====================================

def add_student(student_id, name, mobile_number, email, password, gpa, specialization, preferred_locations, skills):
    """Add a new student using StudentAuthModel"""
    return student_auth.add_student(student_id, name, mobile_number, email, password, gpa,
                                    specialization, preferred_locations, skills)


def get_student_info(student_id):
    """Get student information"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def get_student_by_email_and_password(email, password):
    """Authenticate student using StudentAuthModel"""
    student_id = student_auth.get_student_by_email_and_password(email, password)
    if student_id:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id[0],))
        result = cursor.fetchone()
        conn.close()
        return result
    return None


def update_student(student_id, **kwargs):
    """Update student information"""
    if 'password' in kwargs:
        if not student_auth.is_strong_password(kwargs['password']):
            raise ValueError("Password must be at least 8 characters with letters and numbers")
        kwargs['password'] = student_auth.hash_password(kwargs['password'])

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    updates = ", ".join(f"{key} = ?" for key in kwargs)
    values = list(kwargs.values()) + [student_id]
    cursor.execute(f"UPDATE students SET {updates} WHERE student_id = ?", values)
    conn.commit()
    conn.close()


def add_company(company_name, company_email, company_password):
    """Add a new company using CompanyAuthModel"""
    return company_auth.add_company(company_name, company_email, company_password)


def get_company_by_email_and_password(email, password):
    """Authenticate company using CompanyAuthModel"""
    company_id = company_auth.get_company_by_email_and_password(email, password)
    if company_id:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE company_id = ?", (company_id[0],))
        result = cursor.fetchone()
        conn.close()
        return result
    return None


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
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
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
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))


# -------------------------------------
# Login Window
# -------------------------------------
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.student_signup_window = StudentSignup()
        self.company_signup_window = None
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
        elif self.company_radio.isChecked():
            company = get_company_by_email_and_password(email, password)
            if company:
                self.close()
                self.dashboard_window = CompanyDashboard(company_id=company[0])
                self.dashboard_window.show()
            else:
                QMessageBox.warning(self, "Error", "Invalid email or password")
        else:
            QMessageBox.warning(self, "Error", "Please select your user type.")

    def open_student_signup(self):
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
            self.load_student_info()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
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
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE company_id = ?", (self.company_id,))
        company_info = cursor.fetchone()
        conn.close()

        if company_info:
            info_str = f"Company ID: {company_info[0]}\nName: {company_info[1]}\nEmail: {company_info[2]}"
            QMessageBox.information(self, "Company Info", info_str)
        else:
            QMessageBox.warning(self, "Error", "Could not load company information.")

    def view_company_openings(self):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM openings WHERE company_id = ?", (self.company_id,))
        openings = cursor.fetchall()
        conn.close()

        if openings:
            openings_str = "\n".join([f"ID: {op[0]}, Specialization: {op[2]}, Location: {op[3]}" for op in openings])
            QMessageBox.information(self, "Company Openings", f"Current Openings:\n{openings_str}")
        else:
            QMessageBox.information(self, "Company Openings", "No current openings")

    def add_new_opening(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Opening")
        layout = QFormLayout(dialog)

        specialization_input = QLineEdit()
        location_input = QLineEdit()
        stipend_input = QLineEdit()
        skills_input = QLineEdit()

        layout.addRow("Specialization:", specialization_input)
        layout.addRow("Location:", location_input)
        layout.addRow("Stipend:", stipend_input)
        layout.addRow("Required Skills:", skills_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addRow(button_box)

        if dialog.exec_() == QDialog.Accepted:
            try:
                stipend = int(stipend_input.text())
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO openings (company_id, specialization, location, stipend, required_skills)
                VALUES (?, ?, ?, ?, ?)
                """, (self.company_id, specialization_input.text(), location_input.text(),
                      stipend, skills_input.text()))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Success", "Opening added successfully")
            except ValueError:
                QMessageBox.warning(self, "Error", "Stipend must be a number")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add opening: {str(e)}")

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