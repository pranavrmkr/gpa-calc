import pytest

from app import app


@pytest.fixture
def client():
    app.config.update(TESTING=True, SECRET_KEY="test-key")
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
