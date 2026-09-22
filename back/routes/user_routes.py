from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)
from models.model import db, User, Trek, Booking
import redis 
from  redis_decorator import cache_response


user_bp = Blueprint("user", __name__)


def current_user():
    return User.query.get(get_jwt_identity()["id"])


from tasks.trek_tasks import export_booking_history
from celery.result import AsyncResult
from flask import send_from_directory

@user_bp.route("/export-history", methods=["POST"])
@jwt_required()
def export_history():
    user_id = get_jwt_identity()["id"]
    task = export_booking_history.delay(user_id)
    return jsonify({"task_id": task.id})


@user_bp.route("/export-history/status/<task_id>")
@jwt_required()
def export_status(task_id):
    result = AsyncResult(task_id)

    if result.state == "SUCCESS":
        return jsonify({"status": "done", "filename": result.result})

    if result.state == "FAILURE":
        return jsonify({"status": "failed"})

    return jsonify({"status": "pending"})


@user_bp.route("/download-export/<filename>")
@jwt_required()
def download_export(filename):
    return send_from_directory("static/exports", filename, as_attachment=True)



@user_bp.route("/profile")
@jwt_required()
def get_profile():

    user = current_user()

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone
    })



@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():

    user = current_user()
    data = request.get_json()

    if "name" in data:
        user.name = data["name"]

    if "phone" in data:
        user.phone = data["phone"]

    if data.get("password"):
        user.password = data["password"]

    db.session.commit()
    return jsonify({"message": "Profile updated"})


#  search/ view open treks
@user_bp.route("/treks")
@jwt_required()
@cache_response(timeout=5) 
def get_treks():

    query = Trek.query.filter_by(status="Open")

    difficulty = request.args.get("difficulty")
    location = request.args.get("location")
    duration = request.args.get("duration")

    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))

    if duration:
        query = query.filter_by(duration=duration)

    treks = query.all()

    result = [{
        "id": t.id,
        "name": t.name,
        "location": t.location,
        "difficulty": t.difficulty,
        "duration": t.duration,
        "available_slots": t.available_slots,
        "start_date": t.start_date.isoformat() if t.start_date else None,
        "end_date": t.end_date.isoformat() if t.end_date else None
    } for t in treks]

    return jsonify(result)

@user_bp.route("/treks/<int:id>/book", methods=["POST"])
@jwt_required()
def book_trek(id):

    trek = Trek.query.get(id)

    if not trek:
        return jsonify({"message": "Trek not found"}), 404

    if trek.status != "Open":
        return jsonify({"message": "Trek is not open for booking"}), 400

    if trek.available_slots is None or trek.available_slots <= 0:
        return jsonify({"message": "No slots available"}), 400

    user_id = get_jwt_identity()["id"]

    existing = Booking.query.filter_by(
        user_id=user_id,
        trek_id=id,
        status="Booked"
    ).first()

    if existing:
        return jsonify({"message": "Already booked this trek"}), 400

    updated = Trek.query.filter(
        Trek.id == id,
        Trek.available_slots > 0
    ).update({Trek.available_slots: Trek.available_slots - 1})

    if not updated:
        db.session.rollback()
        return jsonify({"message": "No slots available"}), 400

    booking = Booking(user_id=user_id, trek_id=id)
    db.session.add(booking)
    db.session.commit()

    return jsonify({"message": "Trek booked"})


# View booking statu

@user_bp.route("/bookings")
@jwt_required()
def get_bookings():

    user_id = get_jwt_identity()["id"]

    bookings = Booking.query.filter_by(user_id=user_id).all()
    trek_ids = [b.trek_id for b in bookings]
    treks = {t.id: t for t in Trek.query.filter(Trek.id.in_(trek_ids)).all()}

    result = []

    for b in bookings:
        trek = treks[b.trek_id]

        result.append({
            "booking_id": b.id,
            "trek_id": b.trek_id,
            "trek_name": trek.name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration": trek.duration,
            "start_date": trek.start_date.isoformat() if trek.start_date else None,
            "end_date": trek.end_date.isoformat() if trek.end_date else None,
            "status": b.status,
            "booking_date": b.booking_date.isoformat() if b.booking_date else None
        })

    return jsonify(result)


# Cancel a booking
@user_bp.route("/bookings/<int:id>/cancel", methods=["PUT"])
@jwt_required()
def cancel_booking(id):

    user_id = get_jwt_identity()["id"]

    booking = Booking.query.get(id)

    if not booking or booking.user_id != user_id:
        return jsonify({"message": "Booking not found"}), 404

    if booking.status != "Booked":
        return jsonify({"message": "Booking cannot be cancelled"}), 400

    booking.status = "Cancelled"

    Trek.query.filter(Trek.id == booking.trek_id).update(
        {Trek.available_slots: Trek.available_slots + 1}
    )

    db.session.commit()

    return jsonify({"message": "Booking cancelled"})

