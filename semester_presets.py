SCHEMAS = {
    "THEORY": [("CIA 1", 10), ("CIA 2", 10), ("Mid-Semester Exam", 30),
               ("End-Semester Exam", 50)],
    "TCP": [("CIA 1 & CIA 2 (Combined)", 10), ("Mid-Semester Exam (Theory)", 20),
            ("End-Semester Exam (Practical)", 30), ("End-Semester Exam (Theory)", 40)],
    "PRACTICAL": [("Internal Continuous Assessments", 80), ("End-Semester Exam", 20)],
    "EAA": [],
}

COURSES = [
    ("Mathematics I", 4, "THEORY"),
    ("Electrical and Electronics Essentials for IT", 2, "THEORY"),
    ("Communicative English", 3, "TCP"),
    ("Computational Thinking and Problem Solving with Python", 3, "TCP"),
    ("Introduction to Web Programming", 3, "TCP"),
    ("Professional Ethics and Human Values", 2, "THEORY"),
    ("Open-Source Tools and Prompt Engineering", 2, "PRACTICAL"),
    ("Extra Academic Activity 1", 1, "EAA"),
    ("Introduction to ARVR", 2, "PRACTICAL"),
]


def add_semester_one(subjects):
    subjects = list(subjects)
    next_id = max((s["id"] for s in subjects), default=0) + 1
    added = 0
    for index, (name, credits, schema) in enumerate(COURSES, start=1):
        key = f"snu-it-sem1-{index}"
        if any(s.get("preset_key") == key or s["name"].strip().casefold() == name.casefold()
               for s in subjects):
            continue
        subjects.append({
            "id": next_id, "name": name, "credits": credits,
            "preset_key": key, "schema": schema, "is_cgpa_counted": schema != "EAA",
            "assessments": [{"id": i, "name": title, "weight": weight, "score": None}
                            for i, (title, weight) in enumerate(SCHEMAS[schema], start=1)],
        })
        next_id += 1
        added += 1
    return subjects, added
