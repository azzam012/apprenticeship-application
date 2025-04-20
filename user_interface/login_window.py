import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QLineEdit
from PyQt5.uic import loadUi
from student_signup import StudentSignup
#from company_signup import CompanySignupDialog



class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("user_interface/login.ui", self)  # the location of login window in Qt Designer
        #self.setFixedSize(self.size())
        self.showMaximized()

        self.login_button.clicked.connect(self.handle_login)

        self.student_signup_button.clicked.connect(self.open_student_signup)
        #self.company_signup_button.clicked.connect(self.open_company_signup)
        self.password_input.setEchoMode(QLineEdit.Password) # to make the password hidden
    

    def handle_login(self): # method 3: to save info in the db
        email = self.email_input.text()
        password = self.password_input.text()
        
        
        #confirming that the user does not forgot to type in the email and password
        if not email or not password:
            QMessageBox.warning(self,"Error!"," you may forgit to type in the email ro the password")
            return
        
        if self.student_radio.isChecked():
            print('Logging in as student')
        elif self.company_radio.isChecked():
            print('Logging in as company')
        else:
            QMessageBox.warning(self,'Error!','Please select your user type.')

    def open_student_signup(self):
        self.student_signup_window = StudentSignup()
        self.student_signup_window.exec_()

    #def open_company_signup(self):
        #self.company_signup_window = CompanySignupDialog()
       # self.company_signup_window.exec_()









app = QApplication(sys.argv)
window = LoginDialog()
window.show()
sys.exit(app.exec_())



