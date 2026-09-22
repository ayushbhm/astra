from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from routes.auth_routes import  auth_bp
from models.model import db

from dotenv import load_dotenv
load_dotenv()
app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)


app.register_blueprint(auth_bp)
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

   




if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )