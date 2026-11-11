# GPA Calculator

A web-based Grade and GPA Calculator built using Python, Flask, HTML, and CSS. The application helps students manage subjects, configure assessment weightages, calculate the marks required to achieve a target percentage, and work towards calculating their semester GPA.

## Features

### 1. Subject Management
- Add and delete subjects.
- Assign credit values to individual subjects.
- Manage multiple subjects within one session.

### 2. Assessment Management
- Add assessments under individual subjects.
- Configure assessment weightages as percentages.
- Enter marks obtained in completed assessments.
- Leave pending assessments without a score.
- Edit and delete assessments.

### 3. Weighted Percentage Calculator
- Set a target percentage.
- Calculate the marks required in remaining assessments.
- Display completed assessment contributions.
- Calculate the remaining assessment weightage.
- Determine the maximum achievable percentage.
- Identify whether the target is achievable.

### 4. GPA Calculation Engine
- Convert percentages into letter grades.
- Convert letter grades into grade points.
- Calculate credit-weighted semester GPA.
- Uses a configurable grading scale in the calculation module.

*Note: GPA calculations currently use an illustrative 10-point grading scale. Integration with the Flask interface and support for institution-specific grading systems are planned.*

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Application logic |
| Flask 3.1 | Backend framework |
| HTML5 | Webpage structure |
| CSS3 | Styling and responsive layout |
| Jinja2 | HTML templating |
| pytest | Unit testing |
| Git | Version control |

## Project Structure

```text
GPA_calc/
│
├── calculations/
│   ├── __init__.py
│   ├── weighted_average.py
│   └── gpa.py
│
├── templates/
│   └── index.html
│
├── static/
│   └── css/
│       └── style.css
│
├── tests/
│   ├── test_calculations.py
│   └── test_gpa.py
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/pranavrmkr/gpa-calc.git
cd gpa-calc
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

For a stable session across restarts, set `SECRET_KEY` to a random secret in your environment. Without it, the app creates a new key at startup and existing sessions reset.

### 5. Run the application

```bash
python app.py
```

Open the following URL in your browser:

```text
http://127.0.0.1:5000
```

## Calculation Logic

### Weighted Assessment Contribution

Each completed assessment contributes to the final percentage according to its weightage.

\[
C = \sum \frac{S_i \times W_i}{100}
\]

Where:
- \(C\) = Completed contribution
- \(S_i\) = Assessment score
- \(W_i\) = Assessment weightage

### Required Marks

\[
R = \frac{T-C}{W_r/100}
\]

Where:
- \(R\) = Required average in remaining assessments
- \(T\) = Target percentage
- \(C\) = Completed contribution
- \(W_r\) = Remaining assessment weightage

### Credit-Weighted GPA

\[
GPA = \frac{\sum (C_i \times GP_i)}{\sum C_i}
\]

Where:
- \(C_i\) = Subject credits
- \(GP_i\) = Subject grade points

## Testing

Unit tests are maintained using pytest.

Run the test suite using:

```bash
python -m pytest -v
```

Tests cover:
- Required marks calculation.
- Completed and pending assessments.
- Unachievable target percentages.
- Invalid assessment weights and scores.
- Percentage-to-grade conversion.
- Credit-weighted GPA calculation.

## Current Development Status

- [x] Flask project setup
- [x] Subject management
- [x] Assessment management
- [x] Assessment weightage configuration
- [x] Target percentage configuration
- [x] Required marks calculation
- [x] Calculation validation
- [x] Subject credit configuration
- [x] Basic GPA calculation module
- [ ] Connect GPA calculations to Flask
- [ ] Display subject-wise grades and grade points
- [ ] Display semester GPA on the webpage
- [ ] Support configurable university grading scales
- [ ] Improve automated test execution and coverage

## Future Improvements

- Configurable grading systems based on university requirements.
- GPA target planning and projections.
- Persistent data storage using a database.
- Export calculation results.
- Improved validation and error handling.

---

**Project:** GPA Calculator  
**Language:** Python  
**Framework:** Flask  
**Status:** In Development