from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from routes.auth_routes import  auth_bp
from routes.user_routes import user_bp
from models.model import db
from sqlalchemy import inspect, text

from dotenv import load_dotenv
from pathlib import Path

# Always use the backend's Google client ID, even when Flask is started from
# the repository root or an IDE with an older environment variable set.
load_dotenv(Path(__file__).with_name('.env'), override=True)
app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)


app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trek.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "secret-key"

db.init_app(app)

JWTManager(app)

CORS(app)


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
