# GPA Calculator

A Flask app for planning assessment marks, checking subject grades, and calculating a credit-weighted semester GPA. It includes custom grade bands, GPA projections, SQLite saving, and CSV downloads.

## Run locally

Use Python 3.12.

```powershell
git clone https://github.com/pranavrmkr/gpa-calc.git
cd gpa-calc
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser. Debug mode is off by default.

On macOS or Linux, activate with `source .venv/bin/activate` instead.

## Semester 1 shortcut

Click **+ Semester 1** near the top of the page to load the SNU Chennai B.Tech IT first-semester template supplied for this project. Assessment scores start blank, so you can enter marks straight away.

| Subject | Credits | Assessments and weights |
|---|---|---|
| Mathematics I | 4 | CIA 1 10%, CIA 2 10%, Mid-Semester 30%, End-Semester 50% |
| Electrical and Electronics Essentials for IT | 2 | CIA 1 10%, CIA 2 10%, Mid-Semester 30%, End-Semester 50% |
| Communicative English | 3 | Combined CIA 10%, Mid-Semester Theory 20%, End-Semester Practical 30%, End-Semester Theory 40% |
| Computational Thinking and Problem Solving with Python | 3 | Combined CIA 10%, Mid-Semester Theory 20%, End-Semester Practical 30%, End-Semester Theory 40% |
| Introduction to Web Programming | 3 | Combined CIA 10%, Mid-Semester Theory 20%, End-Semester Practical 30%, End-Semester Theory 40% |
| Professional Ethics and Human Values | 2 | CIA 1 10%, CIA 2 10%, Mid-Semester 30%, End-Semester 50% |
| Open-Source Tools and Prompt Engineering | 2 | Internal Continuous Assessments 80%, End-Semester 20% |
| Extra Academic Activity 1 | 1 | Pass / 10 points, excluded from GPA |

The preset includes **19 GPA credits plus 1 non-CGPA EAA credit**. EAA has no weighted assessments and is marked Pass with 10 points according to the supplied specification. Its credit and points are excluded from final, projected, and maximum GPA; CSV downloads label it as excluded.

Clicking again adds only missing courses. Preset IDs and matching course names prevent duplicates, and existing courses, saved scores, renamed preset courses, and settings are preserved. Matching existing courses are left as they are rather than having their assessments replaced. You can still add and edit subjects manually.

The supplied specification defines grade points but does not provide percentage cutoffs. Loading Semester 1 keeps your current grading scale; check the cutoffs against your institution's rules before relying on the GPA.

## How to use it

1. Set the target percentage you want in each subject.
2. Use **+ Semester 1**, or add subjects with their credit values. You can edit names and credits later.
3. Add assessments, then save each assessment's weight and score. Weights within each subject must total 100%. Scores accept percentages or earned/total marks: enter `18/20` or `90` for 90%. Fractions convert automatically when you save, and the converted percentage appears beside the field. Your original marks entry stays in the field for editing. Decimal marks such as `14.5/20` work too. Total marks must be positive, and earned marks must be between zero and the total. Leave unfinished assessments blank; a score of 0 counts as completed.
4. In **Grading and projections**, set your expected score for pending assessments and your target semester GPA. Enter your institution's grade bands and save the settings.
5. Select **Calculate Results** to see required marks, subject grades, and semester GPA projections.
6. Select **Download CSV** in the results to export the current calculation.

Edits invalidate previous results. Save every form before calculating again. Unsaved input is not included. **Clear All Data** removes the saved semester and settings for the current browser; export results first if you need to keep them.

## Results explained

- **Completed contribution** is the percentage already earned toward a subject's final result.
- **Required average** is the score needed across the remaining assessment weight to reach the target percentage. The result says whether the target is already achieved, still possible, or unreachable.
- **Final percentage and grade** appear when every assessment with a positive weight has a score.
- **Projected percentage and grade** use your expected pending score for unfinished assessments.
- **GPA for fully graded subjects** includes only finished subjects and their credits. Once all subjects are finished, this becomes **Semester GPA**.
- **Projected semester GPA** includes all subjects, using expected pending scores.
- **Maximum possible GPA** assumes 100% on every pending assessment. The target GPA message compares your target against the projection and maximum.

A zero-weight pending assessment does not prevent a subject from being final. Calculations use full precision before displaying values rounded to two decimal places. GPA is calculated from grade points, not directly from the average percentage.

## Custom grading scales

The default scale is an illustrative 10-point scale, not a specific university's official policy:

| Minimum percentage | Grade | Points |
|---|---|---|
| 90 | O | 10 |
| 80 | A+ | 9 |
| 70 | A | 8 |
| 60 | B+ | 7 |
| 50 | B | 6 |
| 40 | C | 5 |
| 0 | F | 0 |

Each line in the grading field uses `minimum percentage, grade, points`. For example, a simple pass/fail scale is:

```text
50, Pass, 4
0, Fail, 0
```

Cutoffs are inclusive. Bands are sorted automatically and must have unique cutoffs, a 0% band, nonempty grade names, and points that do not decrease as percentage rises. Percentages and grade points must be between 0 and 100. The target GPA must be within the scale's maximum. Grade names cannot contain commas.

## Saving and privacy

Data is stored in `instance/gpa.sqlite3`. The app creates the database automatically. A random browser cookie identifies your saved semester; subject details and scores stay in the database rather than in the cookie. Saved data survives app restarts and expires after 31 days without activity. Expired rows are cleaned up during subsequent requests.

This is a local, single-semester calculator without accounts or device syncing. Separate browsers have separate saved work. Clearing browser cookies loses access to that browser's saved semester. Back up the database while the app is stopped if you want to preserve it; CSV exports contain results, not a restorable backup. Database files are ignored by Git.

Optional environment variables:

- `GPA_DATABASE`: path to a different SQLite database. Defaults to `instance/gpa.sqlite3`.
- `SECRET_KEY`: Flask secret key. The server-side saved semester does not depend on this key staying unchanged.

Forms use CSRF protection, and missing or deleted records show an error page. The built-in Flask server is intended for local use. Public hosting would need deployment configuration and an account/access model appropriate for saved student data.

## Calculation logic

For scores `S` and assessment weights `W`:

```text
Completed contribution = sum(score * weight / 100) for completed assessments
Required pending average = (target - completed contribution) / (remaining weight / 100)
Projected percentage = completed contribution + expected pending score * remaining weight / 100
Semester GPA = sum(subject credits * grade points) / sum(subject credits)
```

The default grade scale can be replaced through the settings form. All subjects in a semester use the selected scale. This calculator does not implement institution-specific rounding, resit, attendance, or pass-per-assessment rules.

## Project structure

```text
app.py                       Flask routes, settings, validation, and CSV export
storage.py                   SQLite-backed browser sessions
semester_presets.py          SNU IT Semester 1 courses and assessment weights
calculations/gpa.py          Grade bands and semester GPA projections
calculations/weighted_average.py  Required assessment marks
templates/index.html         Calculator page
templates/error.html         Request error page
static/css/style.css         Responsive styles
tests/                       Calculation, route, storage, and workflow tests
.github/workflows/tests.yml  Automated tests on pushes and pull requests
pytest.ini                   Test discovery and temporary file settings
requirements.txt             Pinned dependencies
```

## Tests

```powershell
python -m pytest -q
python -m pip check
```

The suite covers required marks, invalid inputs, custom grade bands, final versus projected GPA, subject and assessment edits, stale result clearing, SQLite persistence and expiry, browser isolation, large saved semesters, CSV output, CSRF protection, missing records, the full add/save/calculate/export/clear workflow, Semester 1 loading without duplicates or lost edits, and EAA exclusion from every GPA calculation. Temporary test databases live under `.pytest_cache/tmp`.

GitHub Actions runs the suite on Python 3.12 for pushes and pull requests.

## Status

The local calculator's planned core features are implemented: subject and assessment management, required marks, subject grades, semester GPA, configurable scales, target projections, database saving, CSV export, and automated regression tests.
