import sys
from PyQt5.QtWidgets import QApplication
from user_interface.login_window import LoginDialog

def main():
    app = QApplication(sys.argv)

    login_window = LoginDialog()
    login_window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
