from flask import Blueprint, request, jsonify
from time import monotonic
from threading import Lock
import re
import json
from pathlib import Path
from tempfile import gettempdir
from time import time
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

GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v1/certs"


class CachedGoogleCertRequest:
    """Reuse Google's public signing certificates between login attempts."""

    def __init__(self):
        self._request = requests.Request()
        self._lock = Lock()
        self._data = None
        self._expires_at = 0
        self._cache_path = Path(gettempdir()) / "astr-google-certs.json"
        try:
            cached = json.loads(self._cache_path.read_text(encoding="utf-8"))
            self._data = cached["data"].encode("utf-8")
            seconds_until_expiry = cached["expires_at"] - time()
            self._expires_at = monotonic() + seconds_until_expiry
        except (OSError, ValueError, KeyError, TypeError):
            self._data = None

    def __call__(self, url, method="GET", **kwargs):
        if url != GOOGLE_CERTS_URL or method != "GET":
            return self._request(url, method=method, **kwargs)

        with self._lock:
            now = monotonic()
            if self._data is not None and now < self._expires_at:
                return _CachedResponse(self._data)

            try:
                # A cold start or expired cache must never block a login for
                # the browser's full timeout. Google publishes cache headers;
                # honor them, capped to one hour.
                response = self._request(url, method="GET", timeout=4)
                if response.status == 200:
                    self._data = response.data
                    cache_control = response.headers.get("cache-control", "")
                    match = re.search(r"max-age=(\d+)", cache_control)
                    max_age = int(match.group(1)) if match else 300
                    self._expires_at = now + min(max_age, 3600)
                    try:
                        self._cache_path.write_text(json.dumps({
                            "data": self._data.decode("utf-8"),
                            "expires_at": time() + min(max_age, 3600),
                        }), encoding="utf-8")
                    except OSError:
                        # Disk persistence is an optimization; in-memory
                        # certificate verification remains available.
                        pass
                    return response
            except Exception:
                # A recently cached public key set can safely cover a brief
                # Google outage; signature validation still runs per token.
                if self._data is not None and now - self._expires_at <= 3600:
                    return _CachedResponse(self._data)
                raise

            if self._data is not None and now - self._expires_at <= 3600:
                return _CachedResponse(self._data)
            return response


class _CachedResponse:
    status = 200

    def __init__(self, data):
        self.data = data


google_request = CachedGoogleCertRequest()

@auth_bp.post("/google")
def google_login():
    started_at = monotonic()
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
        print(f"Google certificate request failed after {monotonic() - started_at:.2f}s: {error}", flush=True)
        return jsonify({
            "message": "Could not reach Google to verify sign-in. Check your internet connection and try again."
        }), 503
    except Exception as error:
        # Keep the browser response safe, but retain the real reason in the
        # Flask terminal (expired token, audience mismatch, etc.).
        print(f"Google credential verification failed after {monotonic() - started_at:.2f}s: {error}", flush=True)
        return jsonify({"message": "Google credential verification failed"}), 401

    user = User.query.filter_by(
        google_id=google_user["sub"]
    ).first()
    print(f"Google credential verified after {monotonic() - started_at:.2f}s; looking up user", flush=True)

    if not user:
        user = User(
            google_id=google_user["sub"],
            email=google_user["email"],
            name=google_user.get("name", ""),
            role="user"
        )

        db.session.add(user)
        db.session.commit()
        print(f"Google user created after {monotonic() - started_at:.2f}s", flush=True)

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )
    print(f"Google login response ready after {monotonic() - started_at:.2f}s", flush=True)

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
