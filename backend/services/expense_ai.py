import re
import spacy
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

try:
    from rapidfuzz import process, fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False
    print("Warning: 'rapidfuzz' module not found. Fuzzy matching will be disabled.")


class ExpenseAI:
    def __init__(self):
        # Load spaCy
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("SpaCy model loaded")
        except:
            self.nlp = None
            print("Warning: spaCy model 'en_core_web_sm' not found.")

        self.categories = {
            "cloud hosting": ["aws", "azure", "gcp", "hosting", "server", "domain", "cloud", "digitalocean", "heroku"],
            "marketing": ["facebook ads", "instagram ads", "google ads", "seo", "promotion", "advertisement", "billboard", "campaign"],
            "software": ["license", "subscription", "saas", "tool", "zoom", "office 365", "slack", "github", "adobe"],
            "travel": ["flight", "hotel", "uber", "ola", "train", "bus", "cab", "travel", "airbnb", "indigo", "expedia"],
            "office supplies": ["stationery", "printer", "paper", "pen", "chair", "desk", "notebook", "stapler", "furniture"],
            "contractors": ["freelancer", "developer", "designer", "writer", "consultant", "upwork", "fiverr"],
            "utilities": ["electricity", "wifi", "internet", "water bill", "broadband", "phone bill", "gas bill"],
            "shopping": ["amazon", "flipkart", "myntra", "ajio", "mall", "shopping", "clothes", "shoes"],
            "food": ["zomato", "swiggy", "restaurant", "lunch", "dinner", "breakfast", "starbucks", "kfc", "mcdonalds", "pizza"]
        }

        self.vendor_list = [
            "Amazon", "Flipkart", "Ola", "Uber", "Swiggy", "Zomato",
            "Airtel", "Jio", "Vodafone", "Bigbasket", "Nike",
            "McDonalds", "Dominos", "Croma", "Reliance",
            "GoDaddy", "Microsoft", "Google", "Apple", "Netflix", "Spotify",
            "Starbucks", "Burger King", "KFC", "Myntra", "Ajio",
            "Facebook", "Instagram", "AWS", "Azure", "DigitalOcean", "Slack",
            "GitHub", "Adobe", "Zoom", "Air India", "IndiGo", "MakeMyTrip"
        ]

        train_texts = []
        labels = []

        for cat, words in self.categories.items():
            for w in words:
                train_texts.append(f"paid for {w}")
                labels.append(cat)

        self.vectorizer = TfidfVectorizer()
        X = self.vectorizer.fit_transform(train_texts)

        self.model = MultinomialNB()
        self.model.fit(X, labels)

        print("Expense AI initialized with fuzzy matching and categories.")

    def parse_expense(self, text):
        result = {
            "original_text": text,
            "amount": None,
            "currency": "INR",
            "vendor": "Unknown Vendor",
            "category": None,
            "confidence": 0.0,
            "date": datetime.now().strftime("%Y-%m-%d")
        }

        # 1. Extraction with spaCy (if available)
        if self.nlp:
            doc = self.nlp(text)
            # Try to find organizations or people as vendors
            ents = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PERSON"]]
            if ents:
                # Use the first entity found as a candidate
                candidate = ents[0]
                # Fuzzy match against our known vendor list
                if HAS_RAPIDFUZZ:
                    match = process.extractOne(candidate, self.vendor_list, scorer=fuzz.WRatio)
                    if match and match[1] > 70: # 70% confidence threshold
                        result["vendor"] = match[0]
                    else:
                        result["vendor"] = candidate.title()
                else:
                    result["vendor"] = candidate.title()

        # 2. Fallback fuzzy match on the whole text if vendor still unknown
        if result["vendor"] == "Unknown Vendor" and HAS_RAPIDFUZZ:
            # Split text into words and try to match each against vendor list
            words = text.split()
            best_match = None
            highest_score = 0
            
            for word in words:
                if len(word) < 3: continue
                m = process.extractOne(word, self.vendor_list, scorer=fuzz.WRatio)
                if m and m[1] > highest_score:
                    highest_score = m[1]
                    best_match = m[0]
            
            if highest_score > 70: # Lower threshold for better catch-all
                result["vendor"] = best_match

        # 3. Amount Extraction (Regex remains strong for this)
        amount_patterns = [
            r"(?:₹|rs\.?|inr)\s*(\d+(?:,\d+)*(?:\.\d+)?)", # Grouped prefix
            r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:rupees|rs|inr)", # Grouped suffix
            r"(?:spent|paid|total|amount)\s*(?:of\s*)?(\d+(?:,\d+)*(?:\.\d+)?)",
            r"(\d+(?:,\d+)*(?:\.\d+)?)"
        ]

        for pattern in amount_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                try:
                    amt = m.group(1).replace(",", "")
                    result["amount"] = float(amt)
                    break
                except: continue

        if "$" in text.lower():
            result["currency"] = "USD"

        # 4. Category Prediction (Naive Bayes)
        test_vector = self.vectorizer.transform([text])
        predicted = self.model.predict(test_vector)[0]
        confidence = max(self.model.predict_proba(test_vector)[0])

        result["category"] = predicted
        result["confidence"] = round(float(confidence), 2)

        return result
