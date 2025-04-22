import sys, os
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

class StudentDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_file = os.path.join(os.path.dirname(__file__), "student_dashboard.ui")
        loadUi(ui_file, self)

        self.student_info_button.clicked.connect(self.open_info_tab)

    def open_info_tab(self):
        self.student_tabWidget.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentDashboard()
    window.show()
    sys.exit(app.exec_())