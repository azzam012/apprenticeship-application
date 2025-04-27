    def load_student_info(self):
        student_info = get_student_info(self.current_student_id)

        if student_info:
            headers = [
                "Student ID", "Name", "Mobile", "Email", "GPA",
                "Specialization", "Preferred Locations", "Skills"
            ]

            # عدد الأعمدة سيكون 1 (لأننا نعرض البيانات في عمود واحد)
            self.student_info_table.setColumnCount(1)
            self.student_info_table.setRowCount(len(headers))  # عدد الصفوف سيكون عدد الحقول

            # تعبئة الجدول بالعناوين والقيم
            for row, (header, value) in enumerate(zip(headers, student_info)):
                self.student_info_table.setItem(row, 0, QTableWidgetItem(str(value)))  # القيمة ستكون في العمود الأول
                # إذا أردت العناوين في العمود الأول مع القيم في العمود الثاني
                # self.student_info_table.setItem(row, 1, QTableWidgetItem(str(header)))

            # تحسينات على شكل الجدول
            self.student_info_table.horizontalHeader().setStretchLastSection(True)
            self.student_info_table.verticalHeader().setVisible(False)  # إخفاء رؤوس الأعمدة
            self.student_info_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # منع التعديل
        else:
            QMessageBox.warning(self, "Error", "Failed to load student information.")
