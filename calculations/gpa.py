from math import isfinite


GRADING_SCALE = [
    (90, "O", 10),
    (80, "A+", 9),
    (70, "A", 8),
    (60, "B+", 7),
    (50, "B", 6),
    (40, "C", 5),
    (0, "F", 0)
]


def validate_scale(scale):
    if not scale:
        raise ValueError("Add at least one grade band.")
    cleaned = []
    for minimum, grade, points in scale:
        minimum, points = float(minimum), float(points)
        grade = str(grade).strip()
        if not 0 <= minimum <= 100 or not isfinite(points) or not 0 <= points <= 100 or not grade:
            raise ValueError("Use percentages and points between 0 and 100, and a grade name.")
        cleaned.append((minimum, grade, points))
    cleaned.sort(reverse=True)
    if cleaned[-1][0] != 0 or len({row[0] for row in cleaned}) != len(cleaned):
        raise ValueError("Include a 0% band and use different percentage cutoffs.")
    if any(a[2] < b[2] for a, b in zip(cleaned, cleaned[1:])):
        raise ValueError("Higher percentage bands cannot have fewer points.")
    return cleaned


def percentage_to_grade(percentage, scale=None):
    if not 0 <= percentage <= 100:
        raise ValueError("Percentage must be between 0 and 100.")

    for minimum, grade, points in validate_scale(GRADING_SCALE if scale is None else scale):
        if percentage >= minimum:
            return grade, points


def calculate_gpa(subjects, scale=None):
    total_points = 0
    total_credits = 0

    for subject in subjects:
        if not subject.get("is_cgpa_counted", True):
            continue
        credits = float(subject["credits"])
        percentage = float(subject["percentage"])

        if not isfinite(credits) or credits <= 0:
            raise ValueError("Credits must be greater than zero.")

        grade, points = percentage_to_grade(percentage, scale)

        total_points += points * credits
        total_credits += credits

    if total_credits == 0:
        return None

    return round(total_points / total_credits, 2)

def semester_summary(subjects, target=80, pending_score=80, scale=None):
    from calculations.weighted_average import calculate_required_marks

    results = {}
    final_subjects = []
    projected_subjects = []
    maximum_subjects = []
    counted_subjects = [s for s in subjects if s.get("is_cgpa_counted", True)]
    for subject in subjects:
        if not subject.get("is_cgpa_counted", True):
            results[str(subject["id"])] = {
                "status": "excluded", "percentage": None, "grade": "Pass", "points": 10,
                "final": True, "target": None, "required_marks": None,
                "maximum_possible": None,
            }
            continue
        try:
            result = calculate_required_marks(subject["assessments"], subject.get("target", target))
        except ValueError as error:
            raise ValueError(f"{subject['name']}: {error}") from error
        assessments = subject["assessments"]
        final = not any(a["score"] is None and a["weight"] > 0 for a in assessments)
        percentage = sum(a["weight"] * (pending_score if a["score"] is None else a["score"]) / 100
                         for a in assessments)
        grade, points = percentage_to_grade(percentage, scale)
        result.update(percentage=round(percentage, 2), grade=grade, points=points, final=final)
        results[str(subject["id"])] = result
        projected_subjects.append({"credits": subject["credits"], "percentage": percentage})
        maximum = sum(a["weight"] * (100 if a["score"] is None else a["score"]) / 100
                      for a in assessments)
        maximum_subjects.append({"credits": subject["credits"], "percentage": maximum})
        if final:
            final_subjects.append({"credits": subject["credits"], "percentage": percentage})
    return {
        "results": results,
        "gpa": calculate_gpa(final_subjects, scale),
        "projected_gpa": calculate_gpa(projected_subjects, scale),
        "maximum_gpa": calculate_gpa(maximum_subjects, scale),
        "complete": bool(counted_subjects) and len(final_subjects) == len(counted_subjects),
    }
