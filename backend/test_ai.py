import requests
base='http://localhost:5000/api'

test_cases = [
    'Paid 500 to Amzon',
    'Spent 1200 on FlpKart',
    '300 rs for Uberr',
    'Spent 2000 at Starbuks'
]

print("--- Testing Fuzzy Matching ---")
for text in test_cases:
    try:
        r = requests.post(f"{base}/expense/categorize", json={'text': text})
        data = r.json()
        if data.get('success'):
            v = data['data']['vendor']
            c = data['data']['category']
            print(f"Input: '{text}' -> Vendor: {v}, Category: {c}")
        else:
            print(f"Failed: {text} - {data.get('error')}")
    except Exception as e:
        print(f"Error testing '{text}': {e}")
