import os
import requests
import uuid

BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')

def url(p):
    return f"{BASE_URL}{p}"

def unique_email():
    return f"user_{uuid.uuid4().hex[:8]}@example.com"

def register(email, password):
    return requests.post(url('/api/auth/register'), json={'email': email, 'password': password})

def login(email, password):
    return requests.post(url('/api/auth/login'), json={'email': email, 'password': password})

def refresh(refresh_token):
    return requests.post(url('/api/auth/refresh'), json={'refreshToken': refresh_token})

def logout(refresh_token):
    return requests.post(url('/api/auth/logout'), json={'refreshToken': refresh_token})

def me(access_token):
    return requests.get(url('/api/me'), headers={'Authorization': f'Bearer {access_token}'})


def test_logout_returns_204_no_content():
    """Valid logout returns 204 and an empty body."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    r = login(email, 'Passw0rd1')
    rt = r.json()['refreshToken']
    lo = logout(rt)
    assert lo.status_code == 204
    # Some servers send no body; requests maps that to empty string
    assert not lo.text.strip()


def test_logout_idempotent_second_call_204():
    """Calling logout twice with same token returns 204 both times."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    r = login(email, 'Passw0rd1')
    rt = r.json()['refreshToken']
    lo1 = logout(rt)
    lo2 = logout(rt)
    assert lo1.status_code == 204
    assert lo2.status_code == 204


def test_refresh_after_logout_fails():
    """After logout, refresh using that token must fail (400/401)."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    r = login(email, 'Passw0rd1')
    rt = r.json()['refreshToken']
    assert logout(rt).status_code == 204
    rr = refresh(rt)
    assert rr.status_code in (400, 401)


def test_other_refresh_tokens_remain_valid():
    """Revoking one refresh token should not affect others issued to same user."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    r1 = login(email, 'Passw0rd1')
    r2 = login(email, 'Passw0rd1')
    rt1 = r1.json()['refreshToken']
    rt2 = r2.json()['refreshToken']
    assert logout(rt1).status_code == 204
    ok = refresh(rt2)
    assert ok.status_code == 200, ok.text


def test_access_token_still_valid_after_refresh_logout():
    """Existing access token remains valid for /api/me even after logout of the refresh token."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    r = login(email, 'Passw0rd1')
    at = r.json()['accessToken']
    rt = r.json()['refreshToken']
    assert me(at).status_code == 200
    assert logout(rt).status_code == 204
    # Access token should still work until it expires
    mm = me(at)
    assert mm.status_code == 200, mm.text


def test_invalid_or_malformed_token_logout_is_noop_204():
    """Invalid or malformed token in logout should return 204 (idempotent no-op)."""
    lo = logout('this-is-not-a-real-token')
    assert lo.status_code == 204
    assert not lo.text.strip()
