from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models.user import create_user, find_user
import bcrypt

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    create_user(data["email"], data["password"])
    return jsonify({"msg": "User created"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = find_user(data["email"])

    if not user or not bcrypt.checkpw(data["password"].encode(), user["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user["_id"]))
    return jsonify({"token": token})
