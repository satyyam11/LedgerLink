import re
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


class ExpenseAI:
    def __init__(self):
        # Training categories
        self.categories = {
            "cloud hosting": ["aws", "azure", "gcp", "hosting", "server", "domain", "cloud"],
            "marketing": ["facebook", "instagram", "google ads", "seo", "promotion", "advertisement"],
            "software": ["license", "subscription", "saas", "tool", "zoom", "office 365"],
            "travel": ["flight", "hotel", "uber", "ola", "train", "bus", "cab", "travel"],
            "office supplies": ["stationery", "printer", "paper", "pen", "chair", "desk", "notebook"],
            "contractors": ["freelancer", "developer", "designer", "writer", "consultant"],
            "utilities": ["electricity", "wifi", "internet", "water bill", "broadband"]
        }

        # Train lightweight model
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

    # -------------------------
    # Main parsing logic
    # -------------------------
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

        # -------------------------
        # 1. Extract Amount
        # -------------------------
        amount_patterns = [
            r"₹\s*(\d+(?:,\d+)*(?:\.\d+)?)",
            r"rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)",
            r"(\d+(?:,\d+)*(?:\.\d+)?)\s*rupees",
            r"(\d+(?:,\d+)*(?:\.\d+)?)"
        ]

        for pattern in amount_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                amt = m.group(1).replace(",", "")
                result["amount"] = float(amt)
                break

        # Detect USD
        if "$" in text.lower():
            result["currency"] = "USD"

        # -------------------------
        # 2. Vendor Detection
        # -------------------------
        vendor_list = [
            "amazon", "flipkart", "ola", "uber", "swiggy", "zomato",
            "airtel", "jio", "vodafone", "bigbasket", "myprotein",
            "nike", "mcdonalds", "dominos", "croma", "reliance",
            "godaddy", "microsoft", "google", "apple"
        ]

        text_lower = text.lower()
        for v in vendor_list:
            if v in text_lower:
                result["vendor"] = v.title()
                break

        # -------------------------
        # 3. Category Prediction
        # -------------------------
        test_vector = self.vectorizer.transform([text])
        predicted = self.model.predict(test_vector)[0]
        confidence = max(self.model.predict_proba(test_vector)[0])

        result["category"] = predicted
        result["confidence"] = round(float(confidence), 2)

        return result

    def get_categories(self):
        return list(self.categories.keys())
