from flask import Blueprint, request, jsonify, session, url_for, redirect
from datetime import datetime, timedelta
import time
import random
import os
from services.database import SessionLocal
from services.models import Expense, Invoice, Customer, Product, User
from services.auth_service import register_user, login_user
from services.auth_utils import decode_access_token, create_access_token
import re
from authlib.integrations.flask_client import OAuth


def get_current_user():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    try:
        return decode_access_token(token)
    except:
        return None


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

    @bp.route("/auth/google", methods=["POST"])
    def google_auth():
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        data = request.get_json() or {}
        credential = data.get("credential")
        
        if not credential:
            return jsonify({"error": "Missing credential"}), 400

        GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        
        try:
            # Verify the Google token
            idinfo = id_token.verify_oauth2_token(
                credential, 
                google_requests.Request(), 
                GOOGLE_CLIENT_ID
            )

            # Get user info from token
            google_id = idinfo["sub"]
            email = idinfo.get("email")
            name = idinfo.get("name", "User")

            db = SessionLocal()
            try:
                # Check if user already exists
                user = db.query(User).filter(User.google_id == google_id).first()
                
                if not user:
                    # Check if user exists with this email
                    user = db.query(User).filter(User.email == email).first()
                    if user:
                        # Link Google account to existing user
                        user.google_id = google_id
                    else:
                        # Create new user
                        # Generate a random password (not used for Google login)
                        import secrets
                        random_password = secrets.token_urlsafe(16)
                        
                        user = User(
                            name=name,
                            email=email,
                            password_hash=random_password,  # Placeholder
                            google_id=google_id
                        )
                        db.add(user)
                    db.commit()
                    db.refresh(user)

                # Create access token for our app
                access_token = create_access_token(user.id)

                return jsonify({
                    "success": True,
                    "token": access_token,
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email
                    }
                })
            finally:
                db.close()

        except ValueError as e:
            return jsonify({"error": "Invalid Google token"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

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

            # Build detailed context string
            context = "Here is the user's complete financial data:\n\n"
            
            if expenses:
                context += "=== EXPENSES ===\n"
                for e in expenses:
                    context += f"- {e.original_text} | Amount: ₹{e.amount} | Category: {e.category} | Date: {e.date}\n"
            
            if invoices:
                context += "\n=== INVOICES ===\n"
                for i in invoices:
                    context += f"- Invoice #: {i.invoice_number} | Amount: ₹{i.total} | Status: {i.status} | Date: {i.issue_date}\n"
            
            if customers:
                context += "\n=== CUSTOMERS ===\n"
                for c in customers:
                    context += f"- Name: {c.name} | Email: {c.email or 'N/A'} | Phone: {c.phone or 'N/A'}\n"
            
            if products:
                context += "\n=== PRODUCTS ===\n"
                for p in products:
                    context += f"- Name: {p.name} | SKU: {p.sku or 'N/A'} | Price: ₹{p.unit_price}\n"

            # If Gemini is available, use it with a better system prompt!
            if gemini_client:
                system_prompt = """You are LedgerLink AI, a highly helpful financial assistant for the LedgerLink ERP system.

Your capabilities:
- Answer questions about the user's expenses, invoices, customers, and products
- Calculate totals, averages, counts
- Provide financial insights and summaries
- Be friendly, professional, and concise
- Always use Indian Rupees (₹) for currency
- If data isn't available, politely inform the user and suggest what data they can add
- You can also have natural conversations and explain financial concepts
- Help users understand their business finances better

Guidelines:
- Be conversational and engaging
- Use bullet points for lists
- Keep responses clear and easy to understand
- You can acknowledge if you don't have specific data, but offer alternatives
- Always respond helpfully"""

                try:
                    response = gemini_client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=f"{system_prompt}\n\n{context}\n\nUser: {query}\n\nLedgerLink AI:"
                    )
                    return jsonify({"response": response.text.strip()})
                except Exception as e:
                    print("Gemini error:", str(e))
                    # Fallback to enhanced rule-based if Gemini fails

            # ENHANCED Rule-based fallback - much smarter!
            query_lower = query.lower()
            now = datetime.utcnow()

            # Helper: get date range
            def get_date_range():
                if any(term in query_lower for term in ["last month", "previous month"]):
                    if now.month == 1:
                        start = datetime(now.year - 1, 12, 1)
                        end = datetime(now.year, 1, 1)
                    else:
                        start = datetime(now.year, now.month - 1, 1)
                        end = datetime(now.year, now.month, 1)
                    return start, end, "last month"
                elif any(term in query_lower for term in ["this month", "current month"]):
                    start = datetime(now.year, now.month, 1)
                    end = datetime(now.year + 1, now.month, 1) if now.month == 12 else datetime(now.year, now.month + 1, 1)
                    return start, end, "this month"
                elif any(term in query_lower for term in ["this year", "current year"]):
                    start = datetime(now.year, 1, 1)
                    end = datetime(now.year + 1, 1, 1)
                    return start, end, "this year"
                elif any(term in query_lower for term in ["today"]):
                    start = datetime(now.year, now.month, now.day)
                    end = datetime(now.year, now.month, now.day + 1)
                    return start, end, "today"
                else:
                    # Default to this year
                    start = datetime(now.year, 1, 1)
                    end = datetime(now.year + 1, 1, 1)
                    return start, end, "this year"

            # Helper: format currency
            def format_currency(amount):
                return f"₹{amount:.2f}"

            # Detect intent with more keywords
            greeting_words = ["hi", "hello", "hey", "how are you", "good morning", "good afternoon", "good evening", "greetings"]
            thanks_words = ["thank", "thanks", "thx", "great", "awesome", "nice", "perfect"]
            help_words = ["help", "what can you do", "capabilities", "what do you know", "how do you work"]
            expense_words = ["expense", "expenses", "spend", "spent", "spending", "cost", "costs", "payment", "payments"]
            invoice_words = ["invoice", "invoices", "bill", "bills", "sale", "sales", "revenue", "income"]
            pending_words = ["pending", "unpaid", "outstanding"]
            paid_words = ["paid", "completed", "done"]
            count_words = ["how many", "number of", "count", "total number"]
            total_words = ["total", "sum", "how much", "total amount"]
            average_words = ["average", "avg", "mean"]
            max_words = ["highest", "maximum", "most expensive", "largest", "biggest"]
            min_words = ["lowest", "minimum", "cheapest", "smallest"]
            customer_words = ["customer", "customers", "client", "clients"]
            product_words = ["product", "products", "item", "items", "inventory"]
            dashboard_words = ["dashboard", "overview", "summary", "report", "analytics", "insights"]
            profit_words = ["profit", "profits", "gain", "gains", "earnings", "net", "balance"]

            # Extract category with more options
            category = None
            category_keywords = {
                "food": ["food", "meal", "meals", "restaurant", "canteen", "lunch", "dinner", "breakfast", "snack", "snacks"],
                "travel": ["travel", "transport", "transportation", "cab", "taxi", "flight", "train", "bus", "fuel", "petrol", "diesel"],
                "office": ["office", "supplies", "stationery", "equipment", "furniture", "computer", "laptop", "printer"],
                "salary": ["salary", "wages", "payroll", "employee", "employees", "staff"],
                "marketing": ["marketing", "advertisement", "ads", "promotion", "marketing"],
                "rent": ["rent", "lease", "rental"],
                "utilities": ["utility", "utilities", "electricity", "water", "internet", "phone", "mobile"],
                "insurance": ["insurance", "insurances"],
                "maintenance": ["maintenance", "repair", "repairs", "service"],
                "tax": ["tax", "taxes", "gst", "vat"]
            }

            for cat, keywords in category_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    category = cat
                    break

            # Check greeting
            if any(word in query_lower for word in greeting_words):
                responses = [
                    "Hello! I'm LedgerLink AI! How can I help you with your finances today?",
                    "Hi there! Ready to help with your expenses, invoices, or anything financial!",
                    "Hey! Great to hear from you. What would you like to know about your business finances?"
                ]
                response = random.choice(responses)
                return jsonify({"response": response})

            # Check thanks
            elif any(word in query_lower for word in thanks_words):
                responses = [
                    "You're welcome! Happy to help! Is there anything else you'd like to know?",
                    "My pleasure! Let me know if you need anything else!",
                    "Glad I could help! Feel free to ask if you have more questions!"
                ]
                response = random.choice(responses)
                return jsonify({"response": response})

            # Check help
            elif any(word in query_lower for word in help_words):
                response = """I'm LedgerLink AI, your financial assistant! Here's what I can help with:

📊 **Financial Queries:**
• Expenses: total, count, by category, date ranges
• Invoices: total, count, pending, paid
• Customers & Products: counts and details
• Dashboard: overview and summaries
• Profit calculations

💡 **Try asking:**
• "What are my total expenses this month?"
• "How many pending invoices do I have?"
• "Show me my dashboard overview"
• "What's my total revenue this year?"

How can I assist you today?"""
                return jsonify({"response": response})

            # Get date range
            start_date, end_date, period = get_date_range()

            # Handle expenses
            if any(word in query_lower for word in expense_words):
                query_filter = [Expense.user_id == user_id, Expense.date >= start_date, Expense.date < end_date]
                if category:
                    query_filter.append(Expense.category.ilike(f"%{category}%"))
                
                filtered_expenses = db.query(Expense).filter(*query_filter).all()
                total = sum(e.amount for e in filtered_expenses)
                count = len(filtered_expenses)
                
                if count == 0:
                    response = f"You don't have any {category + ' ' if category else ''}expenses {period}."
                elif any(word in query_lower for word in count_words):
                    response = f"You have {count} {category + ' ' if category else ''}expense(s) {period}."
                elif any(word in query_lower for word in max_words) and count > 0:
                    max_exp = max(filtered_expenses, key=lambda x: x.amount)
                    response = f"Your highest {category + ' ' if category else ''}expense {period} is {format_currency(max_exp.amount)} - {max_exp.original_text}"
                elif any(word in query_lower for word in min_words) and count > 0:
                    min_exp = min(filtered_expenses, key=lambda x: x.amount)
                    response = f"Your lowest {category + ' ' if category else ''}expense {period} is {format_currency(min_exp.amount)} - {min_exp.original_text}"
                elif any(word in query_lower for word in average_words) and count > 0:
                    avg = total / count
                    response = f"Your average {category + ' ' if category else ''}expense {period} is {format_currency(avg)} across {count} expenses."
                elif category:
                    response = f"You spent {format_currency(total)} on {category} {period} across {count} expense(s)."
                else:
                    response = f"Your total expenses {period} are {format_currency(total)} across {count} expense(s)."
            
            # Handle invoices
            elif any(word in query_lower for word in invoice_words):
                query_filter = [Invoice.user_id == user_id]
                status_text = ""
                
                if any(word in query_lower for word in pending_words):
                    query_filter.append(Invoice.status == "Pending")
                    status_text = "pending"
                elif any(word in query_lower for word in paid_words):
                    query_filter.append(Invoice.status == "Paid")
                    status_text = "paid"
                
                filtered_invoices = db.query(Invoice).filter(*query_filter).all()
                total = sum(i.total for i in filtered_invoices)
                count = len(filtered_invoices)
                
                if count == 0:
                    response = f"You don't have any {status_text + ' ' if status_text else ''}invoices."
                elif any(word in query_lower for word in count_words):
                    response = f"You have {count} {status_text + ' ' if status_text else ''}invoice(s)."
                elif any(word in query_lower for word in max_words) and count > 0:
                    max_inv = max(filtered_invoices, key=lambda x: x.total)
                    response = f"Your largest {status_text + ' ' if status_text else ''}invoice is {format_currency(max_inv.total)} - {max_inv.invoice_number}"
                elif any(word in query_lower for word in min_words) and count > 0:
                    min_inv = min(filtered_invoices, key=lambda x: x.total)
                    response = f"Your smallest {status_text + ' ' if status_text else ''}invoice is {format_currency(min_inv.total)} - {min_inv.invoice_number}"
                elif any(word in query_lower for word in average_words) and count > 0:
                    avg = total / count
                    response = f"Your average {status_text + ' ' if status_text else ''}invoice is {format_currency(avg)} across {count} invoices."
                else:
                    response = f"Your {status_text + ' ' if status_text else ''}invoices total {format_currency(total)} across {count} invoice(s)."
            
            # Handle customers
            elif any(word in query_lower for word in customer_words):
                if len(customers) == 0:
                    response = "You don't have any customers yet. You can add customers from the Customers page!"
                elif any(word in query_lower for word in count_words):
                    response = f"You have {len(customers)} customer(s)."
                else:
                    customer_list = "\n".join([f"• {c.name}" for c in customers[:5]])
                    if len(customers) > 5:
                        customer_list += f"\n... and {len(customers) - 5} more"
                    response = f"You have {len(customers)} customer(s):\n{customer_list}"
            
            # Handle products
            elif any(word in query_lower for word in product_words):
                if len(products) == 0:
                    response = "You don't have any products yet. You can add products from the Products page!"
                elif any(word in query_lower for word in count_words):
                    response = f"You have {len(products)} product(s)."
                else:
                    product_list = "\n".join([f"• {p.name} - {format_currency(p.unit_price)}" for p in products[:5]])
                    if len(products) > 5:
                        product_list += f"\n... and {len(products) - 5} more"
                    response = f"You have {len(products)} product(s):\n{product_list}"
            
            # Handle profit
            elif any(word in query_lower for word in profit_words):
                total_expenses = sum(e.amount for e in expenses)
                total_invoices = sum(i.total for i in invoices)
                profit = total_invoices - total_expenses
                
                if profit >= 0:
                    response = f"💰 Your profit is {format_currency(profit)}\n\nBreakdown:\n• Total Revenue: {format_currency(total_invoices)}\n• Total Expenses: {format_currency(total_expenses)}"
                else:
                    response = f"📉 Your net loss is {format_currency(abs(profit))}\n\nBreakdown:\n• Total Revenue: {format_currency(total_invoices)}\n• Total Expenses: {format_currency(total_expenses)}"
            
            # Handle dashboard/overview
            elif any(word in query_lower for word in dashboard_words):
                total_expenses = sum(e.amount for e in expenses)
                total_invoices = sum(i.total for i in invoices)
                profit = total_invoices - total_expenses
                
                response = f"""📊 **LedgerLink Dashboard Overview:\n\n💸 Total Expenses: {format_currency(total_expenses)}\n💰 Total Invoices: {format_currency(total_invoices)}\n💼 Profit: {format_currency(profit)}\n👥 Customers: {len(customers)}\n📦 Products: {len(products)}"""
            
            # Default friendly fallback
            else:
                responses = [
                    "I'm here to help! Try asking about your expenses, invoices, customers, or try 'help' to see what I can do!",
                    "Great question! I can help with expenses, invoices, and more. Ask 'help' for options!",
                    "I'd love to assist! Try asking about your financial data or say 'help' to see all options!"
                ]
                response = random.choice(responses)

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

    # ---------- GOOGLE OAUTH ----------
    oauth = OAuth()

    # Initialize Google OAuth client
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if google_client_id and google_client_secret:
        oauth.register(
            name='google',
            client_id=google_client_id,
            client_secret=google_client_secret,
            access_token_url='https://accounts.google.com/o/oauth2/token',
            access_token_params=None,
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            authorize_params=None,
            api_base_url='https://www.googleapis.com/oauth2/v1/',
            client_kwargs={'scope': 'openid email profile'},
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
        )

    @bp.route("/auth/google/login", methods=["GET"])
    def google_login():
        if not google_client_id or not google_client_secret:
            return jsonify({"error": "Google OAuth not configured"}), 500
        
        redirect_uri = url_for('api.google_callback', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)

    @bp.route("/auth/google/callback", methods=["GET"])
    def google_callback():
        if not google_client_id or not google_client_secret:
            return jsonify({"error": "Google OAuth not configured"}), 500
        
        try:
            token = oauth.google.authorize_access_token()
            user_info = token.get('userinfo')
            
            if not user_info or not user_info.get('email'):
                return jsonify({"error": "Failed to get user info from Google"}), 400
            
            email = user_info['email']
            google_id = user_info.get('sub')
            
            db = SessionLocal()
            try:
                # Check if user exists
                user = db.query(User).filter(User.email == email).first()
                
                if user:
                    # User exists, update google_id if not set
                    if not user.google_id and google_id:
                        user.google_id = google_id
                        db.commit()
                else:
                    # Create new user
                    user = User(
                        email=email,
                        google_id=google_id,
                        password_hash=None
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                
                # Create access token
                access_token = create_access_token(user.id)
                
                # For frontend integration, we can redirect with token in query param
                # or return JSON (we'll do both for flexibility)
                frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
                
                # Return both options: redirect and JSON
                return jsonify({
                    "success": True,
                    "token": access_token,
                    "user": {
                        "id": user.id,
                        "email": user.email
                    },
                    "redirect_url": f"{frontend_url}?token={access_token}"
                })
                
            finally:
                db.close()
                
        except Exception as e:
            print("Google OAuth error:", str(e))
            return jsonify({"error": "Google authentication failed"}), 500



    return bp
