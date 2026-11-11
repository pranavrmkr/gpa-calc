import csv
import io
import os
import secrets
from math import isfinite
from pathlib import Path
from storage import SQLiteSessions

from flask import Flask, render_template, request, redirect, url_for, session, abort, Response
from calculations.gpa import GRADING_SCALE, validate_scale, semester_summary

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["DATABASE"] = os.environ.get("GPA_DATABASE", str(Path(app.instance_path) / "gpa.sqlite3"))
app.session_interface = SQLiteSessions()
 
def invalidate_results():
    session.pop("results", None)
    session.pop("summary", None)
    session.pop("error", None) 

@app.route("/", methods=["GET"])

def home():

    return render_template(
        "index.html",
        subjects=session.get("subjects", []),
        target=session.get("target", 80),
        results=session.get("results", {}),
        summary=session.get("summary"),
        scale=session.get("scale", GRADING_SCALE),
        pending_score=session.get("pending_score", 80),
        target_gpa=session.get("target_gpa", 8),
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

                        name = request.form.get("assessment", assessment["name"]).strip()
                        if not name:
                            raise ValueError("Assessment name is required.")
                        assessment["name"] = name
                        assessment["weight"] = weight
                        assessment["score"] = score

        session["subjects"] = subjects
        invalidate_results()
        
    except (ValueError, KeyError):
        session["error"] = "Invalid weight or assessment score."

    return redirect(url_for("home"))


@app.route("/calculate", methods=["POST"])
def calculate():
    invalidate_results()
    try:
        summary = semester_summary(
            session.get("subjects", []), session.get("target", 80),
            session.get("pending_score", 80), session.get("scale", GRADING_SCALE)
        )
    except ValueError as error:
        session["error"] = str(error)
    else:
        session["results"] = summary["results"]
        session["summary"] = summary
    return redirect(url_for("home"))


@app.post("/settings")
def settings():
    try:
        pending_score = float(request.form["pending_score"])
        target_gpa = float(request.form["target_gpa"])
        if not 0 <= pending_score <= 100:
            raise ValueError("Pending assessment score must be between 0 and 100.")
        scale = []
        for line in request.form["scale"].splitlines():
            if line.strip():
                parts = line.split(",")
                if len(parts) != 3:
                    raise ValueError("Use minimum percentage, grade, points on each line.")
                scale.append(parts)
        scale = validate_scale(scale)
        if not 0 <= target_gpa <= scale[0][2]:
            raise ValueError("Target GPA must fit your grading scale.")
    except (ValueError, KeyError) as error:
        session["error"] = str(error) or "Check your settings."
    else:
        session.update(scale=scale, pending_score=pending_score, target_gpa=target_gpa)
        invalidate_results()
    return redirect(url_for("home"))


@app.post("/update-subject/<int:subject_id>")
def update_subject(subject_id):
    subjects = session.get("subjects", [])
    subject = next((s for s in subjects if s["id"] == subject_id), None)
    if subject is None:
        abort(404)
    name = request.form.get("subject", "").strip()
    credits = request.form.get("credits", type=float)
    if not name or credits is None or not isfinite(credits) or credits <= 0:
        session["error"] = "Use a subject name and credits greater than zero."
    else:
        subject.update(name=name, credits=credits)
        session["subjects"] = subjects
        invalidate_results()
    return redirect(url_for("home"))


@app.get("/export")
def export():
    subjects = session.get("subjects", [])
    if not subjects:
        session["error"] = "Add subjects before exporting."
        return redirect(url_for("home"))
    try:
        summary = semester_summary(subjects, session.get("target", 80),
                                   session.get("pending_score", 80), session.get("scale", GRADING_SCALE))
    except ValueError as error:
        session["error"] = str(error)
        return redirect(url_for("home"))
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["Subject", "Credits", "Status", "Percentage", "Grade", "Grade points",
                     "Target percentage", "Required pending average", "Maximum percentage"])
    for subject in subjects:
        result = summary["results"][str(subject["id"])]
        name = subject["name"]
        grade = result["grade"]
        if name.lstrip().startswith(("=", "+", "-", "@")):
            name = "'" + name
        if grade.lstrip().startswith(("=", "+", "-", "@")):
            grade = "'" + grade
        writer.writerow([name, subject["credits"], "Final" if result["final"] else "Projected",
                         result["percentage"], grade, result["points"], result["target"],
                         result["required_marks"], result["maximum_possible"]])
    writer.writerow([])
    writer.writerow(["GPA for fully graded subjects", summary["gpa"]])
    writer.writerow(["Projected semester GPA", summary["projected_gpa"]])
    writer.writerow(["Maximum possible GPA", summary["maximum_gpa"]])
    writer.writerow(["Expected pending score (%)", session.get("pending_score", 80)])
    writer.writerow(["Target GPA", session.get("target_gpa", 8)])
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=gpa-results.csv"})


@app.route("/clear", methods=["POST"])
def clear():

    session.clear()

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run()
