import os
import time
import requests
import jwt
from tenacity import retry, stop_after_delay, wait_fixed

BASE_URL = os.getenv('TARGET_BASE_URL', 'http://localhost:5000')
AUTH_BASE = f"{BASE_URL}/api/v1/auth"

@retry(stop=stop_after_delay(60), wait=wait_fixed(2))
def wait_for_app():
    r = requests.get(BASE_URL, timeout=3)
    assert r.status_code in (200, 404)


def register_user(payload):
    return requests.post(f"{AUTH_BASE}/register", json=payload, timeout=10)


def login_user(email, password):
    return requests.post(f"{AUTH_BASE}/login", json={"email": email, "password": password}, timeout=10)


def get_me(token=None, cookie=None):
    headers = {}
    cookies = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if cookie:
        cookies["token"] = cookie
    return requests.get(f"{AUTH_BASE}/me", headers=headers, cookies=cookies, timeout=10)


def extract_token_cookie(resp):
    # cookie named 'token'
    token_cookie = None
    for c in resp.cookies:
        if c.name == 'token':
            token_cookie = c.value
            break
    return token_cookie


def test_01_app_is_up():
    wait_for_app()


def test_02_register_success_and_cookie_set():
    wait_for_app()
    payload = {
        "name": "Alice", 
        "email": "alice@example.com", 
        "password": "secret123"
    }
    r = register_user(payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data.get('success') is True
    assert 'token' in data
    cookie = extract_token_cookie(r)
    assert cookie is not None

    # Also verify /me works with cookie
    r_me = get_me(cookie=cookie)
    assert r_me.status_code == 200, r_me.text
    me = r_me.json().get('data')
    assert me and me.get('email') == 'alice@example.com'


def test_03_register_duplicate_email_400():
    wait_for_app()
    payload = {
        "name": "Alice2",
        "email": "alice@example.com",
        "password": "secret123"
    }
    r = register_user(payload)
    assert r.status_code == 400, r.text
    data = r.json()
    assert data.get('success') is False
    # error message should mention duplicate
    assert 'duplicate' in data.get('error', '').lower()


def test_04_login_success_and_me_with_bearer():
    wait_for_app()
    r = login_user("alice@example.com", "secret123")
    assert r.status_code == 200, r.text
    token = r.json().get('token')
    assert token
    r_me = get_me(token=token)
    assert r_me.status_code == 200, r_me.text
    me = r_me.json().get('data')
    assert me and me.get('email') == 'alice@example.com'


def test_05_login_wrong_password_401():
    wait_for_app()
    r = login_user("alice@example.com", "wrongpass")
    assert r.status_code == 401, r.text
    data = r.json()
    assert data.get('success') is False


def test_06_me_401_when_user_deleted_but_token_valid():
    wait_for_app()
    # Craft a validly signed token with a non-existent user id
    secret = os.getenv('JWT_SECRET', 'supersecret_for_tests')
    payload = {"id": "507f1f77bcf86cd799439011", "role": "user"}
    token = jwt.encode(payload, secret, algorithm="HS256")
    r_me = get_me(token=token)
    assert r_me.status_code == 401, r_me.text


def test_07_me_401_when_user_deleted_but_cookie_valid():
    wait_for_app()
    # Craft a validly signed token with a non-existent user id and send via cookie
    secret = os.getenv('JWT_SECRET', 'supersecret_for_tests')
    payload = {"id": "507f1f77bcf86cd799439012", "role": "user"}
    token = jwt.encode(payload, secret, algorithm="HS256")
    r_me = get_me(cookie=token)
    assert r_me.status_code == 401, r_me.text


def test_08_me_with_lowercase_bearer_header():
    wait_for_app()
    # Register and login
    email = "dave@example.com"
    r = register_user({"name": "Dave", "email": email, "password": "secret123"})
    assert r.status_code == 201, r.text
    token = r.json().get('token')
    assert token
    # Call /me with lowercase 'bearer' to ensure header parsing is case-insensitive
    headers = {"Authorization": f"bearer {token}"}
    r_me = requests.get(f"{AUTH_BASE}/me", headers=headers, timeout=10)
    assert r_me.status_code == 200, r_me.text
 
