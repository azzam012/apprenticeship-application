    try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT opening_id, specialization, location, stipend, required_skills
                FROM openings
                WHERE company_name = ?
            """, (self.current_company_name,))
            openings = cursor.fetchall()
            conn.close()

            headers = ["ID", "Specialization", "Location", "Stipend", "Skills"]
            self.company_openings_table.setColumnCount(len(headers))
            self.company_openings_table.setRowCount(len(openings))
            self.company_openings_table.setHorizontalHeaderLabels(headers)

            for row_index, row_data in enumerate(openings):
                for col_index, value in enumerate(row_data):
                    self.company_openings_table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

            self.company_openings_table.resizeColumnsToContents()
            self.company_openings_table.horizontalHeader().setStretchLastSection(True)
            self.company_openings_table.verticalHeader().setVisible(False)
            self.company_openings_table.horizontalHeader().setVisible(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load openings: {str(e)}")