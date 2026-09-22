from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
import os
from models.model import db, User

auth_bp = Blueprint("auth", __name__)

from google.oauth2 import id_token
from google.auth.transport import requests

@auth_bp.post("/google")
def google_login():

    credential = request.json["credential"]
    print("GOOGLE_CLIENT_ID:", os.getenv("GOOGLE_CLIENT_ID"))

    google_user = id_token.verify_oauth2_token(
        credential,
        requests.Request(),
        os.getenv("GOOGLE_CLIENT_ID")
    )

    user = User.query.filter_by(
        google_id=google_user["sub"]
    ).first()

    if not user:
        user = User(
            google_id=google_user["sub"],
            email=google_user["email"],
            name=google_user.get("name", ""),
            role="user"
        )

        db.session.add(user)
        db.session.commit()

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role
    }




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