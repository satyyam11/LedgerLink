from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

from services.init_db import init_db
from services.expense_ai import ExpenseAI
from services.invoice_ai import InvoiceAI
from routes.api import create_api_blueprint

app = Flask(__name__)

CORS(
    app,
    resources={r"/api/*": {
        "origins": [
            "http://localhost:5173",
            "http://localhost:3000",
            "https://ledger-link-theta.vercel.app"
        ]
    }},
    supports_credentials=True
)

print("🚀 Loading AI models...")
expense_ai = ExpenseAI()
invoice_ai = InvoiceAI()
print("✅ AI models ready!")

print("🗄️ Initializing database...")
init_db()
print("📦 Database ready!")

api_bp = create_api_blueprint(expense_ai, invoice_ai)
app.register_blueprint(api_bp, url_prefix="/api")

@app.route("/")
def home():
    return {"message": "LedgerLink Backend Running"}

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
