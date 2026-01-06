# backend/app.py
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

from services.init_db import init_db
from services.expense_ai import ExpenseAI
from services.invoice_ai import InvoiceAI

from routes.api import create_api_blueprint

# Create the app
app = Flask(__name__)
CORS(app)

print("🚀 Loading AI models...")
expense_ai = ExpenseAI()
invoice_ai = InvoiceAI()
print("✅ AI models ready!")

print("🗄️ Initializing database...")
init_db()
print("📦 Database ready!")

# Register routes blueprint
api_bp = create_api_blueprint(expense_ai, invoice_ai)
app.register_blueprint(api_bp, url_prefix="/api")

@app.route("/")
def home():
    return {"message": "LedgerLink Backend Running"}

if __name__ == "__main__":
    print("🌍 Backend running at http://localhost:5000")
    app.run(debug=True, port=5000)
