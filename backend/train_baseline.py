import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Paths (robust)
HERE = os.path.dirname(__file__)
DATA_CANDIDATES = [
    os.path.join(HERE, "data", "synthetic_expenses.csv"),
    os.path.join(HERE, "data", "synthetic_expenses.csv".replace("data/data","data"))
]
data_path = None
for p in DATA_CANDIDATES:
    if os.path.exists(p):
        data_path = p
        break

if data_path is None:
    raise FileNotFoundError("Cannot find synthetic_expenses.csv. Expected at backend/data/")

print("Loading data from:", data_path)
df = pd.read_csv(data_path)

# Basic cleaning
df = df.dropna(subset=["text", "label"])
df['text'] = df['text'].astype(str)
df['label'] = df['label'].astype(str)

# Train/test split
X = df['text']
y = df['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)

# Pipeline
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1,2), max_features=5000)),
    ("clf", LinearSVC())
])

print("Training model on %d samples..." % len(X_train))
pipeline.fit(X_train, y_train)

print("Evaluating on test set (%d samples)..." % len(X_test))
pred = pipeline.predict(X_test)
print(classification_report(y_test, pred))

# Save model
OUT_DIR = os.path.join(HERE, "models")
os.makedirs(OUT_DIR, exist_ok=True)
MODEL_PATH = os.path.join(OUT_DIR, "expense_baseline.pkl")
joblib.dump(pipeline, MODEL_PATH)
print("Saved model to:", MODEL_PATH)
