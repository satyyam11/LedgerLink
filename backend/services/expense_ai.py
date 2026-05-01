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

        print(f"Parsing expense: {text}")
        
        # 0. EXTRA: Direct typo check for common misspellings!
        text_lower = text.lower()
        typo_map = {
            "amezon": "Amazon",
            "flipcrt": "Flipkart",
            "myntaa": "Myntra",
            "zomat": "Zomato",
            "swiggyy": "Swiggy",
        }
        for typo, correct in typo_map.items():
            if typo in text_lower:
                result["vendor"] = correct
                print(f"Direct typo match: {typo} → {correct}")
                break
        
        # 1. Try ALL fuzzy scorers!
        if result["vendor"] == "Unknown Vendor" and HAS_RAPIDFUZZ:
            words = text.split()
            best_match = None
            highest_score = 0
            
            for word in words:
                if len(word) < 3:
                    continue
                # Try every scorer!
                for scorer_name, scorer in [
                    ("ratio", fuzz.ratio),
                    ("partial_ratio", fuzz.partial_ratio),
                    ("token_set_ratio", fuzz.token_set_ratio),
                    ("token_sort_ratio", fuzz.token_sort_ratio),
                    ("WRatio", fuzz.WRatio),
                    ("QRatio", fuzz.QRatio),
                ]:
                    m = process.extractOne(word, self.vendor_list, scorer=scorer)
                    if m:
                        print(f"  Word '{word}' with {scorer_name}: {m[0]} (score: {m[1]})")
                        if m[1] > highest_score:
                            highest_score = m[1]
                            best_match = m[0]
            
            print(f"Best fuzzy match: {best_match} (score: {highest_score})")
            
            if highest_score > 35:  # Very low threshold for demo!
                result["vendor"] = best_match
                print(f"Setting vendor to: {result['vendor']}")
        
        # 2. Then direct keyword check as backup
        if result["vendor"] == "Unknown Vendor":
            text_lower = text.lower()
            for vendor in self.vendor_list:
                vendor_lower = vendor.lower()
                if vendor_lower in text_lower:
                    result["vendor"] = vendor
                    break

        # 3. Then try spaCy NER as last resort
        if result["vendor"] == "Unknown Vendor" and self.nlp:
            doc = self.nlp(text)
            ents = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PERSON"]]
            if ents:
                result["vendor"] = ents[0].title()
        
        print(f"Final vendor: {result['vendor']}")

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
