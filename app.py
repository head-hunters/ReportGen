from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    send_file,
)
from io import BytesIO
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dotenv import load_dotenv

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.platypus import HRFlowable

import os
import sqlite3
import re

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("register"))
    return redirect(url_for("dashboard"))


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        db = sqlite3.connect("database/app.db")
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

        session["user_id"] = db.lastrowid
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
@login_required
def dashboard():
    db = sqlite3.connect("database/app.db")
    db.row_factory = sqlite3.Row

    name = db.execute(
        "Select email from users where id=?", (session["user_id"],)
    ).fetchone()

    name = name["email"].split("@")[0].capitalize()

    # Displaying Project Info in Dashboard's Cards

    projects = db.execute(
        """
    SELECT *
    FROM projects
    WHERE user_id = ?
    ORDER BY created_at DESC
    """,
        (session["user_id"],),
    ).fetchall()

    # Formatting the date
    new_projects = []

    for project in projects:

        project_dict = dict(project)

        display_date = datetime.fromisoformat(project["created_at"]).strftime("%d %B")

        project_dict["date"] = display_date

        new_projects.append(project_dict)

    projects = new_projects

    db.close()
    return render_template("dashboard.html", name=name, projects=projects)


@app.route("/project_form.html", methods=["GET", "POST"])
@login_required
def project_form():
    if request.method == "POST":

        project_id = request.form.get("project_id")

        # project details
        title = request.form.get("title")
        name = request.form.get("name")
        dept = request.form.get("dept")
        abstract = request.form.get("abstract")
        description = request.form.get("description")
        survey = request.form.get("survey")
        technologies = request.form.get("technologies")
        duration = request.form.get("duration")
        additional = request.form.get("additional")

        # module details

        modules = []

        module_count = int(request.form.get("modules"))
        for i in range(1, module_count + 1):
            modules.append(
                {
                    "name": request.form.get(f"module_name_{i}"),
                    "description": request.form.get(f"module_description_{i}"),
                }
            )
        preview_data = {
            "title": title,
            "name": name,
            "dept": dept,
            "abstract": abstract,
            "description": description,
            "survey": survey,
            "technologies": technologies,
            "duration": duration,
            "additional": additional,
            "modules": modules,
        }

        if project_id:
            preview_data["project_id"] = project_id
            preview_data["editing"] = True

        session["preview_data"] = preview_data
        return redirect(url_for("preview"))

    else:
        if request.args.get("edit") == "1":

            data = session.get("preview_data")

            return render_template("project_form.html", **data if data else {})
        session.pop("preview_data", None)
        return render_template("project_form.html")


@app.route("/preview.html")
@login_required
def preview():

    project_id = request.args.get("project_id")
    if project_id:
        db = sqlite3.connect("database/app.db")
        db.row_factory = sqlite3.Row
        data = db.execute(
            """SELECT * FROM projects WHERE user_id=? AND project_id=?""",
            (session["user_id"], project_id),
        ).fetchone()
        modules = db.execute(
            """SELECT * FROM modules WHERE project_id=? ORDER BY module_number""",
            (project_id,),
        ).fetchall()
        modules = [dict(module) for module in modules]  # dictionary conversion
        db.close()
        return render_template(
            "preview.html", **data, modules=modules, existing_project=True
        )
    else:
        data = session.get("preview_data")
        if not data:
            return redirect(url_for("project_form"))

        return render_template(
            "preview.html",
            **data,
            existing_project="project_id" in data,
        )


@app.route("/clear_project")
@login_required
def clear_project():
    session.pop("preview_data", None)
    return redirect(url_for("project_form"))


@app.route("/edit/<int:project_id>")
@login_required
def edit(project_id):

    # When the user presses the back button and you want the changes to persist
    preview_data = session.get("preview_data")

    if preview_data and str(preview_data.get("project_id")) == str(project_id):
        return render_template(
            "project_form.html", **preview_data, existing_project=True
        )

    db = sqlite3.connect("database/app.db")
    db.row_factory = sqlite3.Row
    data = db.execute(
        """SELECT * FROM projects WHERE user_id=? AND project_id=?""",
        (session["user_id"], project_id),
    ).fetchone()
    modules = db.execute(
        """SELECT * FROM modules WHERE project_id=? ORDER BY module_number""",
        (project_id,),
    ).fetchall()
    modules = [dict(module) for module in modules]  # dictionary conversion
    db.close()
    return render_template(
        "project_form.html",
        **dict(data),
        modules=modules,
        existing_project=True,
    )


