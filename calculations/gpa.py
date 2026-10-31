GRADING_SCALE = [
    (90, "O", 10),
    (80, "A+", 9),
    (70, "A", 8),
    (60, "B+", 7),
    (50, "B", 6),
    (40, "C", 5),
    (0, "F", 0)
]


def percentage_to_grade(percentage, scale=GRADING_SCALE):

    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100")

    for minimum, grade, points in scale:
        if percentage >= minimum:
            return grade


def percentage_to_points(percentage, scale=GRADING_SCALE):

    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100")

    for minimum, grade, points in scale:
        if percentage >= minimum:
            return points


def calculate_gpa(subjects):

    total_weighted_points = 0
    total_credits = 0

    for subject in subjects:

        credits = subject["credits"]
        points = subject["grade_points"]

        if credits <= 0:
            raise ValueError("Credits must be positive")

        if not 0 <= points <= 10:
            raise ValueError("Grade points must be between 0 and 10")

        total_weighted_points += credits * points
        total_credits += credits

    if total_credits == 0:
        return None

    return round(total_weighted_points / total_credits, 2)