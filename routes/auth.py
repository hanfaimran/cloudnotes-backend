from flask import Blueprint, request, jsonify
from extensions import db
from models.models import User
import secrets

auth_bp = Blueprint("auth", __name__)

tokens = {}

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = secrets.token_hex(32)
    tokens[token] = user.id
    return jsonify({"message": "Account created", "user": user.to_dict(), "token": token}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = secrets.token_hex(32)
    tokens[token] = user.id
    return jsonify({"message": "Logged in", "user": user.to_dict(), "token": token}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    tokens.pop(token, None)
    return jsonify({"message": "Logged out"}), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user_id = tokens.get(token)
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200


def get_user_from_token(request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    return tokens.get(token)
