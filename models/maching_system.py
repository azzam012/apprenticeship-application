import sqlite3
from models.student import view_students
from models.company import view_openings

class MatchingSystem:
    def __init__(self):
        self.matches = []

    def match_students_to_openings(self, weighted=False, gpa_weight=0.6, location_weight=0.4):
        students = view_students()
        openings = view_openings()

        if not students or not openings:
            return "No data available", []

        for student in students:
            student_id, name, mobile, email, gpa, spec, preferred_locations, skills = student
            location_list = [loc.strip() for loc in preferred_locations.split(',')]

            relevant_openings = [op for op in openings if op[1] == spec]
            student_matches = []

            for priority, loc in enumerate(location_list):
                for opening in relevant_openings:
                    opening_id, o_spec, o_loc, stipend, req_skills = opening
                    if o_loc == loc:
                        if weighted:
                            score = (gpa * gpa_weight) + ((3 - priority) * location_weight)
                        else:
                            score = None
                        student_matches.append({
                            "student_name": name,
                            "gpa": gpa,
                            "opening_id": opening_id,
                            "location": o_loc,
                            "stipend": stipend,
                            "priority": priority,
                            "score": score
                        })

            if student_matches:
                if weighted:
                    best_match = sorted(student_matches, key=lambda m: -m['score'])[0]
                else:
                    best_match = sorted(student_matches, key=lambda m: (m['priority'], -m['gpa']))[0]
                self.matches.append(best_match)
            else:
                self.matches.append({
                    "student_name": name,
                    "gpa": gpa,
                    "opening_id": "N/A",
                    "location": "N/A",
                    "stipend": "N/A",
                    "priority": 99,
                    "message": "No openings match your criteria"
                })

        return "success", self.matches

    def display_matches(self):
        print("Student Name | GPA | Opening ID | Location | Stipend")
        for match in self.matches:
            print(f"{match['student_name']} | {match['gpa']} | {match['opening_id']} | {match['location']} | {match['stipend']}")

if __name__ == "__main__":
    matcher = MatchingSystem()
    status, matches = matcher.match_students_to_openings(weighted=True)  # Set to False if you don't want weighted logic
    if status == "success":
        matcher.display_matches()
    else:
        print(status)
