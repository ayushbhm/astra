from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)
from datetime import datetime
from models.model import (
    db,
    User,
    Trek,
    Booking
)

admin_bp = Blueprint("admin", __name__)


def is_admin():

    current_user = get_jwt_identity()

    return current_user["role"] == "admin"


# Statistics
@admin_bp.route("/stats")
@jwt_required()
def stats():

    if not is_admin():
        return jsonify({
            "message": "Access denied"
        }), 403

    return jsonify({
        "users": User.query.filter_by(
            role="user"
        ).count(),

        "staff": User.query.filter_by(
            role="staff"
        ).count(),

        "treks": Trek.query.count(),

        "bookings": Booking.query.count()
    })



@admin_bp.route("/users")
@jwt_required()
def get_users():

    if not is_admin():
        return jsonify({
            "message": "Access denied"
        }), 403

    users = User.query.all()

    result = []

    for user in users:
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "is_active": user.is_active
        })

    return jsonify(result)


@admin_bp.route("/users/<int:id>/status",
                methods=["PUT"])
@jwt_required()
def change_status(id):

    if not is_admin():
        return jsonify({
            "message": "Access denied"
        }), 403

    current_user = get_jwt_identity()

    user = User.query.get(id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    if user.id == current_user["id"]:
        return jsonify({
            "message": "Cannot modify yourself"
        }), 400

    user.is_active = not user.is_active

    db.session.commit()

    return jsonify({
        "message": "Status updated"
    })


# Create staff
@admin_bp.route("/staff",
                methods=["POST"])
@jwt_required()
def create_staff():

    if not is_admin():
        return jsonify({
            "message": "Access denied"
        }), 403

    data = request.get_json()

    if not data["name"].strip():
        return jsonify({
            "message": "Name required"
        }), 400

    if not data["email"].strip():
        return jsonify({
            "message": "Email required"
        }), 400

    if not data["password"].strip():
        return jsonify({
            "message": "Password required"
        }), 400

    existing_user = User.query.filter_by(
        email=data["email"]
    ).first()

    if existing_user:
        return jsonify({
            "message": "Email already exists"
        }), 400

    staff = User(
        name=data["name"],
        email=data["email"],
        password=data["password"],
        phone=data.get("phone"),
        role="staff"
    )

    db.session.add(staff)
    db.session.commit()

    return jsonify({
        "message": "Staff created"
    })


# Update staff
@admin_bp.route("/staff/<int:id>",
                methods=["PUT"])
@jwt_required()
def update_staff(id):

    if not is_admin():
        return jsonify({
            "message": "Access denied"
        }), 403

    staff = User.query.get(id)

    if not staff:
        return jsonify({
            "message": "Staff not found"
        }), 404

    if staff.role != "staff":
        return jsonify({
            "message": "Invalid staff"
        }), 400

    data = request.get_json()

    staff.name = data["name"]
    staff.email = data["email"]
    staff.phone = data["phone"]

    db.session.commit()

    return jsonify({
        "message": "Staff updated"
    })


# Delete staff
@admin_bp.route("/staff/<int:id>",
                methods=["DELETE"])
@jwt_required()
def delete_staff(id):

    if not is_admin():
        return jsonify({
            "message": "Access denied"
        }), 403

    staff = User.query.get(id)

    if not staff:
        return jsonify({
            "message": "Staff not found"
        }), 404

    if staff.role != "staff":
        return jsonify({
            "message": "Invalid staff"
        }), 400

    db.session.delete(staff)

    db.session.commit()

    return jsonify({
        "message": "Staff deleted"
    })


# View treks
@admin_bp.route("/treks")
@jwt_required()
def get_treks():

    if not is_admin():
        return jsonify({
            "message": "Access denied"
        }), 403

    treks = Trek.query.all()

    result = []

    for trek in treks:
        staff = User.query.get(trek.staff_id) if trek.staff_id else None
        result.append({
            "id": trek.id,
            "name": trek.name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration": trek.duration,
            "available_slots": trek.available_slots,
            "start_date": trek.start_date.isoformat() if trek.start_date else None,
            "end_date": trek.end_date.isoformat() if trek.end_date else None,
            "status": trek.status,
            "staff_id": trek.staff_id,
            "staff_name": staff.name if staff else None
        })

    return jsonify(result)



@admin_bp.route("/treks", methods=["POST"])
@jwt_required()
def create_trek():

    if not is_admin():
        return jsonify({"message": "Access denied"}), 403

    data = request.get_json()

    if not data["name"].strip():
        return jsonify({"message": "Trek name required"}), 400

    if not data["location"].strip():
        return jsonify({"message": "Location required"}), 400

    if data["available_slots"] < 0:
        return jsonify({"message": "Invalid slots"}), 400

    start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
    end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()

    if end_date < start_date:
        return jsonify({"message": "End date cannot be before start date"}), 400

    staff_id = data.get("staff_id")

    if staff_id:
        staff = User.query.get(staff_id)

        if not staff or staff.role != "staff":
            return jsonify({"message": "Invalid staff"}), 400

        if not staff.is_active:
            return jsonify({"message": "Staff account disabled"}), 400

    trek = Trek(
        name=data["name"],
        location=data["location"],
        difficulty=data["difficulty"],
        duration=data["duration"],
        available_slots=data["available_slots"],
        start_date=start_date,
        end_date=end_date,
        status=data["status"],
        staff_id=staff_id
    )

    db.session.add(trek)
    db.session.commit()

    return jsonify({"message": "Trek created"})

@admin_bp.route("/treks/<int:id>",
                methods=["PUT"])
@jwt_required()
def update_trek(id):

    if not is_admin():
        return jsonify({
            "message": "Access denied"
        }), 403

    trek = Trek.query.get(id)

    if not trek:
        return jsonify({
            "message": "Trek not found"
        }), 404

    data = request.get_json()

    if not data["name"].strip():
        return jsonify({
            "message": "Trek name required"
        }), 400

    if not data["location"].strip():
        return jsonify({
            "message": "Location required"
        }), 400

    if data["available_slots"] < 0:
        return jsonify({
            "message": "Invalid slots"
        }), 400

    if data["duration"] < 0:
        return jsonify({
            "message": "Invalid duration"
        }), 400

    start_date = datetime.strptime(
        data["start_date"],
        "%Y-%m-%d"
    ).date()

    end_date = datetime.strptime(
        data["end_date"],
        "%Y-%m-%d"
    ).date()

    if end_date < start_date:
        return jsonify({
            "message":
            "End date cannot be before start date"
        }), 400

    trek.name = data["name"]
    trek.location = data["location"]
    trek.difficulty = data["difficulty"]
    trek.duration = data["duration"]
    trek.available_slots = data["available_slots"]

    trek.start_date = start_date
    trek.end_date = end_date

    trek.status = data["status"]

    db.session.commit()

    return jsonify({
        "message": "Trek updated"
    })

# Delete trek
@admin_bp.route("/treks/<int:id>",
                methods=["DELETE"])
@jwt_required()
def delete_trek(id):

    if not is_admin():
        return jsonify({
            "message": "Access denied"
        }), 403

    trek = Trek.query.get(id)

    if not trek:
        return jsonify({
            "message": "Trek not found"
        }), 404

    db.session.delete(trek)

    db.session.commit()

    return jsonify({
        "message": "Trek deleted"
    })


# Assign staff
@admin_bp.route("/treks/<int:id>/assign",
                methods=["PUT"])
@jwt_required()
def assign_staff(id):

    if not is_admin():
        return jsonify({
            "message": "Access denied"
        }), 403

    trek = Trek.query.get(id)

    if not trek:
        return jsonify({
            "message": "Trek not found"
        }), 404

    data = request.get_json()

    staff = User.query.get(
        data["staff_id"]
    )

    if not staff:
        return jsonify({
            "message": "Staff not found"
        }), 404

    if staff.role != "staff":
        return jsonify({
            "message": "Invalid staff"
        }), 400

    if not staff.is_active:
        return jsonify({
            "message": "Staff account disabled"
        }), 400

    trek.staff_id = staff.id

    db.session.commit()

    return jsonify({
        "message": "Staff assigned"
    })


# View bookings
@admin_bp.route("/bookings")
@jwt_required()
def get_bookings():

    if not is_admin():
        return jsonify({
            "message": "Access denied"
        }), 403

    bookings = Booking.query.all()

    result = []

    for booking in bookings:
        result.append({
            "id": booking.id,
            "user_id": booking.user_id,
            "trek_id": booking.trek_id,
            "status": booking.status,
            "payment_status": booking.payment_status,
            "booking_date": booking.booking_date
        })

    return jsonify(result)

