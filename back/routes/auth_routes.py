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
    payload = request.get_json(silent=True) or {}
    credential = payload.get("credential")

    if not credential:
        return jsonify({"message": "Google credential is required"}), 400

    try:
        google_user = id_token.verify_oauth2_token(
            credential,
            requests.Request(),
            os.getenv("GOOGLE_CLIENT_ID")
        )
    except Exception as error:
        # Keep the browser response safe, but retain the real reason in the
        # Flask terminal (expired token, audience mismatch, etc.).
        print(f"Google credential verification failed: {error}")
        return jsonify({"message": "Google credential verification failed"}), 401

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

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "token": token
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
