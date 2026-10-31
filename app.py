from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Grade_gpa calc"

@app.route("/about")
def about():
    return "This is about the GPA calc"

if __name__ == "__main__":
    app.run(debug=True)

