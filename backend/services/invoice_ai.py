import spacy
import re
from datetime import datetime, timedelta

class InvoiceAI:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("SpaCy model loaded ✅")
        except:
            print("⚠️ SpaCy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None

    def parse_invoice_request(self, user_input):
        result = {
            'original_text': user_input,
            'client_name': None,
            'service_description': None,
            'amount': None,
            'currency': 'INR',
            'due_days': 30,
            'issue_date': datetime.now().strftime('%Y-%m-%d'),
            'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }

        # Amount
        amount_patterns = [
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'\$\s*(\d+(?:,\d+)*(?:\.\d+)?)'
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                result['amount'] = float(match.group(1).replace(',', ''))
                if '$' in pattern:
                    result['currency'] = 'USD'
                break

        # Client name
        if self.nlp:
            doc = self.nlp(user_input)
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PERSON"]:
                    result['client_name'] = ent.text
                    break

        # Service
        if not result['service_description']:
            match = re.search(r'for\s+([a-z\s]+)', user_input.lower())
            if match:
                result['service_description'] = match.group(1).strip().title()

        return result

    def generate_invoice_number(self):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"INV-{timestamp}"
