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
    """Registration trims spaces but preserves original-case email for display; no sensitive fields in response."""
    base = unique_email_base()
    pretty = f"  {base}User@Example.COM  "
    clean_display = f"{base}User@Example.COM"
    r = register(pretty, 'Passw0rd1')
    assert r.status_code == 201, r.text
    body = r.json()
    # Schema: must include email (string)
    assert isinstance(body.get('email'), str)
    assert body['email'] == clean_display
    assert 'password' not in body and 'passwordHash' not in body


def test_register_duplicate_ignores_case_and_spaces():
    """Duplicate registration is detected ignoring case/whitespace and mentions 'email' in the error."""
    base = unique_email_base()
    e1 = f"{base}@example.com"
    e2 = f"  {base.upper()}@EXAMPLE.com  "
    assert register(e1, 'Passw0rd1').status_code == 201
    r2 = register(e2, 'Passw0rd1')
    assert r2.status_code == 400, r2.text
    assert 'email' in r2.text.lower()


def test_login_ignores_case_and_spaces():
    """Login succeeds ignoring case/whitespace in email; response must not include sensitive fields."""
    base = unique_email_base()
    display = f"{base}User@Example.com"
    raw = f"  {base}user@example.COM  "
    assert register(display, 'Passw0rd1').status_code == 201
    r = login(raw, 'Passw0rd1')
    assert r.status_code == 200, r.text
    body = r.json()
    # Schema: must include accessToken and refreshToken (strings)
    assert isinstance(body.get('accessToken'), str)
    assert isinstance(body.get('refreshToken'), str)
    assert 'password' not in body and 'passwordHash' not in body


def test_me_returns_original_case_email():
    """/api/me returns original-case email from registration; response excludes sensitive fields."""
    base = unique_email_base()
    display = f"{base}User@Example.com"
    assert register(display, 'Passw0rd1').status_code == 201
    r = login(display.lower(), 'Passw0rd1')
    at = r.json()['accessToken']
    m = me(at)
    assert m.status_code == 200
    data = m.json()
    assert data['email'] == display
    assert 'password' not in data and 'passwordHash' not in data


def test_refresh_and_logout_not_affected_by_login_email_case():
    """Refresh and logout continue to work regardless of login email casing; refresh response has no sensitive fields."""
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
    # Schema: refresh must return JSON with accessToken (string)
    rr_body = rr.json()
    assert isinstance(rr_body.get('accessToken'), str)
    # ensure no sensitive fields in refresh response
    assert 'password' not in rr_body and 'passwordHash' not in rr_body
    # logout should work
    lo = requests.post(url('/api/auth/logout'), json={'refreshToken': rt})
    assert lo.status_code in (200, 204)


def test_validation_errors_include_email_word():
    """Validation errors for bad email should return 400 and include the word 'email'."""
    r = register('not-an-email', 'Passw0rd1')
    assert r.status_code == 400
    assert 'email' in r.text.lower()
