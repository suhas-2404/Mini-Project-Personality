#####################################################
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from numpy import *
from sklearn.linear_model import LogisticRegression
import os

#####################################################

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Simple in-memory user store (for demo purposes)
users = {}

#####################################################
# Loading Dataset Globally
data = pd.read_csv("dataset.csv")
array = data.values

for i in range(len(array)):
    if array[i][0] == "Male":
        array[i][0] = 1
    else:
        array[i][0] = 0

df = pd.DataFrame(array)

maindf = df[[0, 1, 2, 3, 4, 5, 6]]
mainarray = maindf.values

temp = df[7]
train_y = temp.values
train_y = temp.values

for i in range(len(train_y)):
    train_y[i] = str(train_y[i])

mul_lr = LogisticRegression(
    solver="newton-cg", max_iter=1000
)
mul_lr.fit(mainarray, train_y)
#####################################################


@app.route("/", methods=["POST", "GET"])
def home():
    # If user is logged in, show main page, else redirect to signup
    if "user" in session:
        if request.method == "GET":
            return render_template("index.html")
        else:
            age = int(request.form["age"])
            if age < 17:
                age = 17
            elif age > 28:
                age = 28

            inputdata = [
                [
                    request.form["gender"],
                    age,
                    9 - int(request.form["openness"]),
                    9 - int(request.form["neuroticism"]),
                    9 - int(request.form["conscientiousness"]),
                    9 - int(request.form["agreeableness"]),
                    9 - int(request.form["extraversion"]),
                ]
            ]

            for i in range(len(inputdata)):
                if inputdata[i][0] == "Male":
                    inputdata[i][0] = 1
                else:
                    inputdata[i][0] = 0

            df1 = pd.DataFrame(inputdata)
            testdf = df1[[0, 1, 2, 3, 4, 5, 6]]
            maintestarray = testdf.values

            y_pred = mul_lr.predict(maintestarray)
            for i in range(len(y_pred)):
                y_pred[i] = str((y_pred[i]))
            DF = pd.DataFrame(y_pred, columns=["Predicted Personality"])
            DF.index = DF.index + 1
            DF.index.names = ["Person No"]

            return render_template(
                "result.html", per=DF["Predicted Personality"].tolist()[0]
            )
    else:
        return redirect(url_for("signup"))


@app.route("/learn")
def learn():
    return render_template("learn.html")


@app.route("/working")
def working():
    return render_template("working.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        if username in users:
            flash("Username already exists!", "danger")
            return render_template("signup.html")
        users[username] = {
            "email": email,
            "password": generate_password_hash(password)
        }
        session["user"] = username  # Log in the user after signup
        flash("Signup successful! Welcome!", "success")
        return redirect(url_for("home"))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = users.get(username)
        if user and check_password_hash(user["password"], password):
            session["user"] = username
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password!", "danger")
            return render_template("login.html")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))


# Handling error 404
@app.errorhandler(404)
def not_found_error(error):
    return render_template("error.html", code=404, text="Page Not Found"), 404


# Handling error 500
@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", code=500, text="Internal Server Error"), 500


if __name__ == "__main__":

    # use 0.0.0.0 for replit hosting
    # app.run(host="0.0.0.0", port=8080)

    # for localhost testing
    # app.run(debug=True)
    app.run()