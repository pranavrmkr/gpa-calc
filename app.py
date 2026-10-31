from flask import Flask, render_template, request

from calculations.weighted_average import calculate_required_marks

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    error = None

    if request.method == "POST":

        try:
            subject = request.form["subject"]
            target = float(request.form["target"])

            assessments = [
                {
                    "name": request.form["name1"],
                    "weight": float(request.form["weight1"]),
                    "score": float(request.form["score1"])
                    if request.form["score1"] else None
                },
                {
                    "name": request.form["name2"],
                    "weight": float(request.form["weight2"]),
                    "score": float(request.form["score2"])
                    if request.form["score2"] else None
                },
                {
                    "name": request.form["name3"],
                    "weight": float(request.form["weight3"]),
                    "score": float(request.form["score3"])
                    if request.form["score3"] else None
                }
            ]

            total_weight = sum(a["weight"] for a in assessments)

            if not subject.strip():
                raise ValueError("Enter a subject name.")

            if not 0 <= target <= 100:
                raise ValueError("Target must be between 0 and 100.")

            if any(not 0 <= a["weight"] <= 100 for a in assessments):
                raise ValueError("Assessment weights must be between 0 and 100.")

            if abs(total_weight - 100) > 0.01:
                raise ValueError("Assessment weights must total 100%.")

            if any(
                a["score"] is not None and not 0 <= a["score"] <= 100
                for a in assessments
            ):
                raise ValueError("Scores must be between 0 and 100.")

            result = calculate_required_marks(assessments, target)

            result["subject"] = subject
            result["target"] = target

        except (ValueError, KeyError) as e:
            error = str(e)

    return render_template(
        "index.html",
        result=result,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)
