from dotenv import load_dotenv
from pathlib import Path

# Load provider keys before importing route and search modules that read them.
load_dotenv(Path(__file__).with_name('.env'), override=True)

from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from routes.auth_routes import  auth_bp
from routes.user_routes import user_bp
from routes.admin_routes import admin_bp
from routes.search_routes import search_bp
from models.model import db
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)


app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(search_bp, url_prefix="/admin/search")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trek.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "secret-key"


@app.after_request
def allow_google_identity_popup(response):
    # The Google Identity Services popup must be able to message its opener.
    # Vite sets this for development, but Flask serves the built app directly
    # in production and needs to send the same policy itself.
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
    return response

db.init_app(app)

JWTManager(app)

CORS(app)


@app.get("/health")
def health():
    """Fast readiness endpoint used by the sign-in UI."""
    try:
        with db.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return jsonify({"status": "ok"})
    except SQLAlchemyError:
        return jsonify({"status": "not_ready"}), 503


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_vue(path):
    return render_template("index.html")


with app.app_context():

    db.create_all()
    # Existing local SQLite databases predate the title/state fields.
    case_columns = {column["name"] for column in inspect(db.engine).get_columns("cases")}
    if "title" not in case_columns:
        db.session.execute(text("ALTER TABLE cases ADD COLUMN title VARCHAR(200) NOT NULL DEFAULT ''"))
    if "state" not in case_columns:
        db.session.execute(text("ALTER TABLE cases ADD COLUMN state VARCHAR(100) NOT NULL DEFAULT ''"))
    db.session.commit()

   




if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
