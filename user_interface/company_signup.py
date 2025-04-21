import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox, QLineEdit
from PyQt5.uic import loadUi
from models.company import add_opening

class CompanySignup(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("user_interface/company_signup.ui", self)
        
        self.signup_button.clicked.connect(self.register_company)
        self.password_input.setEchoMode(QLineEdit.Password) # to make the password hidden

    def register_company(self):
        company_name = self.company_name_input.text()
        company_email = self.email_input.text()
        company_password = self.password_input.text()
        

        if not all([company_name, company_email, company_password]):
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
        
        #try:
            # add_company(company_name, company_email, company_password)
            #QMessageBox.information(self, "Success", "Company registered successfully")
            #self.close()
        #except Exception as e:
            #QMessageBox.critical(self, "Database Error", str(e))

        if company_name == "__main__":
            app = QApplication(sys.argv)
            window = CompanySignup()
            window.show()
            sys.exit(app.exec_())




