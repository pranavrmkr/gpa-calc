import pytest

from app import app


@pytest.fixture
def client(tmp_path):
    app.config.update(TESTING=True, CSRF_ENABLED=False, SECRET_KEY="test-key", DATABASE=str(tmp_path / "test.sqlite3"))
    with app.test_client() as client:
        yield client


def seed_subject(client):
    with client.session_transaction() as session:
        session["subjects"] = [{
            "id": 1, "name": "Math", "credits": 4,
            "assessments": [
                {"id": 1, "name": "Quiz", "weight": 40, "score": 75},
                {"id": 2, "name": "Final", "weight": 60, "score": None},
            ],
        }]


def test_calculate_displays_and_keeps_results(client):
    seed_subject(client)
    response = client.post("/calculate", follow_redirects=True)
    assert response.status_code == 200
    assert b"83.33%" in response.data
    with client.session_transaction() as session:
        assert session["results"]["1"]["completed_contribution"] == 30
    assert b"83.33%" in client.get("/").data


@pytest.mark.parametrize("data", [
    {"subject": "", "credits": "4"},
    {"subject": "Math", "credits": "0"},
    {"subject": "Math", "credits": "nan"},
    {"subject": "Math", "credits": "inf"},
    {"subject": "Math"},
])
def test_invalid_subject_shows_error(client, data):
    response = client.post("/add-subject", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"error-card" in response.data
    with client.session_transaction() as session:
        assert not session.get("subjects")


def test_stylesheet_is_served(client):
    response = client.get("/static/css/style.css")
    assert response.status_code == 200
    assert b".assessment-form" in response.data


@pytest.mark.parametrize("path,data", [
    ("/add-assessment/1", {"assessment": "Project"}),
    ("/delete-assessment/1/1", {}),
    ("/update-assessment/1/1", {"weight": "40", "score": "85"}),
    ("/set-target", {"target": "90"}),
    ("/add-subject", {"subject": "Physics", "credits": "3"}),
    ("/delete-subject/1", {}),
])
def test_changes_clear_old_results(client, path, data):
    seed_subject(client)
    client.post("/calculate")
    client.post(path, data=data)
    with client.session_transaction() as session:
        assert "results" not in session


def test_invalid_calculation_clears_old_results(client):
    seed_subject(client)
    client.post("/calculate")
    with client.session_transaction() as session:
        session["subjects"][0]["assessments"][0]["weight"] = 10
        session.modified = True
    response = client.post("/calculate", follow_redirects=True)
    assert b"weights must total 100%" in response.data
    with client.session_transaction() as session:
        assert "results" not in session


def test_blank_assessment_shows_error(client):
    seed_subject(client)
    response = client.post("/add-assessment/1", data={"assessment": " "},
                           follow_redirects=True)
    assert b"Assessment name is required." in response.data


def test_clear_removes_data(client):
    seed_subject(client)
    client.post("/calculate")
    client.post("/clear")
    with client.session_transaction() as session:
        assert not session


def test_custom_settings_and_projection(client):
    seed_subject(client)
    response = client.post("/settings", data={"pending_score": "100", "target_gpa": "4",
                           "scale": "70, Pass, 4\n0, Fail, 0"}, follow_redirects=True)
    assert response.status_code == 200
    response = client.post("/calculate", follow_redirects=True)
    assert b"Projected semester GPA: 4.0" in response.data
    assert b"Grade: Pass" in response.data


@pytest.mark.parametrize("scale", ["bad", "50, A, 4", "0, F, nan"])
def test_invalid_settings_preserve_previous_values(client, scale):
    response = client.post("/settings", data={"pending_score": "80", "target_gpa": "4",
                           "scale": scale}, follow_redirects=True)
    assert b"error-card" in response.data
    with client.session_transaction() as session:
        assert "scale" not in session


def test_edit_subject_and_assessment_names(client):
    seed_subject(client)
    client.post("/update-subject/1", data={"subject": "Algebra", "credits": "3"})
    client.post("/update-assessment/1/1", data={"assessment": "Test", "weight": "40", "score": "90"})
    response = client.get("/")
    assert b"Algebra" in response.data
    assert b"Test" in response.data


def test_saved_data_survives_new_client(client):
    seed_subject(client)
    cookie = client.get_cookie("session")
    with app.test_client() as reopened:
        reopened.set_cookie("session", cookie.value)
        assert b"Math" in reopened.get("/").data
    with app.test_client() as other:
        assert b"Math" not in other.get("/").data


def test_large_semester_uses_small_cookie(client):
    with client.session_transaction() as session:
        session["subjects"] = [{"id": i, "name": "Subject " + str(i), "credits": 4,
                                "assessments": []} for i in range(100)]
    assert len(client.get_cookie("session").value) == 64
    with client.session_transaction() as session:
        assert len(session["subjects"]) == 100


def test_export_matches_calculation(client):
    seed_subject(client)
    response = client.get("/export")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "attachment" in response.headers["Content-Disposition"]
    assert b"Math,4,Projected,78.0,A,8.0,80,83.33,90" in response.data
    assert b"Projected semester GPA,8.0" in response.data


def test_export_checks_invalid_data(client):
    response = client.get("/export", follow_redirects=True)
    assert b"Add subjects before exporting." in response.data


def test_export_escapes_formulas(client):
    seed_subject(client)
    client.post("/update-subject/1", data={"subject": "=1+1", "credits": "4"})
    assert b"'=1+1" in client.get("/export").data



@pytest.mark.parametrize("path", ["/add-assessment/99", "/delete-subject/99",
                                   "/update-assessment/1/99", "/delete-assessment/1/99"])
def test_missing_records_return_404(client, path):
    seed_subject(client)
    assert client.post(path).status_code == 404


def test_csrf_rejects_missing_token_and_accepts_valid_form(client):
    app.config["CSRF_ENABLED"] = True
    try:
        client.get("/")
        assert client.post("/add-subject", data={"subject": "Math", "credits": "4"}).status_code == 400
        with client.session_transaction() as session:
            token = session["csrf_token"]
        response = client.post("/add-subject", data={"subject": "Math", "credits": "4", "csrf_token": token})
        assert response.status_code == 302
    finally:
        app.config["CSRF_ENABLED"] = False


def test_database_reopens_in_new_app(client):
    from flask import Flask, session
    from storage import SQLiteSessions
    seed_subject(client)
    restarted = Flask(__name__)
    restarted.config["DATABASE"] = app.config["DATABASE"]
    restarted.session_interface = SQLiteSessions()

    @restarted.get("/")
    def saved_subject():
        return session["subjects"][0]["name"]

    with restarted.test_client() as reopened:
        reopened.set_cookie("session", client.get_cookie("session").value)
        assert reopened.get("/").data == b"Math"


def test_expired_session_is_not_reused(client):
    import sqlite3
    seed_subject(client)
    with sqlite3.connect(app.config["DATABASE"]) as database:
        database.execute("UPDATE sessions SET expires = 0")
    assert b"Math" not in client.get("/").data


def test_full_workflow(client):
    app.config["CSRF_ENABLED"] = True
    try:
        client.get("/")
        with client.session_transaction() as session:
            token = session["csrf_token"]
        def post(path, **data):
            return client.post(path, data={**data, "csrf_token": token}, follow_redirects=True)
        post("/add-subject", subject="Math", credits="4")
        post("/add-assessment/1", assessment="Exam")
        post("/update-assessment/1/1", assessment="Exam", weight="100", score="95")
        response = post("/calculate")
        assert b"Semester GPA" in response.data
        assert b"Final percentage: 95.0%" in response.data
        assert b"Grade: O" in response.data
        assert client.get("/export").status_code == 200
        post("/clear")
        with client.session_transaction() as session:
            assert "subjects" not in session
    finally:
        app.config["CSRF_ENABLED"] = False


def test_semester_one_loads_courses_and_can_calculate(client):
    response = client.post("/semester-1", follow_redirects=True)
    assert response.status_code == 200
    assert b"+ Semester 1" in response.data
    with client.session_transaction() as session:
        subjects = session["subjects"]
        assert len(subjects) == 8
        assert sum(s["credits"] for s in subjects if s["is_cgpa_counted"]) == 19
        assert [a["weight"] for a in subjects[0]["assessments"]] == [10, 10, 30, 50]
        assert [a["weight"] for a in subjects[2]["assessments"]] == [10, 20, 30, 40]
        assert [a["weight"] for a in subjects[6]["assessments"]] == [80, 20]
        assert subjects[7]["credits"] == 1
        assert not subjects[7]["is_cgpa_counted"]
        assert all(a["score"] is None for s in subjects for a in s["assessments"])
    response = client.post("/calculate", follow_redirects=True)
    assert response.status_code == 200
    assert b"Projected semester GPA: 9.0" in response.data
    assert b"Pass / 10 points / Excluded from GPA" in response.data
    assert b"Extra Academic Activity 1,1,Excluded from GPA,,Pass,10" in client.get("/export").data


def test_semester_one_repeat_keeps_edits_and_settings(client):
    seed_subject(client)
    client.post("/semester-1")
    client.post("/update-assessment/2/1", data={"weight": "10", "score": "77"})
    client.post("/update-subject/2", data={"subject": "My Maths", "credits": "4"})
    with client.session_transaction() as session:
        session["scale"] = [[50, "Pass", 4], [0, "Fail", 0]]
        session["target"] = 75
    response = client.post("/semester-1", follow_redirects=True)
    assert b"already added" in response.data
    with client.session_transaction() as session:
        assert len(session["subjects"]) == 9
        assert session["subjects"][0]["name"] == "Math"
        assert session["subjects"][1]["name"] == "My Maths"
        assert session["subjects"][1]["assessments"][0]["score"] == 77
        assert session["scale"][0] == [50, "Pass", 4]
        assert session["target"] == 75


def test_semester_one_invalidates_results(client):
    seed_subject(client)
    client.post("/calculate")
    client.post("/semester-1")
    with client.session_transaction() as session:
        assert "summary" not in session
        assert "results" not in session


def test_semester_one_form_has_csrf_protection(client):
    app.config["CSRF_ENABLED"] = True
    try:
        assert client.post("/semester-1").status_code == 400
        client.get("/")
        with client.session_transaction() as session:
            token = session["csrf_token"]
        assert client.post("/semester-1", data={"csrf_token": token}).status_code == 302
    finally:
        app.config["CSRF_ENABLED"] = False


def test_fraction_marks_save_and_contribute_as_percentages(client):
    seed_subject(client)
    response = client.post("/update-assessment/1/1", data={"weight": "40", "score": "14/20"},
                           follow_redirects=True)
    assert b'value="14/20"' in response.data
    assert b"70.0%" in response.data
    with client.session_transaction() as session:
        assert session["subjects"][0]["assessments"][0]["score"] == 70
    client.post("/calculate")
    with client.session_transaction() as session:
        assert session["results"]["1"]["completed_contribution"] == 28
    assert b"Math,4,Projected,76.0" in client.get("/export").data
    client.post("/update-assessment/1/1", data={"weight": "40", "score": ""})
    with client.session_transaction() as session:
        assert session["subjects"][0]["assessments"][0]["score"] is None
        assert session["subjects"][0]["assessments"][0]["score_input"] == ""


@pytest.mark.parametrize("score", ["14/0", "21/20", "bad", "nan/20"])
def test_invalid_fraction_preserves_saved_assessment(client, score):
    seed_subject(client)
    response = client.post("/update-assessment/1/1", data={"weight": "50", "score": score},
                           follow_redirects=True)
    assert b"Enter a percentage" in response.data
    with client.session_transaction() as session:
        assessment = session["subjects"][0]["assessments"][0]
        assert assessment["weight"] == 40
        assert assessment["score"] == 75


def test_subject_target_applies_to_results_and_export(client):
    seed_subject(client)
    client.post("/subject-target/1", data={"target": "70"})
    client.post("/calculate")
    with client.session_transaction() as session:
        assert session["results"]["1"]["target"] == 70
        assert session["results"]["1"]["required_marks"] == 66.67
    assert b",70.0,66.67," in client.get("/export").data
    client.post("/subject-target/1", data={"target": ""})
    with client.session_transaction() as session:
        assert "target" not in session["subjects"][0]


@pytest.mark.parametrize("target", ["nan", "inf", "-1", "101", "bad"])
def test_invalid_subject_target_is_rejected(client, target):
    seed_subject(client)
    response = client.post("/subject-target/1", data={"target": target}, follow_redirects=True)
    assert b"Subject target must be between 0 and 100." in response.data


def test_fraction_remembers_total_for_planning(client):
    seed_subject(client)
    client.post("/update-assessment/1/1", data={"weight": "40", "score": "14/20"})
    client.post("/update-assessment/1/2", data={"weight": "60", "score": "", "max_marks": "50"})
    with client.session_transaction() as session:
        assert session["subjects"][0]["assessments"][0]["max_marks"] == 20
        assert session["subjects"][0]["assessments"][1]["max_marks"] == 50
