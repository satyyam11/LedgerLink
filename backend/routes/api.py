from flask import Blueprint, request, jsonify
from datetime import datetime
import time
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

    # ---------- EXPENSE AI ----------
    @bp.route("/expense/categorize", methods=["POST"])
    def categorize_expense():
        start = time.time()

        data = request.get_json() or {}
        text = data.get("text")

        if not text:
            return jsonify({"error": "text required"}), 400

        print("Expense text:", text)

        result = expense_ai.parse_expense(text)

        print("Parsed result:", result)

        # safety fixes
        if not result.get("amount"):
            result["amount"] = 0

        if isinstance(result.get("date"), str) or not result.get("date"):
            result["date"] = datetime.utcnow()

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

        print("AI processing time:", round(time.time() - start, 3), "seconds")

        return jsonify({"success": True, "data": result})

    # ---------- GET EXPENSES ----------
    @bp.route("/expenses", methods=["GET"])
    def get_expenses():
        db = SessionLocal()
        expenses = db.query(Expense).all()
        db.close()

        return jsonify([
            {
                "id": e.id,
                "text": e.original_text,
                "category": e.category,
                "amount": e.amount,
                "vendor": e.vendor,
                "date": str(e.date)
            }
            for e in expenses
        ])

    # ---------- INVOICE AI ----------
    @bp.route("/invoice/generate", methods=["POST"])
    def generate_invoice():
        data = request.get_json() or {}
        text = data.get("text")

        if not text:
            return jsonify({"error": "text required"}), 400

        result = invoice_ai.parse_invoice(text)

        invoice_data = {
            "invoice_number": result.get("invoice_number"),
            "total": result.get("total") or result.get("amount") or 0,
            "currency": result.get("currency", "INR"),
            "issue_date": result.get("issue_date") or datetime.utcnow(),
            "due_date": result.get("due_date") or datetime.utcnow()
        }

        db = SessionLocal()
        try:
            inv = Invoice(**invoice_data)
            db.add(inv)
            db.commit()
        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            db.close()

        return jsonify({"success": True, "data": invoice_data})

    # ---------- GET INVOICES ----------
    @bp.route("/invoices", methods=["GET"])
    def get_invoices():
        db = SessionLocal()
        invoices = db.query(Invoice).all()
        db.close()

        return jsonify([
            {
                "id": i.id,
                "invoice_number": i.invoice_number,
                "amount": i.total,
                "currency": i.currency,
                "due": str(i.due_date),
                "status": i.status
            }
            for i in invoices
        ])

    @bp.route("/invoices/<int:invoice_id>/status", methods=["PATCH"])
    def update_invoice_status(invoice_id):
        data = request.get_json() or {}
        status = data.get("status")
        if not status:
            return jsonify({"error": "status required"}), 400

        db = SessionLocal()
        try:
            inv = db.query(Invoice).get(invoice_id)
            if not inv:
                return jsonify({"error": "invoice not found"}), 404
            inv.status = status
            db.commit()
            return jsonify({"success": True})
        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            db.close()

    # ---------- SYSTEM STATS ----------
    @bp.route("/stats", methods=["GET"])
    def get_stats():
        db = SessionLocal()

        stats = {
            "expenses": db.query(Expense).count(),
            "invoices": db.query(Invoice).count(),
            "customers": db.query(Customer).count(),
            "products": db.query(Product).count()
        }

        db.close()

        return jsonify(stats)

    # ---------- CUSTOMERS ----------
    @bp.route("/customers", methods=["GET"])
    def get_customers():
        db = SessionLocal()
        customers = db.query(Customer).all()
        db.close()
        return jsonify({
            "success": True,
            "data": [
                {
                    "id": c.id,
                    "name": c.name,
                    "email": c.email,
                    "phone": c.phone,
                    "address": c.address
                }
                for c in customers
            ]
        })

    @bp.route("/customers", methods=["POST"])
    def create_customer():
        data = request.get_json() or {}
        name = data.get("name")
        if not name:
            return jsonify({"error": "name required"}), 400
        db = SessionLocal()
        try:
            c = Customer(
                name=name,
                email=data.get("email"),
                phone=data.get("phone"),
                address=data.get("address"),
            )
            db.add(c)
            db.commit()
            db.refresh(c)
            return jsonify({"success": True, "data": {"id": c.id}}), 201
        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            db.close()

    # ---------- PRODUCTS ----------
    @bp.route("/products", methods=["GET"])
    def get_products():
        db = SessionLocal()
        products = db.query(Product).all()
        db.close()
        return jsonify({
            "success": True,
            "data": [
                {
                    "id": p.id,
                    "name": p.name,
                    "sku": p.sku,
                    "unit_price": p.unit_price,
                }
                for p in products
            ]
        })

    @bp.route("/products", methods=["POST"])
    def create_product():
        data = request.get_json() or {}
        name = data.get("name")
        if not name:
            return jsonify({"error": "name required"}), 400
        db = SessionLocal()
        try:
            p = Product(
                name=name,
                sku=data.get("sku"),
                unit_price=data.get("unit_price") or 0.0,
            )
            db.add(p)
            db.commit()
            db.refresh(p)
            return jsonify({"success": True, "data": {"id": p.id}}), 201
        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            db.close()

    return bp
