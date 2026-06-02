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

# Initialize Cloudinary
cloudinary_config = None
try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")
    if CLOUDINARY_URL:
        cloudinary.config(cloudinary_url=CLOUDINARY_URL)
        print("Cloudinary initialized!")
    else:
        print("CLOUDINARY_URL not found, receipt upload disabled.")
        cloudinary_config = False
except ImportError:
    print("cloudinary not installed, receipt upload disabled.")
    cloudinary_config = False
except Exception as e:
    print(f"Error initializing Cloudinary: {e}, receipt upload disabled.")
    cloudinary_config = False

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

print("Running database migrations...")
try:
    from migrate_add_user_name import migrate
    migrate()
    print("Migrations complete!")
except Exception as e:
    print(f"Migration warning: {e}")



api_bp = create_api_blueprint(expense_ai, invoice_ai, gemini_client, cloudinary_config)
app.register_blueprint(api_bp, url_prefix="/api")


@app.route("/")
def home():
    return {"message": "LedgerLink Backend Running"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
