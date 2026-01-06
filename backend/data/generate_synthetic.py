# backend/generate_synthetic.py
import csv
import random
import os
from datetime import datetime

random.seed(42)  # reproducible

OUT_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUT_DIR, "synthetic_expenses.csv")

templates = [
    # (template, category)
    ("Bought {item} for {amount} rupees from {vendor}", "office supplies"),
    ("Ordered {item} from {vendor} costing {amount}", "office supplies"),
    ("Paid {amount} for {vendor} hosting", "cloud hosting"),
    ("Renewal: domain {vendor} payment {amount}", "cloud hosting"),
    ("Paid {amount} for Facebook ads campaign", "marketing"),
    ("Instagram ads charged {amount} for promotion", "marketing"),
    ("Monthly subscription {vendor} {amount}", "software"),
    ("Subscription renewal {vendor} amount {amount}", "software"),
    ("Uber to client office {amount}", "travel"),
    ("Ola cab fare {amount} for commute", "travel"),
    ("Flight ticket to conference {amount}", "travel"),
    ("Freelancer payment {vendor} {amount}", "contractors"),
    ("Consultant invoice paid {amount}", "contractors"),
    ("Electricity bill payment {amount}", "utilities"),
    ("Internet broadband recharge {vendor} {amount}", "utilities"),
    ("Purchased equipment: {item} {amount}", "equipment"),
    ("Bought laptop for team {amount} from {vendor}", "equipment"),
]

vendors = [
    "Amazon", "Flipkart", "GoDaddy", "Uber", "Ola", "Airtel", "Jio",
    "Adobe", "Zoom", "Google", "Microsoft", "Dell", "HP", "Swiggy", "Zomato"
]

items = [
    "office chair", "printer ink", "A4 paper ream", "notebook", "pens",
    "monitor", "keyboard", "mouse", "desk", "laptop"
]

def gen_amount(cat):
    # sample amounts depending on category
    if cat in ("office supplies", "utilities", "marketing", "software"):
        return str(random.randint(100, 15000))
    if cat in ("travel",):
        return str(random.randint(100, 60000))
    if cat in ("equipment",):
        return str(random.randint(10000, 200000))
    if cat in ("cloud hosting",):
        return str(random.randint(200, 50000))
    if cat in ("contractors",):
        return str(random.randint(1000, 200000))
    return str(random.randint(100, 10000))

def generate_rows(n=2000):
    rows = []
    for i in range(n):
        tpl, cat = random.choice(templates)
        vendor = random.choice(vendors)
        item = random.choice(items)
        amount = gen_amount(cat)
        text = tpl.format(item=item, amount=amount, vendor=vendor)
        # occasionally add currency symbol or Rs
        if random.random() < 0.35:
            text = text.replace(amount, f"₹{amount}")
        elif random.random() < 0.1:
            text = text.replace(amount, f"Rs {amount}")
        # sometimes include date or extra words
        if random.random() < 0.12:
            text = f"{text} on {datetime.now().strftime('%Y-%m-%d')}"
        rows.append((text, cat))
    return rows

def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["text", "label"])
        w.writerows(rows)

if __name__ == "__main__":
    print("Generating synthetic dataset...")
    rows = generate_rows(2000)
    write_csv(rows, OUT_FILE)
    print("Wrote:", OUT_FILE)
    print("Sample rows:")
    for r in rows[:8]:
        print(" -", r)
