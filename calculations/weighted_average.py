def calculate_required_marks(assessments, target):

    completed_score = 0
    remaining_weight = 0

    for assessment in assessments:

        weight = assessment["weight"]
        score = assessment["score"]

        if score is None:
            remaining_weight += weight / 100

        else:
            completed_score += (score * weight) / 100

    if completed_score >= target:
        return {
        "status": "achieved",
        "required_marks": 0
    }

    if remaining_weight == 0:

        if completed_score >= target:
            return {
                "status": "achieved",
                "required_marks": 0
            }

        return {
            "status": "impossible",
            "required_marks": None
        }

    required = (target - completed_score) / remaining_weight

    if required > 100:
        return {
            "status": "impossible",
            "required_marks": required
        }

    if required <= 0:
        return {
            "status": "achieved",
            "required_marks": 0
        }

    return {
        "status": "possible",
        "required_marks": round(required, 2)
    }