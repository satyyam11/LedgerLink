import spacy
import re
from datetime import datetime, timedelta


class InvoiceAI:

    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("SpaCy model loaded")
        except:
            print("SpaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None


    # ---------- MAIN PARSER ----------
    def parse_invoice_request(self, user_input):

        result = {
            "original_text": user_input,
            "client_name": None,
            "service_description": None,
            "amount": None,
            "currency": "INR",
            "issue_date": datetime.utcnow(),
            "due_date": datetime.utcnow() + timedelta(days=30)
        }

        # ---------- AMOUNT ----------
        amount_patterns = [
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'\$\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'(\d+)\s*rupees'
        ]

        for pattern in amount_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)

            if match:
                result["amount"] = float(match.group(1).replace(",", ""))

                if "$" in pattern:
                    result["currency"] = "USD"

                break


        # ---------- CLIENT NAME ----------
        if self.nlp:
            doc = self.nlp(user_input)

            for ent in doc.ents:
                if ent.label_ in ["ORG", "PERSON"]:
                    result["client_name"] = ent.text
                    break


        # ---------- SERVICE DESCRIPTION ----------
        match = re.search(r'for\s+([a-z\s]+)', user_input.lower())

        if match:
            result["service_description"] = match.group(1).strip().title()


        # fallback values (important for demo)
        if not result["client_name"]:
            result["client_name"] = "Client"

        if not result["service_description"]:
            result["service_description"] = "Consulting Services"

        if not result["amount"]:
            result["amount"] = 0


        return result


    # ---------- WRAPPER USED BY API ----------
    def parse_invoice(self, text):
        data = self.parse_invoice_request(text)
        
        return {
        "invoice_number": self.generate_invoice_number(),
        "total": data["amount"],  # must be TOTAL for the DB
        "currency": data["currency"],
        "issue_date": data["issue_date"],
        "due_date": data["due_date"]
    }


    # ---------- INVOICE NUMBER ----------
    def generate_invoice_number(self):

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

        return f"INV-{timestamp}"