@app.route("/confirm", methods=["POST"])
@login_required
def confirm():
    data = session.get("preview_data")
    if not data:
        return redirect(url_for("project_form"))

    db = sqlite3.connect("database/app.db")

    if "project_id" in data:
        # This check ensures that the project being edited is an EXISTING project
        project_id = data["project_id"]
        db.execute(
            """
            UPDATE projects
            SET title = ?,
                name = ?,
                dept = ?,
                abstract = ?,
                description = ?,
                survey = ?,
                technologies = ?,
                duration = ?,
                additional = ?
            WHERE project_id = ? AND user_id = ?
            """,
            (
                data["title"],
                data["name"],
                data["dept"],
                data["abstract"],
                data["description"],
                data["survey"],
                data["technologies"],
                data["duration"],
                data["additional"],
                project_id,
                session["user_id"],
            ),
        )

        # To REMOVE OLD modules

        db.execute(
            "DELETE FROM modules WHERE project_id = ?",
            (project_id,),
        )

    else:

        # New project creation
        cursor = db.execute(
            """
        INSERT INTO projects (
            user_id,
            title,
            name,
            dept,
            abstract,
            description,
            survey,
            technologies,
            duration,
            additional
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                session["user_id"],
                data["title"],
                data["name"],
                data["dept"],
                data["abstract"],
                data["description"],
                data["survey"],
                data["technologies"],
                data["duration"],
                data["additional"],
            ),
        )

        project_id = cursor.lastrowid

    # Insert current modules
    for i, module in enumerate(data["modules"], start=1):
        db.execute(
            """
            INSERT INTO modules (
                project_id,
                module_number,
                name,
                description
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                project_id,
                i,
                module["name"],
                module["description"],
            ),
        )

    db.commit()
    db.close()

    pdf = generate_pdf(data)

    session.pop("preview_data", None)

    # Sanitising filename

    filename = re.sub(r'[<>:"/\\|?*]', "-", data["title"])
    filename = re.sub(r"\s+", " ", filename).strip()

    response = send_file(
        pdf,
        as_attachment=True,
        download_name=f"{filename}.pdf",
        mimetype="application/pdf",
    )

    response.headers["Filename"] = f"{filename}.pdf"
    return response


@app.route("/delete/<int:project_id>", methods=["POST"])
@login_required
def delete(project_id):
    db = sqlite3.connect("database/app.db")

    # we're removing the modules first because of the foreign key relationship
    db.execute(
        """
        DELETE FROM modules
        WHERE project_id = ?
        """,
        (project_id,),
    )

    db.execute(
        """
        DELETE FROM projects
        WHERE project_id = ? AND user_id = ?
        """,
        (project_id, session["user_id"]),
    )
    db.commit()
    db.close()
    return redirect(url_for("dashboard"))


# PDF Generation and Styles


def get_pdf_styles():

    styles = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "ProjectTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=20,
            spaceAfter=6,
        ),
        "project_title": ParagraphStyle(
            "ProjectName",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=14,
            spaceAfter=25,
        ),
        "heading": ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            spaceBefore=10,
            spaceAfter=10,
        ),
        "subheading": ParagraphStyle(
            "Subheading",
            parent=styles["Heading3"],
            fontSize=11,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=styles["BodyText"],
            fontSize=10,
            leading=15,
            spaceAfter=10,
        ),
        "separator": {
            "width": "100%",
            "thickness": 1.0,
            "spaceBefore": 5,
            "spaceAfter": 0,
        },
    }


def add_page_number(canvas, document):
    canvas.saveState()

    canvas.setFont("Helvetica", 9)

    canvas.drawCentredString(A4[0] / 2, 30, f"Page {document.page}")

    canvas.restoreState()


def generate_pdf(data):

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)

    styles = get_pdf_styles()

    story = []

    # Title
    story.append(Paragraph("PROJECT REPORT", styles["title"]))

    story.append(Paragraph(data["title"], styles["project_title"]))

    # Basic Information
    story.append(Paragraph(f"Student: {data['name']}", styles["body"]))

    story.append(Paragraph(f"Department / Course: {data['dept']}", styles["body"]))

    story.append(Paragraph(f"Duration: {data['duration']}", styles["body"]))

    story.append(HRFlowable(**styles["separator"]))

    # Project Description
    story.append(Paragraph("PROJECT DESCRIPTION", styles["heading"]))

    story.append(Paragraph(data["description"], styles["body"]))

    story.append(HRFlowable(**styles["separator"]))

    # Modules
    story.append(Paragraph("MODULES", styles["heading"]))

    for i, module in enumerate(data["modules"], start=1):

        story.append(Paragraph(f"{i}. {module['name']}", styles["subheading"]))

        story.append(Paragraph(module["description"], styles["body"]))

    story.append(HRFlowable(**styles["separator"]))

    # Literature Survey
    story.append(Paragraph("LITERATURE SURVEY", styles["heading"]))

    story.append(Paragraph(data["survey"], styles["body"]))

    story.append(HRFlowable(**styles["separator"]))
    # Other Project Details
    story.append(Paragraph("OTHER PROJECT DETAILS", styles["heading"]))

    story.append(Paragraph("Technologies Used", styles["subheading"]))

    story.append(Paragraph(data["technologies"], styles["body"]))

    story.append(Paragraph("Duration", styles["subheading"]))

    story.append(Paragraph(data["duration"], styles["body"]))

    story.append(Paragraph("Additional Details", styles["subheading"]))

    story.append(Paragraph(data["additional"], styles["body"]))

    pdf.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)

    buffer.seek(0)
    return buffer


if __name__ == "__main__":
    app.run(debug=True)
