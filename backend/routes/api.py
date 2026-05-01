from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import time
from services.database import SessionLocal
from services.models import Expense, Invoice, Customer, Product
from services.auth_service import register_user, login_user
from services.auth_utils import decode_access_token
import re


def get_current_user():
    # Demo mode: always return user 1 for presentation
    return 1


def create_api_blueprint(expense_ai, invoice_ai, gemini_client=None):
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

    # ---------- CHATBOT ----------
    @bp.route("/chatbot/query", methods=["POST"])
    def chatbot_query():
        user_id = get_current_user()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}
        query = data.get("query", "")

        db = SessionLocal()
        try:
            # Get all user's data for context
            expenses = db.query(Expense).filter(Expense.user_id == user_id).all()
            invoices = db.query(Invoice).filter(Invoice.user_id == user_id).all()
            customers = db.query(Customer).filter(Customer.user_id == user_id).all()
            products = db.query(Product).filter(Product.user_id == user_id).all()

            # Build context string
            context = "Here is the user's financial data:\n\n"
            
            if expenses:
                context += "EXPENSES:\n"
                for e in expenses:
                    context += f"- {e.original_text} | ₹{e.amount} | {e.category} | {e.date}\n"
            
            if invoices:
                context += "\nINVOICES:\n"
                for i in invoices:
                    context += f"- {i.invoice_number} | ₹{i.total} | {i.status} | {i.issue_date}\n"
            
            if customers:
                context += f"\nCUSTOMERS: {len(customers)} total\n"
            
            if products:
                context += f"\nPRODUCTS: {len(products)} total\n"

            # If Gemini is available, use it!
            if gemini_client:
                system_prompt = """You are a helpful financial assistant for LedgerLink, an AI-based ERP system. 
Answer the user's questions using only the provided financial data. 
Be friendly, concise, and professional. Use Indian Rupees (₹) for currency.
If the data isn't available, politely say so and suggest what data they might want to add."""

                try:
                    response = gemini_client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=f"{system_prompt}\n\n{context}\n\nUser question: {query}"
                    )
                    return jsonify({"response": response.text.strip()})
                except Exception as e:
                    print("Gemini error:", str(e))
                    # Fallback to rule-based if Gemini fails

            # Rule-based fallback
            response = "I'm sorry, I don't understand that question. Try asking about expenses, invoices, or totals!"
            query_lower = query.lower()
            now = datetime.utcnow()

            # Helper: get date range
            def get_date_range():
                if "last month" in query_lower:
                    if now.month == 1:
                        start = datetime(now.year - 1, 12, 1)
                        end = datetime(now.year, 1, 1)
                    else:
                        start = datetime(now.year, now.month - 1, 1)
                        end = datetime(now.year, now.month, 1)
                    return start, end, "last month"
                elif "this month" in query_lower:
                    start = datetime(now.year, now.month, 1)
                    end = datetime(now.year + 1, now.month, 1) if now.month == 12 else datetime(now.year, now.month + 1, 1)
                    return start, end, "this month"
                else:
                    start = datetime(now.year, 1, 1)
                    end = datetime(now.year + 1, 1, 1)
                    return start, end, "this year"

            # Detect intent
            is_expense_query = any(word in query_lower for word in ["expense", "expenses", "spend", "spent", "spending"])
            is_invoice_query = any(word in query_lower for word in ["invoice", "invoices"])
            is_pending_query = "pending" in query_lower
            is_paid_query = "paid" in query_lower
            is_count_query = any(word in query_lower for word in ["how many", "number of", "count"])
            
            # Extract category
            category = None
            if "food" in query_lower:
                category = "food"
            elif "travel" in query_lower or "transport" in query_lower:
                category = "travel"
            elif "office" in query_lower or "supplies" in query_lower:
                category = "office"

            start_date, end_date, period = get_date_range()

            # Handle expenses
            if is_expense_query:
                query_filter = [Expense.user_id == user_id, Expense.date >= start_date, Expense.date < end_date]
                if category:
                    query_filter.append(Expense.category.ilike(f"%{category}%"))
                
                expenses = db.query(Expense).filter(*query_filter).all()
                total = sum(e.amount for e in expenses)
                
                if is_count_query:
                    response = f"You have {len(expenses)} expense(s) {period}."
                elif category:
                    response = f"You spent ₹{total:.2f} on {category} {period}."
                else:
                    response = f"Your total expenses {period} are ₹{total:.2f}."
            
            # Handle invoices
            elif is_invoice_query:
                query_filter = [Invoice.user_id == user_id]
                
                if is_pending_query:
                    query_filter.append(Invoice.status == "Pending")
                    status_text = "pending"
                elif is_paid_query:
                    query_filter.append(Invoice.status == "Paid")
                    status_text = "paid"
                else:
                    status_text = ""
                
                invoices = db.query(Invoice).filter(*query_filter).all()
                total = sum(i.total for i in invoices)
                
                if is_count_query:
                    response = f"You have {len(invoices)} {status_text + ' ' if status_text else ''}invoice(s)."
                else:
                    response = f"Your {status_text + ' ' if status_text else ''}invoices total ₹{total:.2f}."
            
            # Handle customers/products
            elif "customer" in query_lower or "customers" in query_lower:
                response = f"You have {len(customers)} customer(s)."
            
            elif "product" in query_lower or "products" in query_lower:
                response = f"You have {len(products)} product(s)."
            
            # Stats overview
            elif "dashboard" in query_lower or "overview" in query_lower or "summary" in query_lower:
                total_expenses = sum(e.amount for e in expenses)
                total_invoices = sum(i.total for i in invoices)
                
                response = (f"Here's your overview: "
                          f"₹{total_expenses:.2f} total expenses, "
                          f"₹{total_invoices:.2f} total invoices, "
                          f"{len(customers)} customers, and {len(products)} products.")

            return jsonify({"response": response})

        except Exception as e:
            print("Chatbot error:", str(e))
            return jsonify({"response": "Sorry, I encountered an error. Please try again!"}), 500
        finally:
            db.close()

    # ---------- EXPENSE AI ----------
    @bp.route("/expense/categorize", methods=["POST"])
    def categorize_expense():
        user_id = get_current_user()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        start = time.time()

        data = request.get_json() or {}
        text = data.get("text")

        if not text:
            return jsonify({"error": "text required"}), 400

        print("Expense text:", text)

        result = expense_ai.parse_expense(text)

        print("Parsed result:", result)

        if not result.get("amount"):
            result["amount"] = 0

        if isinstance(result.get("date"), str) or not result.get("date"):
            result["date"] = datetime.utcnow()

        db = SessionLocal()
        try:
            exp = Expense(**result, user_id=user_id)
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
        user_id = get_current_user()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        db = SessionLocal()
        expenses = db.query(Expense).filter(Expense.user_id == user_id).all()
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
        user_id = get_current_user()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}
        text = data.get("text")

        if not text:
            return jsonify({"error": "text required"}), 400

        result = invoice_ai.parse_invoice(text)

        invoice_data = {
            "user_id": user_id,
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
        user_id = get_current_user()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        db = SessionLocal()
        invoices = db.query(Invoice).filter(Invoice.user_id == user_id).all()
        db.close()

        return jsonify([
            {
                "id": i.id,
                "invoice_number": i.invoice_number,
                "amount": i.total,
                "total": i.total,
                "currency": i.currency,
                "due": str(i.due_date),
                "due_date": str(i.due_date),
                "issue_date": str(i.issue_date),
                "status": i.status
            }
            for i in invoices
        ])

    @bp.route("/invoices/<int:invoice_id>/status", methods=["PATCH"])
    def update_invoice_status(invoice_id):
        user_id = get_current_user()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}
        status = data.get("status")
        if not status:
            return jsonify({"error": "status required"}), 400

        db = SessionLocal()
        try:
            inv = db.query(Invoice).filter(
                Invoice.id == invoice_id,
                Invoice.user_id == user_id
            ).first()
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
        user_id = get_current_user()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        db = SessionLocal()

        stats = {
            "expenses": db.query(Expense).filter(Expense.user_id == user_id).count(),
            "invoices": db.query(Invoice).filter(Invoice.user_id == user_id).count(),
            "customers": db.query(Customer).filter(Customer.user_id == user_id).count(),
            "products": db.query(Product).filter(Product.user_id == user_id).count()
        }

        db.close()

        return jsonify(stats)

    # ---------- CUSTOMERS ----------
    @bp.route("/customers", methods=["GET"])
    def get_customers():
        user_id = get_current_user()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        db = SessionLocal()
        customers = db.query(Customer).filter(Customer.user_id == user_id).all()
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
        user_id = get_current_user()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}
        name = data.get("name")
        if not name:
            return jsonify({"error": "name required"}), 400
        db = SessionLocal()
        try:
            c = Customer(
                user_id=user_id,
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
        user_id = get_current_user()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        db = SessionLocal()
        products = db.query(Product).filter(Product.user_id == user_id).all()
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
        user_id = get_current_user()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json() or {}
        name = data.get("name")
        if not name:
            return jsonify({"error": "name required"}), 400
        db = SessionLocal()
        try:
            p = Product(
                user_id=user_id,
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
