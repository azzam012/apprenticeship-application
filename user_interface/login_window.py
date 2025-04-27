import sys , os
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from user_interface.student_signup import StudentSignup
from user_interface.company_signup import CompanySignup


from user_interface.student_dashboard import StudentDashboard
from models.student import get_student_by_email_and_password
#from user_interface.company_dashboard import CompanyDashboard
#from user_interface.student_signup import StudentSignup
#from user_interface.company_signup import CompanySignup



class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'login.ui')
        loadUi(ui_path, self)
        #loadUi("user_interface/login.ui", self)  # the location of login window in Qt Designer
        #self.setFixedSize(self.size())
        #self.showMaximized()

        self.login_button.clicked.connect(self.handle_login)

        self.student_signup_button.clicked.connect(self.open_student_signup)
        self.company_signup_button.clicked.connect(self.open_company_signup)
        self.password_input.setEchoMode(QLineEdit.Password) # to make the password hidden
    

    def handle_login(self): # method 3: to save info in the db
        email = self.email_input.text()
        password = self.password_input.text()
        
        
        #confirming that the user does not forgot to type in the email and password
        if not email or not password:
            QMessageBox.warning(self,"Error!"," you may forgit to type in the email ro the password")
            return
        
        if self.student_radio.isChecked():
             student = get_student_by_email_and_password(email, password)
            
             if student:
                self.close()
                self.dashboard_window = StudentDashboard(student_id=student[0])
                self.dashboard_window.show()
             else:
                QMessageBox.warning(self, "Error", "Invalid email or password")
    
        #elif self.company_radio.isChecked():
        #    self.dashboard = CompanyDashboard()
         #   self.dashboard.show()
        #    self.close()
        else:
            QMessageBox.warning(self,'Error!','Please select your user type.')

    def open_student_signup(self):
        self.student_signup_window = StudentSignup()
        self.student_signup_window.exec_()

    def open_company_signup(self):
        self.company_signup_window = CompanySignup()
        self.company_signup_window.exec_()










app = QApplication(sys.argv)
window = LoginDialog()
window.show()
sys.exit(app.exec_())



