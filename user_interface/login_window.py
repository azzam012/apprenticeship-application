import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QLineEdit
from PyQt5.uic import loadUi

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("user_interface/login.ui", self)  # the location of login window in Qt Designer
        self.setFixedSize(self.size())

        self.student_login_button.clicked.connect(self.login_as_student)
        self.company_login_button.clicked.connect(self.login_as_company)
        self.password_input.setEchoMode(QLineEdit.Password) # to make the password hidden
    
    def login_as_student(self): # method 1: if the user is student
        self.handle_login('student')
        print('student')
    
    def login_as_company(self): # method 2: if the user is company
        self.handle_login('company')
        print('company')

    def handle_login(self , user_typ): # method 3: to save info in the db
        email = self.email_input.text()
        password = self.password_input.text()
        print(email,password)
        
        #confirming that the user does not forgot to type in the email and password
        if not email or not password:
            QMessageBox.warning(self,"Error!"," you may forgit to type in the email ro the password")









app = QApplication(sys.argv)
window = LoginDialog()
window.show()
sys.exit(app.exec_())



