from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from models.model import db, User, Case
from routes.user_routes import serialize_case, parse_case_data, assign_tags

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/cases", methods=["GET", "POST"])
@jwt_required()
def manage_cases():
    if not is_admin():
        return jsonify({"message": "Access denied"}), 403

    if request.method == "GET":
        return jsonify([serialize_case(case) for case in Case.query.order_by(Case.id.desc()).all()])

    data, error = parse_case_data(request.get_json(silent=True) or {})
    if error:
        return jsonify({"message": error}), 400
    case = Case(**{key: value for key, value in data.items() if key != "tags"},
                created_by=int(get_jwt_identity()),
                status=(request.get_json() or {}).get("status", "APPROVED"),
                verification_status=(request.get_json() or {}).get("verification_status", "UNVERIFIED"))
    assign_tags(case, data["tags"])
    db.session.add(case)
    db.session.commit()
    return jsonify(serialize_case(case)), 201


@admin_bp.route("/cases/<int:case_id>", methods=["PUT", "DELETE"])
@jwt_required()
def update_or_delete_case(case_id):
    if not is_admin():
        return jsonify({"message": "Access denied"}), 403
    case = Case.query.get(case_id)
    if not case:
        return jsonify({"message": "Chart not found"}), 404
    if request.method == "DELETE":
        db.session.delete(case)
        db.session.commit()
        return "", 204

    payload = request.get_json(silent=True) or {}
    data, error = parse_case_data(payload)
    if error:
        return jsonify({"message": error}), 400
    for key, value in data.items():
        if key != "tags":
            setattr(case, key, value)
    assign_tags(case, data["tags"])
    if payload.get("status") in {"PENDING", "APPROVED", "REJECTED"}:
        case.status = payload["status"]
    if payload.get("verification_status") in {"VERIFIED", "UNVERIFIED"}:
        case.verification_status = payload["verification_status"]
    db.session.commit()
    return jsonify(serialize_case(case))


@admin_bp.route("/cases/<int:case_id>/<action>", methods=["PUT"])
@jwt_required()
def moderate_case(case_id, action):
    if not is_admin():
        return jsonify({"message": "Access denied"}), 403
    case = Case.query.get(case_id)
    if not case:
        return jsonify({"message": "Chart not found"}), 404
    if action == "status":
        status = (request.get_json(silent=True) or {}).get("status")
        if status not in {"PENDING", "APPROVED", "REJECTED"}:
            return jsonify({"message": "Invalid status"}), 400
        case.status = status
    elif action == "verification":
        case.verification_status = "UNVERIFIED" if case.verification_status == "VERIFIED" else "VERIFIED"
    else:
        return jsonify({"message": "Unknown action"}), 404
    db.session.commit()
    return jsonify(serialize_case(case))


def is_admin():
    return get_jwt().get("role") == "admin"


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

    if str(user.id) == str(current_user) or (
        isinstance(current_user, dict) and user.id == current_user.get("id")
    ):
        return jsonify({
            "message": "Cannot modify yourself"
        }), 400

    user.is_active = not user.is_active

    db.session.commit()

    return jsonify({
        "message": "Status updated"
    })
