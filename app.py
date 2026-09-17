from flask import Flask, flash, redirect, render_template, request, session, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your-secret-key"


@app.route("/")
# Redirect by default


def index():
    return redirect(url_for("register"))


@app.route("/register", methods=["GET", "POST"])
# User registration


def register():
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
        return render_template("register.html")
    else:
        return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)
