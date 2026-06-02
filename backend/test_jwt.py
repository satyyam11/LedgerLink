from services.auth_utils import create_access_token, decode_access_token

# Test token creation
token = create_access_token(1)
print(f"Generated token: {token}")

# Test token decoding
decoded = decode_access_token(token)
print(f"Decoded user_id: {decoded}")
