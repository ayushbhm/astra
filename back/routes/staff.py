from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)
from models.model import db, User, Trek, Booking

staff_bp = Blueprint("staff", __name__)


def get_own_trek(trek_id):
    """Checks staff role + trek ownership in one place.
    Returns (trek, None) on success, or (None, error_response) on failure.
    """
    current_user = get_jwt_identity()

    if current_user["role"] != "staff":
        return None, (jsonify({"message": "Access denied"}), 403)

    trek = Trek.query.get(trek_id)

    if not trek:
        return None, (jsonify({"message": "Trek not found"}), 404)

    if trek.staff_id != current_user["id"]:
        return None, (jsonify({"message": "Not your trek"}), 403)

    return trek, None


# View assigned treks
@staff_bp.route("/treks")
@jwt_required()
def get_assigned_treks():

    current_user = get_jwt_identity()

    if current_user["role"] != "staff":
        return jsonify({"message": "Access denied"}), 403

    treks = Trek.query.filter_by(staff_id=current_user["id"]).all()

    result = [{
        "id": t.id,
        "name": t.name,
        "location": t.location,
        "difficulty": t.difficulty,
        "duration": t.duration,
        "available_slots": t.available_slots,
        "start_date": t.start_date.isoformat() if t.start_date else None,
        "end_date": t.end_date.isoformat() if t.end_date else None,
        "status": t.status,
        "registered_users": Booking.query.filter_by(trek_id=t.id, status="Booked").count()
    } for t in treks]

    return jsonify(result)




# Update slot s
@staff_bp.route("/treks/<int:id>", methods=["PUT"])
@jwt_required()
def update_trek_details(id):

    trek, error = get_own_trek(id)
    if error:
        return error

    data = request.get_json()

    if "available_slots" in data:
        if data["available_slots"] < 0:
            return jsonify({"message": "Invalid slots"}), 400
        trek.available_slots = data["available_slots"]

    if "status" in data:
        if data["status"] not in ("Open", "Closed"):
            return jsonify({"message": "Status must be Open or Closed"}), 400
        trek.status = data["status"]

    db.session.commit()
    return jsonify({"message": "Trek updated"})


#View registered users for a trek
@staff_bp.route("/treks/<int:id>/users")
@jwt_required()
def get_trek_users(id):

    trek, error = get_own_trek(id)
    if error:
        return error

    bookings = Booking.query.filter_by(trek_id=id).all()

    result = []

    for b in bookings:
        user = User.query.get(b.user_id)

        result.append({
            "booking_id": b.id,
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "status": b.status,
            "payment_status": b.payment_status
        })

    return jsonify(result)


# Mark trek as complete
@staff_bp.route("/treks/<int:id>/complete", methods=["PUT"])
@jwt_required()
def complete_trek(id):

    trek, error = get_own_trek(id)
    if error:
        return error

    trek.status = "Completed"
    db.session.commit()
    return jsonify({"message": "Trek marked as completed"})