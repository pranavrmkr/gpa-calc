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
| Introduction to ARVR | 2 | Internal Continuous Assessments 80%, End-Semester 20% |
| Extra Academic Activity 1 | 1 | Pass / 10 points, excluded from GPA |

The preset includes **21 GPA credits plus 1 non-CGPA EAA credit**. EAA has no weighted assessments and is marked Pass with 10 points according to the supplied specification. Its credit and points are excluded from final, projected, and maximum GPA; CSV downloads label it as excluded.

Clicking again adds only missing courses, including Introduction to ARVR for semesters loaded before it was added. Preset IDs and matching course names prevent duplicates, and existing courses, saved scores, renamed preset courses, and settings are preserved. Matching existing courses are left as they are rather than having their assessments replaced. You can still add and edit subjects manually.

The supplied specification defines grade points but does not provide percentage cutoffs. Loading Semester 1 keeps your current grading scale; check the cutoffs against your institution's rules before relying on the GPA.

## Menus and workflow

- **Subjects & marks**: load Semester 1, add or edit subjects, and enter assessment scores. Open a subject card to work on it. Scores accept percentages or earned/total marks: `18/20` and `90` both mean 90%. Decimal marks such as `14.5/20` work too. Fractions keep their original entry for editing and show the converted percentage after saving. Leave pending scores blank; 0 counts as completed. Assessment weights within a subject must total 100%.
- **Target planner**: set a final percentage separately for each subject. Blank targets use the default target from Settings. Saving a target immediately updates its plan; it also applies to GPA results and CSV exports.
- **GPA calculator**: choose **Calculate GPA** after saving your marks to see actual and projected GPA and subject grades. **Download CSV** exports the results.
- **Settings**: set the default subject target, expected score on pending assessments, target semester GPA, and grade bands. Clear saved data here when you want a fresh semester.

With JavaScript enabled, forms save and delete in place without a page reload. The current menu, open subject cards, scroll position, and unsaved edits in other forms are kept. A status message confirms saves or explains errors. Duplicate submissions are blocked while a request is running. Validation errors keep the submitted draft editable. Without JavaScript, all sections remain available and forms use normal page navigation.

Save every form before calculating; unsaved input is not included. Changes invalidate previous GPA results, so use **Calculate GPA** again after edits. **Clear All Data** removes saved work and unsaved drafts; export anything you need first.

## Marks needed in an assessment

In **Subjects & marks**, enter an optional **Total marks** for a pending assessment, such as 20 or 50, then save the row. An entry such as `14/20` also records the total automatically. A plain score is always a percentage even if a total is set.

The **Target planner** shows each subject's required average across its pending assessments, plus the required percentage and marks for each individual pending assessment. For example, a required 70% on an assessment out of 20 is shown as `14 / 20`.

Each individual estimate assumes the expected pending score from Settings on all the *other* pending assessments. These rows are separate scenarios, not a combined set of marks to achieve together. Use the required average if you want the same percentage across all pending assessments. An estimate can be unreachable under the chosen assumptions even when a different combination of scores could reach the subject target.

Marks and individual required percentages round up to two decimal places so the displayed value does not undershoot the target. If an exam only awards whole marks, round up to the next whole mark. Zero-weight pending assessments are left out of the estimates. The planner explains missing assessments or invalid total weights per subject, so another incomplete subject does not block a valid subject's plan.

## Results explained

- **Completed contribution** is the percentage already earned toward a subject's final result.
- **Required average** is the score needed across the remaining assessment weight to reach the target percentage. The result says whether the target is already achieved, still possible, or unreachable.
- **Final percentage and grade** appear when every assessment with a positive weight has a score.
- **Projected percentage and grade** use your expected pending score for unfinished assessments.
- **GPA for fully graded subjects** includes only finished subjects and their credits. Once all subjects are finished, this becomes **Semester GPA**.
- **Projected semester GPA** includes all subjects, using expected pending scores.
- **Maximum possible GPA** assumes 100% on every pending assessment. The target GPA message compares your target against the projection and maximum.

A zero-weight pending assessment does not prevent a subject from being final. GPA and subject percentages use full precision before displaying values rounded to two decimal places; individual assessment requirements round up as described above. GPA is calculated from grade points, not directly from the average percentage.

## Custom grading scales

The default grading system rounds each final course percentage to the nearest whole number, then applies these bands:

| Minimum percentage | Grade | Points |
|---|---|---|
| 91 | O | 10 |
| 81 | A+ | 9 |
| 71 | A | 8 |
| 61 | B+ | 7 |
| 51 | B | 6 |
| 50 | C | 5 |
| 0 | F | 0 |

Each line in the grading field uses `minimum percentage, grade, points`. For example, a simple pass/fail scale is:

```text
50, Pass, 4
0, Fail, 0
```

The rounded mark uses half-up rounding (so 50.5 becomes 51). Cutoffs are inclusive. Bands are sorted automatically and must have unique cutoffs, a 0% band, nonempty grade names, and points that do not decrease as percentage rises. Percentages and grade points must be between 0 and 100. The target GPA must be within the scale's maximum. Grade names cannot contain commas.

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
Selected assessment percentage = (subject target - completed contribution - expected contribution of other pending assessments) / (selected assessment weight / 100)
Selected assessment marks = selected assessment percentage * total marks / 100
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
static/js/app.js             Menus and in-place form updates
tests/ui.test.cjs            JavaScript interaction checks with a simulated DOM
tests/                       Calculation, route, storage, and workflow tests
.github/workflows/tests.yml  Automated tests on pushes and pull requests
pytest.ini                   Test discovery and temporary file settings
requirements.txt             Pinned dependencies
```

## Tests

```powershell
python -m pytest -q
python -m pip check
node --test tests/ui.test.cjs
```

The suite covers required marks, invalid inputs, custom grade bands, final versus projected GPA, subject and assessment edits, stale result clearing, SQLite persistence and expiry, browser isolation, large saved semesters, CSV output, CSRF protection, missing records, the full add/save/calculate/export/clear workflow, Semester 1 loading without duplicates or lost edits, and EAA exclusion from every GPA calculation. Temporary test databases live under `.pytest_cache/tmp`.

JavaScript tests use Node.js 22 or newer and its built-in test runner; there are no npm dependencies. They exercise in-place updates, scroll/menu/card preservation, unsaved drafts, validation failures, network failures, deletes, clearing drafts, and duplicate-submit prevention using a simulated DOM. These checks do not replace a rendered browser test.

GitHub Actions runs the Python and JavaScript suites for pushes and pull requests.

## Status

The local calculator's planned core features are implemented: subject and assessment management, required marks, subject grades, semester GPA, configurable scales, target projections, database saving, CSV export, and automated regression tests.
