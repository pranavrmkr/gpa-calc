GRADING_SCALE = [
    (90, "O", 10),
    (80, "A+", 9),
    (70, "A", 8),
    (60, "B+", 7),
    (50, "B", 6),
    (40, "C", 5),
    (0, "F", 0)
]


def percentage_to_grade(percentage):
    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100.")

    for minimum, grade, points in GRADING_SCALE:
        if percentage >= minimum:
            return grade, points


def calculate_gpa(subjects):
    total_points = 0
    total_credits = 0

    for subject in subjects:
        credits = float(subject["credits"])
        percentage = float(subject["percentage"])

        if credits <= 0:
            raise ValueError("Credits must be greater than zero.")

        grade, points = percentage_to_grade(percentage)

        total_points += points * credits
        total_credits += credits

    if total_credits == 0:
        return None

    return round(total_points / total_credits, 2)