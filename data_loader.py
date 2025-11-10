import csv
from tkinter import messagebox

def load_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_all_data():
    teachers_data = load_csv("data/teachers.csv")
    classes_data = load_csv("data/classes.csv")
    subjects_data = load_csv("data/subjects.csv")
    rooms_data = load_csv("data/rooms.csv")
    timeslots_data = load_csv("data/timeslots.csv")

    teachers = {
        t["TeacherID"]: {
            "name": t.get("TeacherName", t["TeacherID"]),
            "subjects": t["Subjects"].split("|"),
            "available": t["AvailableSlots"].split("|")
        }
        for t in teachers_data
    }

    classes = {
        c["ClassID"]: {
            "name": c.get("ClassName", c["ClassID"]),
            "students": int(c["Students"]),
            "subjects": c["Subjects"].split("|")
        }
        for c in classes_data
    }

    subjects = {
        s["SubjectName"]: {
            "type": s["SubjectType"],
            "name": s.get("SubjectDisplayName", s["SubjectName"])
        }
        for s in subjects_data
    }

    rooms = {
        r["RoomID"]: {"capacity": int(r["Capacity"]), "type": r["RoomType"]}
        for r in rooms_data
    }

    timeslots = [t["SlotID"] for t in timeslots_data]

    # 🔹 Trả thêm mapping tên
    teacher_names = {t["TeacherID"]: t.get("TeacherName", t["TeacherID"]) for t in teachers_data}
    class_names = {c["ClassID"]: c.get("ClassName", c["ClassID"]) for c in classes_data}
    subject_names = {s["SubjectName"]: s.get("SubjectDisplayName", s["SubjectName"]) for s in subjects_data}

    return teachers, classes, subjects, rooms, timeslots, teacher_names, class_names, subject_names
