import pytest
from calculations.gpa import validate_scale, semester_summary, percentage_to_grade


@pytest.mark.parametrize("scale", [[], [(10, "A", 4)], [(0, "F", 0), (0, "A", 4)],
                                   [(0, "F", 4), (90, "A", 0)], [(0, "F", float("nan"))]])
def test_invalid_scale(scale):
    with pytest.raises(ValueError):
        validate_scale(scale)


def test_custom_scale():
    assert percentage_to_grade(75, [(0, "F", 0), (70, "Pass", 4)]) == ("Pass", 4)


def test_summary_separates_final_and_projected():
    subjects = [{"id": 1, "name": "Math", "credits": 4,
                 "assessments": [{"weight": 100, "score": 95}]},
                {"id": 2, "name": "Physics", "credits": 4,
                 "assessments": [{"weight": 50, "score": 60}, {"weight": 50, "score": None}]}]
    summary = semester_summary(subjects, pending_score=80)
    assert summary["gpa"] == 10
    assert summary["projected_gpa"] == 9
    assert summary["maximum_gpa"] == 9.5
    assert not summary["complete"]
    assert summary["results"]["2"]["percentage"] == 70


def test_zero_weight_pending_does_not_block_final():
    summary = semester_summary([{"id": 1, "name": "Math", "credits": 4,
                                "assessments": [{"weight": 100, "score": 80},
                                                {"weight": 0, "score": None}]}])
    assert summary["complete"]
    assert summary["gpa"] == 9


def test_eaa_is_excluded_from_every_gpa():
    from calculations.gpa import calculate_gpa
    from semester_presets import add_semester_one
    subjects, _ = add_semester_one([])
    for subject in subjects:
        for assessment in subject["assessments"]:
            assessment["score"] = 0
    summary = semester_summary(subjects)
    assert summary["complete"]
    assert summary["gpa"] == summary["projected_gpa"] == summary["maximum_gpa"] == 0
    assert summary["results"]["8"]["points"] == 10
    assert calculate_gpa([{"credits": 4, "percentage": 0},
                          {"credits": 1, "is_cgpa_counted": False}]) == 0


def test_eaa_alone_has_no_semester_gpa():
    summary = semester_summary([{"id": 1, "is_cgpa_counted": False}])
    assert summary["gpa"] is None
    assert summary["projected_gpa"] is None
    assert not summary["complete"]
