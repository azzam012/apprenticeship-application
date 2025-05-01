import sqlite3

class MatchingSystem:
    def __init__(self, db_name='apprenticeship.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def fetch_students(self):
        self.cursor.execute("SELECT student_id, name, gpa, specialization, preferred_locations FROM students")
        return self.cursor.fetchall()

    def fetch_openings(self):
        self.cursor.execute("SELECT opening_id, specialization, location, stipend FROM openings")
        return self.cursor.fetchall()

    def match_students(self):
        students = self.fetch_students()
        openings = self.fetch_openings()
        matches = []

        for student in students:
            student_id, name, gpa, spec, pref_locations = student
            preferred_locations = [loc.strip() for loc in pref_locations.split(",")]

            matching_openings = [op for op in openings if op[1] == spec and op[2] in preferred_locations]

            if matching_openings:
                matching_openings.sort(key=lambda op: preferred_locations.index(op[2]))
                best_opening = matching_openings[0]
                matches.append((name, gpa, best_opening[0], best_opening[2], best_opening[3]))
            else:
                print(f"No match found for {name}.")

        return matches

    def display_matches(self, matches):
        print("Student Name | GPA | Opening ID | Location | Stipend")
        for match in matches:
            print(f"{match[0]} | {match[1]} | {match[2]} | {match[3]} | {match[4]}")

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    system = MatchingSystem()
    matches = system.match_students()
    system.display_matches(matches)
    system.close()
