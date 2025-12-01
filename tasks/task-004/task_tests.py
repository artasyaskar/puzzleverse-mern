import os
import requests

BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')

def url(p):
    return f"{BASE_URL}{p}"

def body_has_no_password_fields(text: str) -> bool:
    t = text.lower()
    return ('password"' not in t) and ("'password'" not in t) and ('passwordhash' not in t)


def test_register_missing_email_400_with_field_name():
    r = requests.post(url('/api/auth/register'), json={'password': 'Passw0rd1'})
    assert r.status_code == 400, r.text
    assert 'email' in r.text.lower()
    assert body_has_no_password_fields(r.text)


def test_register_missing_password_400_with_field_name():
    r = requests.post(url('/api/auth/register'), json={'email': 'user@example.com'})
    assert r.status_code == 400, r.text
    assert 'password' in r.text.lower()
    assert body_has_no_password_fields(r.text)


def test_register_invalid_email_format_400():
    r = requests.post(url('/api/auth/register'), json={'email': 'not-an-email', 'password': 'Passw0rd1'})
    assert r.status_code == 400, r.text
    assert 'email' in r.text.lower()
    assert body_has_no_password_fields(r.text)


def test_register_password_policy_violation_400_helpful():
    r = requests.post(url('/api/auth/register'), json={'email': 'user@example.com', 'password': 'short'})
    assert r.status_code == 400, r.text
    txt = r.text.lower()
    assert 'password' in txt and ('8' in txt or 'length' in txt)
    assert body_has_no_password_fields(r.text)


def test_login_missing_email_is_400():
    r = requests.post(url('/api/auth/login'), json={'password': 'Passw0rd1'})
    assert r.status_code == 400, r.text
    assert 'email' in r.text.lower()
    assert body_has_no_password_fields(r.text)


def test_login_missing_password_is_400():
    r = requests.post(url('/api/auth/login'), json={'email': 'user@example.com'})
    assert r.status_code == 400, r.text
    assert 'password' in r.text.lower()
    assert body_has_no_password_fields(r.text)
