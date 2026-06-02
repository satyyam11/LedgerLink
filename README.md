# LedgerLink 🚀

LedgerLink is an **AI-powered ERP and accounting platform** designed to automate financial workflows and reduce manual accounting effort. It converts unstructured natural-language business inputs into structured financial records using machine learning and NLP.

---

## ✨ Features

### 🤖 AI-Powered Features
- **AI Expense Interpretation**: Converts inputs like *“Paid ₹2500 for Myntra office uniform”* into structured expense records (with optional receipt upload)
- **AI Invoice Assistant**: Generates complete invoices from free-form text (with PDF download)
- **AI Chatbot**: Interactive financial assistant with quick replies for common queries

### 📊 ERP Modules
- **Expense Management**: Track expenses with AI categorization and optional receipt attachment
- **Invoicing**: Generate, manage, and download invoices as PDFs
- **Customers**: Maintain customer records
- **Products**: Manage product catalog
- **Analytics Dashboard**: Real-time financial insights

### 🔐 Security & Authentication
- Email/password login with secure JWT tokens
- Optional Google OAuth support
- User data isolation (each user sees only their own data)

### 🐳 Deployment
- **Docker Support**: One-click deployment with docker-compose
- Production-ready architecture

---

## 🧠 Tech Stack

### Backend
- Python + Flask
- SQLAlchemy ORM
- PostgreSQL
- Custom NLP pipeline
- Cloudinary (for receipt uploads)
- Google Generative AI (for chatbot)

### Frontend
- React + React Router
- Vite
- Recharts (for analytics)
- jsPDF + html2canvas (for PDF generation)

---

## 🚀 Getting Started

### Option 1: Docker (Recommended)
1. Make sure Docker Desktop is running
2. Clone the repo
3. Run:
   ```bash
   docker-compose up --build
   ```
4. Open http://localhost:3000 in your browser

### Option 2: Manual Setup
#### Backend
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\Activate.ps1` (Windows)
3. Install dependencies: `cd backend && pip install -r requirements.txt`
4. Download spaCy model: `python -m spacy download en_core_web_sm`
5. Create a `.env` file in `backend/` with:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/ledgerlink
   SECRET_KEY=your-secret-key-here
   GEMINI_API_KEY=your-gemini-api-key-here (optional)
   CLOUDINARY_URL=your-cloudinary-url-here (optional)
   ```
6. Run: `python app.py`

#### Frontend
1. Install dependencies: `cd frontend && npm install`
2. Run: `npm run dev`

---

## 🎯 Objective

LedgerLink demonstrates how **AI-driven automation** can improve financial accuracy, reduce operational overhead, and provide structured insights for growing businesses.

---

## 📝 License
MIT License
