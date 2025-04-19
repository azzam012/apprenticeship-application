import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt5.uic import loadUi

class LoginDialog(QDialog):
    def __init__(self):
        super(LoginDialog, self).__init__()
        loadUi("user_interface/login.ui", self)  # the location of login window in Qt Designer
        self.student_login_button.clicked.connect(self.login_as_student)
        self.company_login_button.cliked.connect(self.login_as_company)

    def login_as_student(self):
        self.handel_login('student')
        print('student')
    
    def login_as_company(self):
        self.handel_login('company')
        print('company')

    def handle_login(self , user_typ):
        email = self.email_input.text()
        password = self.password_input.text()
        
        #confirming that the user does not forgot to type the email and password
        if not email or not password:
            QMessageBox.warning("Error! you forgot to type the email ro the password")








app = QApplication(sys.argv)
window = LoginDialog()
window.show()
sys.exit(app.exec_())



