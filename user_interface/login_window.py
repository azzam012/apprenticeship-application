import sys
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi

class LoginDialog(QDialog):
    def __init__(self):
        super(LoginDialog, self).__init__()
        loadUi("user_interface/login.ui", self)  # the location of login window in qt designer

app = QApplication(sys.argv)
window = LoginDialog()
window.show()
sys.exit(app.exec_())