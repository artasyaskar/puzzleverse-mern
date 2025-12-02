import os
import requests

BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')

def url(p):
    return f"{BASE_URL}{p}"

def body_has_no_password_fields(text: str) -> bool:
    t = text.lower()
    return ('password"' not in t) and ("'password'" not in t) and ('passwordhash' not in t)


def test_register_missing_email_400_with_field_name():
    """Register without email returns 400 and mentions 'email'; response must not leak password fields."""
    r = requests.post(url('/api/auth/register'), json={'password': 'Passw0rd1'})
    assert r.status_code == 400, r.text
    assert 'email' in r.text.lower()
    assert body_has_no_password_fields(r.text)


def test_register_missing_password_400_with_field_name():
    """Register without password returns 400 and mentions 'password'; response must not leak password fields."""
    r = requests.post(url('/api/auth/register'), json={'email': 'user@example.com'})
    assert r.status_code == 400, r.text
    assert 'password' in r.text.lower()
    assert body_has_no_password_fields(r.text)


def test_register_invalid_email_format_400():
    """Register with an invalid email format returns 400 and mentions 'email'; no sensitive fields included."""
    r = requests.post(url('/api/auth/register'), json={'email': 'not-an-email', 'password': 'Passw0rd1'})
    assert r.status_code == 400, r.text
    assert 'email' in r.text.lower()
    assert body_has_no_password_fields(r.text)


def test_register_password_policy_violation_400_helpful():
    """Register with a too-short password returns 400 and hints at length (mentions '8' or 'length')."""
    r = requests.post(url('/api/auth/register'), json={'email': 'user@example.com', 'password': 'short'})
    assert r.status_code == 400, r.text
    txt = r.text.lower()
    assert 'password' in txt and ('8' in txt or 'length' in txt)
    assert body_has_no_password_fields(r.text)


def test_login_missing_email_is_400():
    """Login without email returns 400 and mentions 'email'; response must not leak password fields."""
    r = requests.post(url('/api/auth/login'), json={'password': 'Passw0rd1'})
    assert r.status_code == 400, r.text
    assert 'email' in r.text.lower()
    assert body_has_no_password_fields(r.text)


def test_login_missing_password_is_400():
    """Login without password returns 400 and mentions 'password'; response must not leak password fields."""
    r = requests.post(url('/api/auth/login'), json={'email': 'user@example.com'})
    assert r.status_code == 400, r.text
    assert 'password' in r.text.lower()
    assert body_has_no_password_fields(r.text)


def test_register_password_must_include_letters_and_numbers():
    """Register enforces password complexity: must include both letters and numbers (beyond length)."""
    # All letters only
    r_letters = requests.post(url('/api/auth/register'), json={'email': 'user1@example.com', 'password': 'aaaaaaaa'})
    assert r_letters.status_code == 400, r_letters.text
    txt1 = r_letters.text.lower()
    assert 'password' in txt1 and ('letter' in txt1 or 'number' in txt1 or 'alphanumeric' in txt1)
    assert body_has_no_password_fields(r_letters.text)
    # All numbers only
    r_numbers = requests.post(url('/api/auth/register'), json={'email': 'user2@example.com', 'password': '12345678'})
    assert r_numbers.status_code == 400, r_numbers.text
    txt2 = r_numbers.text.lower()
    assert 'password' in txt2 and ('letter' in txt2 or 'number' in txt2 or 'alphanumeric' in txt2)
    assert body_has_no_password_fields(r_numbers.text)

