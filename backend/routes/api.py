# backend/routes/api.py
from flask import Blueprint, request, jsonify
from datetime import datetime 
from services.database import SessionLocal
from services.models import Expense, Invoice, Customer, Product


def create_api_blueprint(expense_ai, invoice_ai):
    """
    We pass in the AI objects from app.py so the routes can use them.
    """
    bp = Blueprint("api", __name__)

    # -------- Health --------
    @bp.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "message": "API is running"})

    # -------- Expense routes --------
    @bp.route("/expense/categorize", methods=["POST"])
    def categorize_expense():
        data = request.get_json() or {}
        text = data.get("text", "")

        if not text:
            return jsonify({"success": False, "error": "No text provided"}), 400

        # Use AI to parse
        result = expense_ai.parse_expense(text)

        # Save to DB
        db = SessionLocal()
        try:
            new_exp = Expense(**result)
            db.add(new_exp)
            db.commit()
        except Exception as e:
            db.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
        finally:
            db.close()

        return jsonify({"success": True, "data": result})

    @bp.route("/expenses", methods=["GET"])
    def get_expenses():
        db = SessionLocal()
        try:
            rows = db.query(Expense).all()
            output = []
            for r in rows:
                obj = r.__dict__.copy()
                obj.pop("_sa_instance_state", None)
                output.append(obj)
        finally:
            db.close()

        return jsonify({"success": True, "data": output})

    # -------- Invoice routes --------
    @bp.route("/invoice/generate", methods=["POST"])
    def generate_invoice():
        data = request.get_json() or {}
        text = data.get("text", "")

        if not text:
            return jsonify({"success": False, "error": "No text provided"}), 400

        # Use AI to parse natural language invoice request
        result = invoice_ai.parse_invoice_request(text)
        invoice_number = invoice_ai.generate_invoice_number()
        result["invoice_number"] = invoice_number  # send back to frontend

        # Extract values we actually store in the Invoice table
        amount = result.get("amount") or 0.0
        currency = result.get("currency", "INR")

        # issue_date and due_date are strings like 'YYYY-MM-DD' from InvoiceAI
        try:
            issue_date = datetime.strptime(result["issue_date"], "%Y-%m-%d")
        except Exception:
            issue_date = datetime.now()

        try:
            due_date = datetime.strptime(result["due_date"], "%Y-%m-%d")
        except Exception:
            due_date = None

        db = SessionLocal()
        try:
            # ✅ Only pass columns that actually exist on Invoice model
            new_invoice = Invoice(
                invoice_number=invoice_number,
                customer_id=None,   # you can later link this to a real Customer
                total=amount,
                currency=currency,
                issue_date=issue_date,
                due_date=due_date,
            )
            db.add(new_invoice)
            db.commit()
        except Exception as e:
            db.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
        finally:
            db.close()

        # You still get the full AI result on the frontend (includes original_text, etc.)
        return jsonify({"success": True, "data": result})

    @bp.route("/invoices", methods=["GET"])
    def get_invoices():
        db = SessionLocal()
        try:
            rows = db.query(Invoice).all()
            output = []
            for r in rows:
                obj = r.__dict__.copy()
                obj.pop("_sa_instance_state", None)
                output.append(obj)
        finally:
            db.close()

        return jsonify({"success": True, "data": output})

    # -------- Customer routes --------
    @bp.route("/customers", methods=["GET"])
    def list_customers():
        db = SessionLocal()
        try:
            rows = db.query(Customer).all()
            output = []
            for r in rows:
                obj = r.__dict__.copy()
                obj.pop("_sa_instance_state", None)
                output.append(obj)
        finally:
            db.close()
        return jsonify({"success": True, "data": output})

    @bp.route("/customers", methods=["POST"])
    def create_customer():
        data = request.get_json() or {}
        name = data.get("name")
        if not name:
            return jsonify({"success": False, "error": "name is required"}), 400

        db = SessionLocal()
        try:
            customer = Customer(
                name=name,
                email=data.get("email"),
                phone=data.get("phone"),
                address=data.get("address"),
            )
            db.add(customer)
            db.commit()
            db.refresh(customer)
            obj = customer.__dict__.copy()
            obj.pop("_sa_instance_state", None)
        except Exception as e:
            db.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
        finally:
            db.close()

        return jsonify({"success": True, "data": obj}), 201

    # -------- Product routes --------
    @bp.route("/products", methods=["GET"])
    def list_products():
        db = SessionLocal()
        try:
            rows = db.query(Product).all()
            output = []
            for r in rows:
                obj = r.__dict__.copy()
                obj.pop("_sa_instance_state", None)
                output.append(obj)
        finally:
            db.close()
        return jsonify({"success": True, "data": output})

    @bp.route("/products", methods=["POST"])
    def create_product():
        data = request.get_json() or {}
        name = data.get("name")
        if not name:
            return jsonify({"success": False, "error": "name is required"}), 400

        db = SessionLocal()
        try:
            product = Product(
                name=name,
                sku=data.get("sku"),
                unit_price=data.get("unit_price", 0.0),
            )
            db.add(product)
            db.commit()
            db.refresh(product)
            obj = product.__dict__.copy()
            obj.pop("_sa_instance_state", None)
        except Exception as e:
            db.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
        finally:
            db.close()

        return jsonify({"success": True, "data": obj}), 201

    return bp
