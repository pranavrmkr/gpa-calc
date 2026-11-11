import os
import secrets
from math import isfinite

from flask import Flask, render_template, request, redirect, url_for, session
from calculations.weighted_average import calculate_required_marks

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
 
def invalidate_results():
    session.pop("results", None)
    session.pop("error", None) 

@app.route("/", methods=["GET"])

def home():

    return render_template(
        "index.html",
        subjects=session.get("subjects", []),
        target=session.get("target", 80),
        results=session.get("results", {})
    )


@app.route("/set-target", methods=["POST"])
def set_target():

    try:
        target = float(request.form["target"])

        if not 0 <= target <= 100:
            raise ValueError

        session["target"] = target
        invalidate_results()
        
    except (ValueError, KeyError):
        session["error"] = "Target must be between 0 and 100."

    
    return redirect(url_for("home"))
    

@app.route("/add-subject", methods=["POST"])
def add_subject():
    name = request.form.get("subject", "").strip()
    credits = request.form.get("credits", type=float)

    if not name:
        session["error"] = "Subject name is required."
        return redirect(url_for("home"))

    if credits is None or not isfinite(credits) or credits <= 0:
        session["error"] = "Credits must be greater than zero."
        return redirect(url_for("home"))

    subjects = session.get("subjects", [])

    new_subject = {
        "id": max((s["id"] for s in subjects), default=0) + 1,
        "name": name,
        "credits": credits,
        "assessments": []
    }

    subjects.append(new_subject)
    session["subjects"] = subjects

    invalidate_results()
    return redirect("/")


@app.route("/delete-subject/<int:subject_id>", methods=["POST"])
def delete_subject(subject_id):

    subjects = session.get("subjects", [])

    subjects = [
        s for s in subjects
        if s["id"] != subject_id
    ]

    session["subjects"] = subjects

    results = session.get("results", {})
    results.pop(str(subject_id), None)
    session["results"] = results
    invalidate_results()
    
    return redirect(url_for("home"))


@app.route("/add-assessment/<int:subject_id>", methods=["POST"])
def add_assessment(subject_id):

    subjects = session.get("subjects", [])

    for subject in subjects:

        if subject["id"] == subject_id:

            name = request.form.get("assessment", "").strip()

            if not name:
                session["error"] = "Assessment name is required."
                return redirect(url_for("home"))

            assessments = subject["assessments"]

            new_id = max(
                (a["id"] for a in assessments),
                default=0
            ) + 1

            assessments.append({
                "id": new_id,
                "name": name,
                "weight": 0,
                "score": None
            })

            break

    session["subjects"] = subjects
    invalidate_results()

    return redirect(url_for("home"))


@app.route("/delete-assessment/<int:subject_id>/<int:assessment_id>", methods=["POST"])
def delete_assessment(subject_id, assessment_id):

    subjects = session.get("subjects", [])

    for subject in subjects:

        if subject["id"] == subject_id:

            subject["assessments"] = [
                a for a in subject["assessments"]
                if a["id"] != assessment_id
            ]

            break

    session["subjects"] = subjects
    invalidate_results()
    

    return redirect(url_for("home"))


@app.route("/update-assessment/<int:subject_id>/<int:assessment_id>", methods=["POST"])
def update_assessment(subject_id, assessment_id):

    subjects = session.get("subjects", [])

    try:
        weight = float(request.form["weight"])

        score_input = request.form.get("score", "").strip()

        score = float(score_input) if score_input else None

        if not 0 <= weight <= 100:
            raise ValueError("Weight must be between 0 and 100.")

        if score is not None and not 0 <= score <= 100:
            raise ValueError("Score must be between 0 and 100.")

        for subject in subjects:

            if subject["id"] == subject_id:

                for assessment in subject["assessments"]:

                    if assessment["id"] == assessment_id:

                        assessment["weight"] = weight
                        assessment["score"] = score

        session["subjects"] = subjects
        invalidate_results()
        
    except (ValueError, KeyError):
        session["error"] = "Invalid weight or assessment score."

    return redirect(url_for("home"))


@app.route("/calculate", methods=["POST"])
def calculate():
    session.pop("results", None)
    subjects = session.get("subjects", [])
    results = {}

    try:

        for subject in subjects:

            assessments = subject["assessments"]

            if not assessments:
                raise ValueError(
                    f"{subject['name']} has no assessments."
                )

            total_weight = sum(a["weight"] for a in assessments)

            if abs(total_weight - 100) > 0.01:
                raise ValueError(
                    f"{subject['name']}: weights must total 100%."
                )

            results[str(subject["id"])] = calculate_required_marks(
                assessments,
                session.get("target", 80)
            )

    except ValueError as e:

        session["error"] = str(e)
        return redirect(url_for("home"))

    session["results"] = results
    session.pop("error", None)

    return redirect(url_for("home"))


@app.route("/clear", methods=["POST"])
def clear():

    session.clear()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run()