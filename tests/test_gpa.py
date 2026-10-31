import pytest

from calculations.gpa import (
    percentage_to_grade,
    percentage_to_points,
    calculate_gpa
)


def test_grade_conversion():
    assert percentage_to_grade(95) == "O"
    assert percentage_to_grade(84) == "A+"
    assert percentage_to_grade(35) == "F"


def test_grade_points():
    assert percentage_to_points(95) == 10
    assert percentage_to_points(75) == 8
    assert percentage_to_points(35) == 0


def test_calculate_gpa():

    subjects = [
        {"credits": 4, "grade_points": 10},
        {"credits": 3, "grade_points": 9},
        {"credits": 4, "grade_points": 8}
    ]

    assert calculate_gpa(subjects) == 9.0


def test_empty_subjects():
    assert calculate_gpa([]) is None


def test_invalid_percentage():
    with pytest.raises(ValueError):
        percentage_to_points(110)