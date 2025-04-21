import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox, QLineEdit
from PyQt5.uic import loadUi
from models.student import add_student 

class StudentSignup(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("user_interface/student_signup.ui", self)
        #self.showFullScreen()

        self.signup_button.clicked.connect(self.register_student)
        self.password_input.setEchoMode(QLineEdit.Password) # to make the password hidden

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
            add_student(student_id, name, mobile, email, gpa, specialization, locations, skills)
            QMessageBox.information(self, "Success", "Student registered successfully")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))


        if name == "__main__":
            app = QApplication(sys.argv)
            window = StudentSignup()
            window.show()
            sys.exit(app.exec_()) 