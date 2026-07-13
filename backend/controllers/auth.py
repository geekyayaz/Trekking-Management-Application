from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

from controllers.database import db
from controllers.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Registration credentials are required"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not username or not email or not password:
        return jsonify({"message": "Username, email and password are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    user = User(
        username=username,
        email=email,
        name=name,
        role="user",
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registration successful"}), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Login credentials are required"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid username or password"}), 401

    if not user.active or user.blacklisted:
        return jsonify({"message": "This account has been deactivated"}), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role},
    )

    return jsonify({
        "message": "Login successful",
        "data": {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "access_token": access_token,
        }
    }), 200


@auth_bp.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password) and user.role == "admin":
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role},
        )
        return jsonify({
            "message": "Admin login successful",
            "data": {
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "access_token": access_token,
            }
        }), 200

    return jsonify({"message": "Invalid admin credentials"}), 401


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify({"message": "Logout successful"}), 200