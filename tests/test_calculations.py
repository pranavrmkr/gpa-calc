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

@pytest.mark.parametrize("value,expected", [
    ("14/20", 70), (" 14 / 20 ", 70), ("14.5/20", 72.5),
    ("0/20", 0), ("20/20", 100), ("70", 70), ("0", 0), ("", None), (" ", None),
])
def test_parse_score(value, expected):
    from calculations.weighted_average import parse_score
    assert parse_score(value) == expected


@pytest.mark.parametrize("value", ["14/0", "-1/20", "21/20", "14/-20", "1/2/3",
                                   "14/", "/20", "abc", "nan", "inf", "nan/20",
                                   "14/inf", "101", "-1", "inf/inf"])
def test_invalid_marks(value):
    from calculations.weighted_average import parse_score
    with pytest.raises(ValueError, match="Enter a percentage"):
        parse_score(value)
