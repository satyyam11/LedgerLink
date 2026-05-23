from flask import jsonify
from services.database import SessionLocal
from services.models import User
from services.auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
)

def register_user(data):
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return jsonify({"error": "User already exists"}), 400

        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        token = create_access_token(user.id)

        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }), 201
    finally:
        db.close()


def login_user(data):
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()

        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid credentials"}), 401

        token = create_access_token(user.id)

        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        })
    finally:
        db.close()
