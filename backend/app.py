from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from controllers.database import db
from controllers.config import Config
from controllers.models import User
from controllers.auth import auth_bp
from controllers.user_routes import user_bp
from controllers.admin_routes import admin_bp
from controllers.staff_routes import staff_bp
from controllers.create_initialdata import seed_data
from controllers.celery_app import init_celery


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    init_celery(app)
    JWTManager(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(staff_bp, url_prefix="/api/staff")

    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                email="admin@trekking.com",
                name="Admin",
                role="admin",
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

        seed_data()

    return app


app = create_app()

from controllers.celery_app import celery


@app.route("/")
def index():
    return jsonify({"message": "Welcome to Trekking Management API"}), 200


if __name__ == "__main__":
    app.run(debug=True)