from flask import Blueprint, request, jsonify
from services.database import SessionLocal
from services.models import Expense, Invoice, Customer, Product
from services.auth_service import register_user, login_user

def create_api_blueprint(expense_ai, invoice_ai):
    bp = Blueprint("api", __name__)

    # ---------- HEALTH ----------
    @bp.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    # ---------- AUTH ----------
    @bp.route("/auth/register", methods=["POST"])
    def register():
        return register_user(request.get_json() or {})

    @bp.route("/auth/login", methods=["POST"])
    def login():
        return login_user(request.get_json() or {})

    # ---------- EXPENSE ----------
    @bp.route("/expense/categorize", methods=["POST"])
    def categorize_expense():
        data = request.get_json() or {}
        text = data.get("text")

        if not text:
            return jsonify({"error": "text required"}), 400

        result = expense_ai.parse_expense(text)

        db = SessionLocal()
        try:
            exp = Expense(**result)
            db.add(exp)
            db.commit()
        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            db.close()

        return jsonify({"success": True, "data": result})

    return bp
