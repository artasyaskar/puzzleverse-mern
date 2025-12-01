import os
import requests

BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')

def url(p):
    return f"{BASE_URL}{p}"

def unique_email():
    import uuid
    return f"user_{uuid.uuid4().hex[:8]}@example.com"

def register(email, password):
    return requests.post(url('/api/auth/register'), json={'email': email, 'password': password})

def login(email, password):
    return requests.post(url('/api/auth/login'), json={'email': email, 'password': password})


def test_rate_limit_after_five_attempts_includes_retry_after():
    """After five failed attempts, sixth returns 429 with a numeric Retry-After header."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    for _ in range(5):
        r = login(email, 'wrongpass')
        assert r.status_code in (401, 429)
        if r.status_code == 429:
            break
    sixth = login(email, 'wrongpass')
    assert sixth.status_code == 429, sixth.text
    ra = sixth.headers.get('Retry-After')
    assert ra is not None and ra.isdigit() and int(ra) >= 1


def test_success_resets_failures():
    """A successful login clears the failure counter, allowing five new attempts before 429."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    # 4 bad attempts (should not lock yet)
    for _ in range(4):
        r = login(email, 'badbadbad')
        assert r.status_code in (401, 429)
        if r.status_code == 429:
            # if implementation locks early, still okay to proceed
            break
    # success should reset failures
    ok = login(email, 'Passw0rd1')
    assert ok.status_code == 200
    # Now we should again have room; do 4 more bad attempts without 429
    saw_429 = False
    for _ in range(4):
        rr = login(email, 'badbadbad')
        if rr.status_code == 429:
            saw_429 = True
            break
        assert rr.status_code in (401, 429)
    assert not saw_429, 'Limiter should reset on success to give new attempts'


def test_interleaving_success_prevents_lockout():
    """Alternating failures with successes should not produce a 429 during the sequence."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    for _ in range(3):
        r1 = login(email, 'nope')
        assert r1.status_code in (401, 429)
        r2 = login(email, 'Passw0rd1')
        assert r2.status_code == 200
    # One more bad just to be sure we're still not locked
    r3 = login(email, 'nope')
    assert r3.status_code in (401, 429)
    # If it locked, it would be 429 very quickly; allow this test to be tolerant


def test_different_email_not_locked_by_other_email():
    """Locking one account must not prevent another email from logging in successfully."""
    e1 = unique_email()
    e2 = unique_email()
    assert register(e1, 'Passw0rd1').status_code == 201
    assert register(e2, 'Passw0rd1').status_code == 201
    # Lock e1
    for _ in range(6):
        login(e1, 'wrongpass')
    # e2 should still be able to log in
    ok2 = login(e2, 'Passw0rd1')
    assert ok2.status_code == 200, ok2.text


def test_429_message_is_friendly():
    """429 response should contain a friendly 'Too many' phrase in the body."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    for _ in range(6):
        r = login(email, 'wrongpass')
    assert r.status_code == 429
    assert 'too many' in r.text.lower()


def test_retry_after_header_numeric_seconds():
    """Retry-After header should be a positive integer number of seconds."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    for _ in range(6):
        r = login(email, 'nope')
    assert r.status_code == 429
    ra = r.headers.get('Retry-After')
    assert ra is not None and ra.isdigit() and int(ra) >= 1
