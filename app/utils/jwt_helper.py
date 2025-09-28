# app/utils/jwt_helper.py
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "supersecretkey"  # ممكن تخليه في .env

def generate_token(user_id, role, expires_in=7):
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=expires_in)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
