import pytest

from calculations.gpa import percentage_to_grade, calculate_gpa


def test_percentage_to_grade():
    assert percentage_to_grade(95) == ("O", 10)
    assert percentage_to_grade(85) == ("A+", 9)
    assert percentage_to_grade(45) == ("C", 5)
    assert percentage_to_grade(30) == ("F", 0)


def test_invalid_percentage():
    with pytest.raises(ValueError):
        percentage_to_grade(110)


def test_calculate_gpa():
    subjects = [
        {"credits": 4, "percentage": 95},
        {"credits": 3, "percentage": 85},
        {"credits": 3, "percentage": 75}
    ]

    # (4 × 10 + 3 × 9 + 3 × 8) / 10
    assert calculate_gpa(subjects) == 9.1


def test_invalid_credits():
    subjects = [
        {"credits": 0, "percentage": 90}
    ]

    with pytest.raises(ValueError):
        calculate_gpa(subjects)


def test_empty_subjects():
    assert calculate_gpa([]) is None

@pytest.mark.parametrize("credits", [float("nan"), float("inf"), -1])
def test_nonfinite_or_negative_credits(credits):
    with pytest.raises(ValueError):
        calculate_gpa([{"credits": credits, "percentage": 90}])
