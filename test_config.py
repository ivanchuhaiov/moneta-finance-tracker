from app.auth.security import create_access_token, create_refresh_token, decode_token

access = create_access_token(user_id=1)
print("access:", access)

payload = decode_token(access)
print("decoded:", payload)

refresh = create_refresh_token(user_id=1)
print("refresh:", refresh)



