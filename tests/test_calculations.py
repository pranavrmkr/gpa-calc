import pytest

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
    assert result["completed_contribution"] == 29
    assert result["maximum_possible"] == 89


def test_already_achieved():

    assessments = [
        {"weight": 50, "score": 90},
        {"weight": 50, "score": 100}
    ]

    result = calculate_required_marks(assessments, 80)

    assert result["status"] == "achieved"


def test_impossible_target():

    assessments = [
        {"weight": 50, "score": 20},
        {"weight": 50, "score": None}
    ]

    result = calculate_required_marks(assessments, 80)

    assert result["status"] == "impossible"


def test_invalid_weights():

    assessments = [
        {"weight": 40, "score": 80},
        {"weight": 40, "score": None}
    ]

    with pytest.raises(ValueError):
        calculate_required_marks(assessments, 80)


def test_invalid_score():

    assessments = [
        {"weight": 50, "score": 110},
        {"weight": 50, "score": None}
    ]

    with pytest.raises(ValueError):
        calculate_required_marks(assessments, 80)


def test_invalid_target():

    with pytest.raises(ValueError):
        calculate_required_marks([], 110)