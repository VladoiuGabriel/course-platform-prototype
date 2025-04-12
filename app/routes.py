import os

from app import mail
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, login_required, current_user, logout_user
from flask_socketio import emit, join_room
from werkzeug.utils import secure_filename

from app.models import User, Course, ProfessorKeys, Message, Material
from app import bcrypt, db, socketio
from sqlalchemy.sql import text
import secrets
from flask_mail import Message as MailMessage

main = Blueprint("main", __name__)

@main.route("/")
def home():

    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    return render_template("home.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)

            if user.role == "profesor":
                return redirect(url_for("main.profesor_dashboard"))
            elif user.role == "student":
                return redirect(url_for("main.student_dashboard"))

        flash("Autentificare eșuată! Verifică datele introduse.", "danger")

    return render_template("login.html")


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
        role = request.form["role"]
        professor_key = request.form.get("professor_key")

        if role == "profesor":
            key = ProfessorKeys.query.filter_by(key_value=professor_key, is_used=False).first()

            if not key:
                flash("Cheia de acces este invalidă sau a fost deja folosită.", "danger")
                return render_template("register.html")

            key.is_used = True
            db.session.commit()


        user = User(username=username, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()

        flash("Cont creat cu succes!", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")


@main.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "student":
        return redirect(url_for("main.student_dashboard"))
    elif current_user.role == "profesor":
        return redirect(url_for("main.profesor_dashboard"))
    else:
        flash("Rol necunoscut. Contactați administratorul.", "danger")
        return redirect(url_for("main.login"))

@main.route("/dashboard/student")
@login_required
def student_dashboard():
    if current_user.role != "student":
        flash("Doar studenții pot accesa acest dashboard.", "danger")
        return redirect(url_for("main.dashboard"))


    courses = current_user.enrolled_courses

    return render_template("student_dashboard.html", courses=courses)

@main.route("/dashboard/profesor")
@login_required
def profesor_dashboard():

    courses = Course.query.filter_by(professor_id=current_user.id).all()
    return render_template("profesor_dashboard.html", courses=courses)

@main.route("/dashboard/profesor/create_course", methods=["GET", "POST"])
@login_required
def create_course():
    if current_user.role != "profesor":
        flash("Doar profesorii pot crea cursuri.", "danger")
        return redirect(url_for("main.profesor_dashboard"))

    if request.method == "POST":
        course_name = request.form["course_name"]
        course_description = request.form["course_description"]


        access_key = secrets.token_hex(4)


        new_course = Course(
            name=course_name,
            description=course_description,
            professor_id=current_user.id,
            access_key=access_key
        )
        db.session.add(new_course)
        db.session.commit()


        flash("Curs creat cu succes!", "success")
        return render_template("create_course.html", access_key=access_key)

    return render_template("create_course.html")

@main.route("/dashboard/profesor/add_student/<int:course_id>", methods=["GET", "POST"])
@login_required
def add_student_to_course(course_id):
    if current_user.role != "profesor":
        flash("Doar profesorii pot adăuga studenți.", "danger")
        return redirect(url_for("main.profesor_dashboard"))

    course = Course.query.get_or_404(course_id)

    if request.method == "POST":
        student_email = request.form["student_email"]
        student = User.query.filter_by(email=student_email, role="student").first()

        if not student:
            flash("Studentul cu acest email nu există sau nu este înregistrat ca student.", "danger")
        elif student in course.students:
            flash("Studentul este deja înscris la acest curs.", "warning")
        else:
            course.students.append(student)
            db.session.commit()
            flash("Student adăugat cu succes!", "success")

        return redirect(url_for("main.add_student_to_course", course_id=course.id))

    students = User.query.filter_by(role="student").all()
    return render_template("add_student.html", course=course, students=students)


@main.route("/enroll", methods=["GET", "POST"])
@login_required
def enroll():
    if current_user.role != "student":
        flash("Doar studenții se pot înrola la cursuri.", "danger")
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        access_key = request.form["access_key"]

        course = Course.query.filter_by(access_key=access_key).first()

        if not course:
            flash("Cheia de acces introdusă este invalidă.", "danger")
        elif current_user in course.students:
            flash("Ești deja înscris la acest curs.", "warning")
        else:
            course.students.append(current_user)
            db.session.commit()
            flash(f"Te-ai înscris cu succes la cursul {course.name}!", "success")
            return redirect(url_for("main.student_dashboard"))

    return render_template("enroll.html")

@main.route("/course/<int:course_id>")
@login_required
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    if current_user not in course.students and current_user.id != course.professor_id:
        flash("Nu aveți acces la acest curs.", "danger")
        return redirect(url_for("main.dashboard"))

    return render_template("course_details.html", course=course)


@socketio.on('join_room')
def handle_join(data):
    room = str(data['course_id'])
    join_room(room)
@socketio.on('send_message')
def handle_send_message(data):
    course_id = data['course_id']
    message_content = data['message']

    new_message = Message(content=message_content, course_id=course_id, user_id=current_user.id)
    db.session.add(new_message)
    db.session.commit()

    emit('new_message', {
        'username': current_user.username,
        'message': f"{current_user.username}: {message_content}",
        'timestamp': new_message.timestamp.isoformat()  # ISO8601 format
    }, room=str(course_id))

@main.route("/course/<int:course_id>/send_message", methods=["POST"])
@login_required
def send_message(course_id):
    course = Course.query.get_or_404(course_id)

    if current_user not in course.students and current_user.id != course.professor_id:
        return jsonify({"error": "Nu aveți acces la acest curs."}), 403

    message_content = request.json.get("message")
    if not message_content:
        return jsonify({"error": "Mesajul nu poate fi gol."}), 400

    new_message = Message(content=message_content, course_id=course.id, user_id=current_user.id)
    db.session.add(new_message)
    db.session.commit()

    emit('new_message', {
        'message': f"{current_user.username}: {message_content}",
        'timestamp': new_message.timestamp.strftime("%H:%M:%S")
    }, room=str(course_id), namespace='/chat', broadcast=True)

    return jsonify({"message": f"{current_user.username}: {message_content}"})

UPLOAD_FOLDER = "app/static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def send_email_notifications(course, material_name):
    professor = User.query.get(course.professor_id)
    subject = f"[Notificare nouă] Material nou la cursul {course.name}"
    body = f"""
    Salut,\n\n
    Un nou material intitulat '{material_name}' a fost încărcat la cursul {course.name} de către profesorul {professor.username}.\n
    Poți accesa materialul în platforma online.\n\n
    Succes!
    """

    for student in course.students:
        msg = MailMessage(
            subject=subject,
            sender=('gabi.vladoiu1389@gmail.com'),
            recipients=[student.email],
            body=body
        )
        mail.send(msg)

@main.route('/course/<int:course_id>/upload', methods=['POST'])
@login_required
def upload_material(course_id):
    course = Course.query.get_or_404(course_id)

    if current_user.id != course.professor_id:
        flash('Doar profesorii pot încărca materiale.', 'danger')
        return redirect(url_for('main.course_details', course_id=course.id))

    if 'material' not in request.files:
        flash('Niciun fișier selectat.', 'danger')
        return redirect(url_for('main.course_details', course_id=course.id))

    file = request.files['material']
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        file.save(upload_path)

        new_material = Material(filename=filename, course_id=course.id)
        db.session.add(new_material)
        db.session.commit()

        flash('Fișier încărcat cu succes!', 'success')


        send_email_notifications(course, filename)
    else:
        flash('Fișier invalid sau gol.', 'danger')

    return redirect(url_for('main.course_details', course_id=course.id))
@main.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Te-ai deconectat cu succes!', 'success')
    return redirect(url_for('main.login'))