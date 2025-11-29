import os
import time
import uuid
import requests

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


def test_register_success_and_case_insensitive_uniqueness():
    email = unique_email()
    r1 = register(email, 'Passw0rd!')
    assert r1.status_code == 201, r1.text
    body = r1.json()
    assert 'id' in body and body['email'].lower() == email.lower()

    # duplicate with different case should fail 400
    r2 = register(email.upper(), 'Passw0rd!')
    assert r2.status_code == 400, r2.text
    assert 'email' in r2.text.lower() or 'duplicate' in r2.text.lower()


def test_register_password_policy():
    email = unique_email()
    r = register(email, 'short')
    assert r.status_code == 400, r.text
    assert 'password' in r.text.lower() and ('8' in r.text or 'length' in r.text.lower())


def test_login_success_and_me_endpoint_with_bearer():
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    r = login(email, 'Passw0rd1')
    assert r.status_code == 200, r.text
    data = r.json()
    assert 'accessToken' in data and 'refreshToken' in data and 'user' in data

    m = me(data['accessToken'])
    assert m.status_code == 200, m.text
    user = m.json()
    assert user['email'].lower() == email.lower()


def test_login_rate_limit_after_five_attempts():
    email = unique_email()
    # create account
    assert register(email, 'Passw0rd1').status_code == 201
    # 5 bad attempts allowed, then 429
    for i in range(5):
        resp = login(email, 'wrongpass')
        # May be 401 for the first 5
        assert resp.status_code in (401, 429)
        if resp.status_code == 429:
            break
    # ensure rate limit trips by the sixth at the latest
    lr = login(email, 'wrongpass')
    assert lr.status_code == 429, lr.text
    assert 'too many' in lr.text.lower() or 'rate' in lr.text.lower()


def test_refresh_rotation_and_old_token_invalid():
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    r = login(email, 'Passw0rd1')
    data = r.json()
    rt1 = data['refreshToken']

    r2 = refresh(rt1)
    assert r2.status_code == 200, r2.text
    d2 = r2.json()
    assert 'accessToken' in d2 and 'refreshToken' in d2
    rt2 = d2['refreshToken']

    # using old refresh token again should fail
    r3 = refresh(rt1)
    assert r3.status_code in (400, 401), r3.text

    # new access token should reach /api/me
    m = me(d2['accessToken'])
    assert m.status_code == 200, m.text


def test_logout_revokes_refresh_token():
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    r = login(email, 'Passw0rd1')
    data = r.json()
    rt = data['refreshToken']

    lo = logout(rt)
    assert lo.status_code in (200, 204), lo.text

    # refresh should now be invalid
    rr = refresh(rt)
    assert rr.status_code in (400, 401), rr.text


def test_me_requires_valid_bearer_token():
    # missing token
    r1 = requests.get(url('/api/me'))
    assert r1.status_code == 401

    # invalid token
    r2 = requests.get(url('/api/me'), headers={'Authorization': 'Bearer not-a-real-token'})
    assert r2.status_code == 401
