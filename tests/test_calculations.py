from calculations.weighted_average import calculate_required_marks


def test_required_marks():

    assessments = [
        {"weight": 10, "score": 80},
        {"weight": 30, "score": 70},
        {"weight": 60, "score": None}
    ]

    result = calculate_required_marks(assessments, 80)

    assert result["status"] == "possible"
    assert result["required_marks"] == 85

def test_target_already_achieved():

    assessments = [
        {"weight": 50, "score": 90},
        {"weight": 50, "score": 100}
    ]

    result = calculate_required_marks(assessments, 80)

    assert result["status"] == "achieved"


def test_target_impossible():

    assessments = [
        {"weight": 50, "score": 20},
        {"weight": 50, "score": None}
    ]

    result = calculate_required_marks(assessments, 80)

    assert result["status"] == "impossible"