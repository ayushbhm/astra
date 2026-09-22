from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from models.model import db, User

auth_bp = Blueprint("auth", __name__)



@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    existing_user = User.query.filter_by(
        email=data["email"]
    ).first()

    if existing_user:
        return jsonify({
            "message": "Email already exists"
        }), 400

    user = User(
        name=data["name"],
        email=data["email"],
        password=data["password"],
        phone=data["phone"],
        role="user"
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Registration successful"
    }), 201






@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    user = User.query.filter_by(
        email=data["email"]
    ).first()

    if not user:
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if not user.is_active:
        return jsonify({
            "message": "Account disabled"
        }), 403

    if user.password != data["password"]:
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    token = create_access_token(
        identity={
            "id": user.id,
            "role": user.role
        }
    )

    return jsonify({
        "token": token,
        "role": user.role,
        "name": user.name
    }), 200


@auth_bp.route("/me")
@jwt_required()
def me():

    current_user = get_jwt_identity()

    return jsonify(current_user)