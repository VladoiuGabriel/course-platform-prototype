from flask import Blueprint, request, jsonify
from app import db
from app.models import Course
from flask_login import login_required, current_user

courses_bp = Blueprint("courses", __name__)

@courses_bp.route("/create", methods=["POST"])
@login_required
def create_course():
    if current_user.role != "profesor":
        return jsonify({"error": "Doar profesorii pot crea cursuri"}), 403

    data = request.json
    new_course = Course(name=data["name"], description=data["description"], professor_id=current_user.id)
    db.session.add(new_course)
    db.session.commit()
    return jsonify({"message": "Curs creat cu succes!"})
