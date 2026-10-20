from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from models.model import Case
from routes.user_routes import serialize_case
from search.indexer import sync_case_index
from search.providers import SearchProviderError
from search.registry import search_cases


search_bp = Blueprint("admin_search", __name__)


def _require_admin():
    return get_jwt().get("role") == "admin"


@search_bp.post("/index")
@jwt_required()
def index_cases():
    if not _require_admin():
        return jsonify({"message": "Access denied"}), 403
    try:
        return jsonify(sync_case_index())
    except SearchProviderError as error:
        return jsonify({"message": str(error)}), 503


@search_bp.post("")
@jwt_required()
def semantic_search():
    if not _require_admin():
        return jsonify({"message": "Access denied"}), 403
    query = str((request.get_json(silent=True) or {}).get("query", "")).strip()
    if not query:
        return jsonify({"message": "Enter a search question."}), 400
    if len(query) > 500:
        return jsonify({"message": "Search questions must be 500 characters or fewer."}), 400

    try:
        cases = Case.query.order_by(Case.id.desc()).all()
        plan, matches = search_cases(query, cases)
        return jsonify({
            "intent": plan.get("intent", "semantic_chart_search"),
            "results": [
                {**serialize_case(item["case"]), "search_score": item["score"], "match_scores": item["matches"]}
                for item in matches[:200]
            ],
        })
    except SearchProviderError as error:
        return jsonify({"message": str(error)}), 503
