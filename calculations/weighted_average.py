from math import isfinite


def parse_score(value):
    value = value.strip()
    if not value:
        return None
    try:
        if "/" in value:
            earned, total = (float(part.strip()) for part in value.split("/"))
            if not isfinite(earned) or not isfinite(total) or total <= 0 or not 0 <= earned <= total:
                raise ValueError
            return earned / total * 100
        score = float(value)
        if not isfinite(score) or not 0 <= score <= 100:
            raise ValueError
        return score
    except ValueError:
        raise ValueError("Enter a percentage from 0 to 100 or marks like 14/20. Total marks must be positive and earned marks cannot exceed the total.") from None


def calculate_required_marks(assessments, target):

    if not 0 <= target <= 100:
        raise ValueError("Target must be between 0 and 100.")

    if not assessments:
        raise ValueError("At least one assessment is required.")

    total_weight = 0
    completed_score = 0
    remaining_weight = 0

    for assessment in assessments:

        weight = float(assessment["weight"])
        score = assessment["score"]

        if not 0 <= weight <= 100:
            raise ValueError("Assessment weight must be between 0 and 100.")

        total_weight += weight

        if score is None:
            remaining_weight += weight

        else:
            score = float(score)

            if not 0 <= score <= 100:
                raise ValueError("Assessment score must be between 0 and 100.")

            completed_score += (score * weight) / 100

    if abs(total_weight - 100) > 0.01:
        raise ValueError("Assessment weights must total 100%.")

    maximum_possible = completed_score + remaining_weight

    if completed_score >= target:

        status = "achieved"
        required_marks = 0

    elif maximum_possible < target:

        status = "impossible"
        required_marks = None

    elif remaining_weight == 0:

        status = "impossible"
        required_marks = None

    else:

        status = "possible"

        required_marks = (
            (target - completed_score) / (remaining_weight / 100))

    return {
        "status": status,
        "target": round(target, 2),
        "completed_contribution": round(completed_score, 2),
        "remaining_weight": round(remaining_weight, 2),
        "maximum_possible": round(maximum_possible, 2),
        "required_marks": (
            round(required_marks, 2)
            if required_marks is not None
            else None
        )
    }