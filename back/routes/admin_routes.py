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
            
            "role": user.role,
            
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
