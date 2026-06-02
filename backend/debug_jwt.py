from services.auth_utils import create_access_token, decode_access_token
import jwt

# Test token creation
token = create_access_token(1)
print(f"Generated token: {token}")

try:
    JWT_SECRET = "change-me"
    payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    print(f"Payload: {payload}")
    print(f"Decoded user_id: {int(payload['sub'])}")
except Exception as e:
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
    import traceback
    traceback.print_exc()
