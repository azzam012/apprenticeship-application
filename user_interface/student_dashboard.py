import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from models.student import *


class StudentDashboard(QMainWindow):
    def __init__(self , student_id):
        super().__init__()
        ui_file = os.path.join(os.path.dirname(__file__), "student_dashboard.ui")
        loadUi(ui_file, self)

        self.current_student_id = student_id 
        self.student_tabWidget.tabBar().setVisible(False)
        self.handle_student_buttons()

    def handle_student_buttons(self):
        self.student_info_button.clicked.connect(self.open_info_tab)
        self.student_applications_button.clicked.connect(self.open_applications_tab)
        self.student_oppourtunities_button.clicked.connect(self.open_oppourtunities_tab)
        self.student_logout_button.clicked.connect(self.logout)

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
        # نجهز اسماء الحقول بالترتيب
        headers = [
            "Student ID", "Name", "Mobile Number", "Email", "GPA",
            "Specialization", "Preferred Locations", "Skills"
        ]

        self.student_info_table.clear()  # تنظيف الجدول قبل كل تحميل
        self.student_info_table.setRowCount(len(headers))
        self.student_info_table.setColumnCount(2)
        self.student_info_table.setHorizontalHeaderLabels(["Field", "Value"])

        # نعبي كل صف
        for row, (field, value) in enumerate(zip(headers, student_info)):
            self.student_info_table.setItem(row, 0, QTableWidgetItem(field))
            self.student_info_table.setItem(row, 1, QTableWidgetItem(str(value)))

        # تحسينات شكل الجدول
        self.student_info_table.resizeColumnsToContents()
        self.student_info_table.horizontalHeader().setStretchLastSection(True)
        self.student_info_table.verticalHeader().setVisible(False)
        self.student_info_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    else:
        QMessageBox.warning(self, "Error", "Could not load student information.")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentDashboard()
    window.show()
    sys.exit(app.exec_())
