from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)
from datetime import datetime
import re
from models.model import db, Case, Tag


user_bp = Blueprint("user", __name__)

MAX_CASES_PER_USER = 5


def current_user_id():
    return int(get_jwt_identity())


def serialize_case(case):
    return {
        "id": case.id,
        "title": case.title,
        "dob": case.dob.isoformat(),
        "tob": case.tob.strftime("%H:%M") if case.tob else "",
        "gender": case.gender,
        "place": case.place,
        "state": case.state,
        "story": case.story or "",
        "tags": [tag.name for tag in case.tags],
        "status": case.status,
        "verification_status": case.verification_status,
        "created_by": case.created_by
    }


def parse_case_data(data):
    required = ("title", "dob", "gender", "place", "state", "story")
    missing = [field for field in required if not str(data.get(field, "")).strip()]
    if missing:
        return None, f"Missing required field: {missing[0]}"

    try:
        dob = datetime.strptime(data["dob"], "%Y-%m-%d").date()
        tob = datetime.strptime(data["tob"], "%H:%M").time() if data.get("tob") else None
    except ValueError:
        return None, "Use YYYY-MM-DD for date and HH:MM for time"

    return {
        "title": data["title"].strip(), "dob": dob, "tob": tob,
        "gender": data["gender"].strip(), "place": data["place"].strip(),
        "state": data["state"].strip(), "story": data["story"].strip(),
        "tags": [str(tag).strip() for tag in data.get("tags", []) if str(tag).strip()]
    }, None


def assign_tags(case, names):
    tags = []
    for name in dict.fromkeys(names):
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "tag"
            if Tag.query.filter_by(slug=slug).first():
                slug = f"{slug}-{Tag.query.count() + 1}"
            tag = Tag(name=name, slug=slug, category="user")
            db.session.add(tag)
        tags.append(tag)
    case.tags = tags


@user_bp.get("/cases")
def public_cases():
    return jsonify([serialize_case(case) for case in Case.query.filter_by(status="APPROVED").all()])


@user_bp.get("/user/cases")
@jwt_required()
def my_cases():
    cases = Case.query.filter_by(created_by=current_user_id()).order_by(Case.id.desc()).all()
    return jsonify([serialize_case(case) for case in cases])


@user_bp.get("/user/quota")
@jwt_required()
def my_quota():
    count = Case.query.filter_by(created_by=current_user_id()).count()
    return jsonify({"count": count, "max": MAX_CASES_PER_USER, "canAdd": count < MAX_CASES_PER_USER,
                    "remaining": max(0, MAX_CASES_PER_USER - count)})


@user_bp.post("/user/cases")
@jwt_required()
def add_case():
    user_id = current_user_id()
    if Case.query.filter_by(created_by=user_id).count() >= MAX_CASES_PER_USER:
        return jsonify({"message": "Maximum of 5 charts reached"}), 400
    data, error = parse_case_data(request.get_json(silent=True) or {})
    if error:
        return jsonify({"message": error}), 400
    case = Case(**{key: value for key, value in data.items() if key != "tags"}, created_by=user_id,
                status="PENDING", verification_status="UNVERIFIED")
    assign_tags(case, data["tags"])
    db.session.add(case)
    db.session.commit()
    return jsonify(serialize_case(case)), 201


@user_bp.put("/user/cases/<int:case_id>")
@jwt_required()
def update_case(case_id):
    case = Case.query.filter_by(id=case_id, created_by=current_user_id()).first()
    if not case:
        return jsonify({"message": "Chart not found"}), 404
    data, error = parse_case_data(request.get_json(silent=True) or {})
    if error:
        return jsonify({"message": error}), 400
    for key, value in data.items():
        if key != "tags":
            setattr(case, key, value)
    assign_tags(case, data["tags"])
    case.status = "PENDING"
    case.verification_status = "UNVERIFIED"
    db.session.commit()
    return jsonify(serialize_case(case))


@user_bp.delete("/user/cases/<int:case_id>")
@jwt_required()
def delete_case(case_id):
    case = Case.query.filter_by(id=case_id, created_by=current_user_id()).first()
    if not case:
        return jsonify({"message": "Chart not found"}), 404
    db.session.delete(case)
    db.session.commit()
    return "", 204
