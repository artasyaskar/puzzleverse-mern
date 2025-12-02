import os
import requests
import uuid
from datetime import datetime

BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')

def url(p):
    return f"{BASE_URL}{p}"

def unique_email():
    return f"user_{uuid.uuid4().hex[:8]}@example.com"

def register(email, password):
    return requests.post(url('/api/auth/register'), json={'email': email, 'password': password})

def login(email, password):
    return requests.post(url('/api/auth/login'), json={'email': email, 'password': password})

def me(access_token):
    return requests.get(url('/api/me'), headers={'Authorization': f'Bearer {access_token}'})

def test_me_payload_has_expected_fields_and_types():
    """/api/me returns JSON with id, email, createdAt (ISO string) and excludes sensitive fields."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    r = login(email, 'Passw0rd1')
    at = r.json()['accessToken']
    m = me(at)
    assert m.status_code == 200
    assert m.headers.get('Content-Type', '').lower().startswith('application/json')
    data = m.json()
    assert isinstance(data.get('id'), str) and isinstance(data.get('email'), str)
    assert isinstance(data.get('createdAt'), str)
    # createdAt should be a valid ISO-8601 timestamp
    created_at = data.get('createdAt')
    try:
        # Accept both 'Z' and offset formats
        datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    except Exception:
        assert False, "createdAt is not a valid ISO 8601 datetime"
    assert 'password' not in data and 'passwordHash' not in data

def test_me_headers_no_store_and_json():
    """/api/me sets Cache-Control: no-store and Content-Type: application/json headers."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    at = login(email, 'Passw0rd1').json()['accessToken']
    m = me(at)
    assert 'no-store' in (m.headers.get('Cache-Control','').lower())
    assert m.headers.get('Content-Type','').lower().startswith('application/json')

def test_me_returns_stable_values_across_calls():
    """Multiple calls to /api/me with the same token return identical payloads (stable values)."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    at = login(email, 'Passw0rd1').json()['accessToken']
    m1 = me(at).json()
    m2 = me(at).json()
    assert m1 == m2

def test_me_missing_token_401():
    """Calling /api/me without an Authorization token returns 401 Unauthorized with JSON error."""
    r = requests.get(url('/api/me'))
    assert r.status_code == 401
    assert r.headers.get('Content-Type','').lower().startswith('application/json')
    body = r.json()
    assert 'error' in body and isinstance(body['error'], str)


def test_me_invalid_token_401():
    """Calling /api/me with an invalid token returns 401 Unauthorized with JSON error."""
    r = requests.get(url('/api/me'), headers={'Authorization': 'Bearer not-a-token'})
    assert r.status_code == 401
    assert r.headers.get('Content-Type','').lower().startswith('application/json')
    body = r.json()
    assert 'error' in body and isinstance(body['error'], str)


def test_health_unchanged():
    """/api/health remains unaffected and returns { status: 'ok' } with 200 status."""
    r = requests.get(url('/api/health'))
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'
