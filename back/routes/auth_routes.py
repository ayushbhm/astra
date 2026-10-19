from flask import Blueprint, request, jsonify
from functools import partial
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
import os
from google.auth import exceptions as google_auth_exceptions
from models.model import db, User

auth_bp = Blueprint("auth", __name__)

from google.oauth2 import id_token
from google.auth.transport import requests

# google-auth defaults certificate fetches to a 120 second timeout. Keep a
# local sign-in attempt responsive when Google cannot be reached.
google_request = partial(requests.Request(), timeout=10)

@auth_bp.post("/google")
def google_login():
    payload = request.get_json(silent=True) or {}
    credential = payload.get("credential")

    if not credential:
        return jsonify({"message": "Google credential is required"}), 400

    print("Google login POST received; verifying credential", flush=True)
    try:
        google_user = id_token.verify_oauth2_token(
            credential,
            google_request,
            os.getenv("GOOGLE_CLIENT_ID"),
            clock_skew_in_seconds=60
        )
        print("Google credential verified", flush=True)
    except google_auth_exceptions.TransportError as error:
        print(f"Google certificate request failed: {error}")
        return jsonify({
            "message": "Could not reach Google to verify sign-in. Check your internet connection and try again."
        }), 503
    except Exception as error:
        # Keep the browser response safe, but retain the real reason in the
        # Flask terminal (expired token, audience mismatch, etc.).
        print(f"Google credential verification failed: {error}")
        return jsonify({"message": "Google credential verification failed"}), 401

    user = User.query.filter_by(
        google_id=google_user["sub"]
    ).first()
    print("Google user lookup complete", flush=True)

    if not user:
        user = User(
            google_id=google_user["sub"],
            email=google_user["email"],
            name=google_user.get("name", ""),
            role="user"
        )

        db.session.add(user)
        db.session.commit()
        print("Google user created", flush=True)

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )
    print("Google login response ready", flush=True)

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
