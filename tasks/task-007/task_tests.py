import os
import uuid
import requests

BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')

def url(p):
    return f"{BASE_URL}{p}"

def unique_email_base():
    return f"user_{uuid.uuid4().hex[:6]}"


def register(email, password):
    return requests.post(url('/api/auth/register'), json={'email': email, 'password': password})


def login(email, password):
    return requests.post(url('/api/auth/login'), json={'email': email, 'password': password})


def me(access_token):
    return requests.get(url('/api/me'), headers={'Authorization': f'Bearer {access_token}'})


def test_register_trims_and_preserves_display_case():
    base = unique_email_base()
    pretty = f"  {base}User@Example.COM  "
    clean_display = f"{base}User@Example.COM"
    r = register(pretty, 'Passw0rd1')
    assert r.status_code == 201, r.text
    body = r.json()
    assert body['email'] == clean_display


def test_register_duplicate_ignores_case_and_spaces():
    base = unique_email_base()
    e1 = f"{base}@example.com"
    e2 = f"  {base.upper()}@EXAMPLE.com  "
    assert register(e1, 'Passw0rd1').status_code == 201
    r2 = register(e2, 'Passw0rd1')
    assert r2.status_code == 400, r2.text
    assert 'email' in r2.text.lower()


def test_login_ignores_case_and_spaces():
    base = unique_email_base()
    display = f"{base}User@Example.com"
    raw = f"  {base}user@example.COM  "
    assert register(display, 'Passw0rd1').status_code == 201
    r = login(raw, 'Passw0rd1')
    assert r.status_code == 200, r.text


def test_me_returns_original_case_email():
    base = unique_email_base()
    display = f"{base}User@Example.com"
    assert register(display, 'Passw0rd1').status_code == 201
    r = login(display.lower(), 'Passw0rd1')
    at = r.json()['accessToken']
    m = me(at)
    assert m.status_code == 200
    assert m.json()['email'] == display


def test_refresh_and_logout_not_affected_by_login_email_case():
    base = unique_email_base()
    display = f"{base}User@Example.com"
    assert register(display, 'Passw0rd1').status_code == 201
    r = login(display.lower(), 'Passw0rd1')
    data = r.json()
    at = data['accessToken']
    rt = data['refreshToken']
    # use access token on /me
    assert me(at).status_code == 200
    # refresh should work
    rr = requests.post(url('/api/auth/refresh'), json={'refreshToken': rt})
    assert rr.status_code == 200
    # logout should work
    lo = requests.post(url('/api/auth/logout'), json={'refreshToken': rt})
    assert lo.status_code in (200, 204)


def test_validation_errors_include_email_word():
    r = register('not-an-email', 'Passw0rd1')
    assert r.status_code == 400
    assert 'email' in r.text.lower()
