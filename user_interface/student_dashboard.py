import sys, os
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi



class StudentDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_file = os.path.join(os.path.dirname(__file__), "student_dashboard.ui")
        loadUi(ui_file, self)

        self.student_tabWidget.tabBar().setVisible(False) # to hide the tab widget, and use buttons to use it
        self.handel_student_buttons()
        


    def handel_student_buttons(self):
        self.student_info_button.clicked.connect(self.open_info_tab)
        self.student_applications_button.clicked.connect(self.open_applications_tab)
        self.student_oppourtunities_button.clicked.connect(self.open_oppourtunities_tab)
        self.student_logout_button.clicked.connect(self.logout)



    def open_info_tab(self):
        self.student_tabWidget.setCurrentIndex(0)
    
    def open_applications_tab(self):
        self.student_tabWidget.setCurrentIndex(1)
    
    def open_oppourtunities_tab(self):
        self.student_tabWidget.setCurrentIndex(2)
    
    def logout(self):
        QApplication.quit()





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentDashboard()
    window.show()
    sys.exit(app.exec_())


