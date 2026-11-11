import pytest

from app import app


@pytest.fixture
def client(tmp_path):
    app.config.update(TESTING=True, SECRET_KEY="test-key", DATABASE=str(tmp_path / "test.sqlite3"))
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

