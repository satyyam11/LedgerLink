from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

from services.init_db import init_db
from services.expense_ai import ExpenseAI
from services.invoice_ai import InvoiceAI
from routes.api import create_api_blueprint
from services.database import SessionLocal
from services.models import User

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-me-in-production")

CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    supports_credentials=True
)

print("Starting LedgerLink Backend...")

# Initialize Gemini AI
gemini_client = None
try:
    import google.genai as genai
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        print("Gemini AI initialized!")
    else:
        print("GEMINI_API_KEY not found in .env, chatbot will use rule-based mode.")
except ImportError:
    print("google-genai not installed, chatbot will use rule-based mode.")
except Exception as e:
    print(f"Error initializing Gemini: {e}, chatbot will use rule-based mode.")

print("Loading AI models...")
expense_ai = ExpenseAI()
invoice_ai = InvoiceAI()
print("AI models ready!")

print("Initializing database...")
init_db()
print("Database ready!")

print("Creating demo user...")
db = SessionLocal()
try:
    from services.auth_utils import hash_password
    demo_user = db.query(User).filter(User.id == 1).first()
    if not demo_user:
        demo_user = User(
            name="Demo User",
            email="demo@ledgerlink.com",
            password_hash=hash_password("demo123")
        )
        db.add(demo_user)
        db.commit()
        print("Demo user created!")
    else:
        print("Demo user already exists!")
finally:
    db.close()

api_bp = create_api_blueprint(expense_ai, invoice_ai, gemini_client)
app.register_blueprint(api_bp, url_prefix="/api")


@app.route("/")
def home():
    return {"message": "LedgerLink Backend Running"}


if __name__ == "__main__":
    app.run(port=5000, debug=True)
