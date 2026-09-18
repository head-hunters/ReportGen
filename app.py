from flask import Flask, flash, redirect, render_template, request, session, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your-secret-key"


@app.route("/")
def index():
    return redirect(url_for("register"))


@app.route("/register", methods=["GET", "POST"])
def register():

    db = sqlite3.connect("database/app.db")

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if not email:
            flash("Invalid email.", "Error")
            return render_template("register.html")
        elif not password:
            flash("Invalid password.", "Error")
            return render_template("register.html", email=email)
        elif not confirm or password != confirm:
            flash("Invalid confirmation", "Error")
            return render_template("register.html", email=email, password=password)

        try:

            db.execute(
                "INSERT INTO users (email,password_hash) VALUES(?,?)",
                (email, generate_password_hash(password)),
            )

            db.commit()
            db.close()
        except sqlite3.IntegrityError:
            flash("Account already Exists!", "Error")
            return render_template("register.html")

        return render_template("dashboard.html")
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        db = sqlite3.connect("database/app.db")
        db.row_factory = sqlite3.Row
        email = request.form.get("email")
        password = request.form.get("password")

        if not email:
            flash("Invalid email.", "Error")
            return render_template("login.html")
        elif not password:
            flash("Invalid password.", "Error")
            return render_template("login.html", email=email)

        user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid username and/or password", "Error")
            return render_template("login.html")

        session["user_id"] = user["id"]

        db.close()
        return redirect(url_for("dashboard"))

    else:
        return render_template("login.html")


@app.route("/dashboard.html")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(debug=True)
