import os
import time
import json
import base64
import hmac
import hashlib
import uuid
import requests

BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')
DEFAULT_SECRET = 'dev-secret'  # server default when JWT_SECRET not set


def url(p):
    return f"{BASE_URL}{p}"


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


def b64url_decode(s: str) -> bytes:
    pad = '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def make_jwt(payload: dict, secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h = b64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    p = b64url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
    signing_input = f"{h}.{p}".encode('ascii')
    sig = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
    s = b64url_encode(sig)
    return f"{h}.{p}.{s}"


def unique_email():
    return f"user_{uuid.uuid4().hex[:8]}@example.com"


def register(email, password):
    return requests.post(url('/api/auth/register'), json={'email': email, 'password': password})


def login(email, password):
    return requests.post(url('/api/auth/login'), json={'email': email, 'password': password})


def test_access_token_has_required_claims_and_hs256():
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    r = login(email, 'Passw0rd1')
    assert r.status_code == 200, r.text
    tok = r.json()['accessToken']
    parts = tok.split('.')
    assert len(parts) == 3
    header = json.loads(b64url_decode(parts[0]).decode('utf-8'))
    payload = json.loads(b64url_decode(parts[1]).decode('utf-8'))
    assert header.get('alg') == 'HS256'
    assert 'sub' in payload and 'email' in payload
    assert 'iat' in payload and 'exp' in payload and isinstance(payload['exp'], int)
    assert payload['exp'] > int(time.time())


def test_health_has_app_name_header():
    r = requests.get(url('/api/health'))
    assert r.status_code == 200
    app_name = r.headers.get('X-App-Name')
    assert isinstance(app_name, str) and len(app_name.strip()) > 0


def test_me_rejects_expired_token_with_default_secret():
    # Craft a token with exp in the past using the default secret
    now = int(time.time())
    payload = {"sub": "expired-user", "email": "x@example.com", "iat": now - 120, "exp": now - 60}
    expired = make_jwt(payload, DEFAULT_SECRET)
    r = requests.get(url('/api/me'), headers={'Authorization': f'Bearer {expired}'})
    assert r.status_code == 401, r.text


def test_me_rejects_token_signed_with_wrong_secret():
    # Create a token with a future exp but wrong secret
    now = int(time.time())
    payload = {"sub": "bad-user", "email": "y@example.com", "iat": now, "exp": now + 600}
    wrong = make_jwt(payload, 'totally-wrong-secret')
    r = requests.get(url('/api/me'), headers={'Authorization': f'Bearer {wrong}'})
    assert r.status_code == 401, r.text


def test_me_accepts_valid_server_token_from_login():
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    r = login(email, 'Passw0rd1')
    assert r.status_code == 200
    at = r.json()['accessToken']
    me = requests.get(url('/api/me'), headers={'Authorization': f'Bearer {at}'})
    assert me.status_code == 200
    body = me.json()
    assert body['email'].lower() == email.lower()


def test_tampered_signature_is_rejected():
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    r = login(email, 'Passw0rd1')
    tok = r.json()['accessToken']
    h, p, s = tok.split('.')
    # Tamper signature by flipping last char (safe alnum rotate)
    last = s[-1]
    new_last = 'A' if last != 'A' else 'B'
    bad = f"{h}.{p}.{s[:-1]}{new_last}"
    me = requests.get(url('/api/me'), headers={'Authorization': f'Bearer {bad}'})
    assert me.status_code == 401
