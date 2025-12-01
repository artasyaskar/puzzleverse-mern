import os
import uuid
import requests

BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')

MAX_TOKENS = 5  # expected cap per user

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


def test_multiple_logins_create_distinct_refresh_tokens():
    """Each successful login issues a distinct refresh token for the same user."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    tokens = set()
    for _ in range(3):
        r = login(email, 'Passw0rd1')
        assert r.status_code == 200, r.text
        rt = r.json()['refreshToken']
        assert isinstance(rt, str) and len(rt) >= 40
        tokens.add(rt)
    assert len(tokens) == 3


def test_refresh_invalidates_used_token_and_returns_new():
    """/refresh consumes the old token and returns a new token; old token cannot be reused."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    r = login(email, 'Passw0rd1')
    rt1 = r.json()['refreshToken']
    r2 = refresh(rt1)
    assert r2.status_code == 200, r2.text
    rt2 = r2.json()['refreshToken']
    assert rt2 != rt1
    r3 = refresh(rt1)
    assert r3.status_code in (400, 401)


def test_cap_of_max_tokens_per_user_trims_oldest():
    """When more than MAX_TOKENS tokens are issued, the oldest should be trimmed and become invalid."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    issued = []
    for _ in range(MAX_TOKENS + 2):
        r = login(email, 'Passw0rd1')
        assert r.status_code == 200
        issued.append(r.json()['refreshToken'])
    # The earliest two should be trimmed now
    for old in issued[:2]:
        rr = refresh(old)
        assert rr.status_code in (400, 401), f"old token should be trimmed: {old}"
    # Newest should still work
    ok = refresh(issued[-1])
    assert ok.status_code == 200, ok.text


def test_rotation_respects_cap_does_not_grow_beyond_limit():
    """Rotating via /refresh should not increase outstanding tokens beyond the cap."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    # Issue MAX_TOKENS tokens
    rts = [login(email, 'Passw0rd1').json()['refreshToken'] for _ in range(MAX_TOKENS)]
    # Rotate the newest token several times; old rotated tokens must be invalid
    cur = rts[-1]
    for _ in range(3):
        rr = refresh(cur)
        assert rr.status_code == 200
        nxt = rr.json()['refreshToken']
        bad = refresh(cur)
        assert bad.status_code in (400, 401)
        cur = nxt
    # Still should be able to rotate again without exceeding cap
    final = refresh(cur)
    assert final.status_code == 200


def test_no_refresh_token_leakage_in_other_fields():
    """Ensure only the 'refreshToken' field contains the token; no leakage in other response fields."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    r = login(email, 'Passw0rd1')
    body = r.json()
    rt = body['refreshToken']
    s = json_dump(body).lower()
    assert 'password' not in s and 'passwordhash' not in s
    # Only the explicit field should contain token value
    occurrences = s.count(rt.lower())
    assert occurrences == 1


def test_oldest_trimmed_token_fails_even_if_it_was_never_used():
    """A trimmed token (due to cap) should fail even if never used before."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    rts = []
    for _ in range(MAX_TOKENS + 1):
        r = login(email, 'Passw0rd1')
        assert r.status_code == 200
        rts.append(r.json()['refreshToken'])
    oldest = rts[0]
    res = refresh(oldest)
    assert res.status_code in (400, 401)

# helpers
import json as _json

def json_dump(obj):
    return _json.dumps(obj, separators=(',', ':'), sort_keys=True)


def test_exceeding_by_three_trims_three_oldest():
    """Issuing MAX_TOKENS+3 tokens should trim exactly the first three oldest tokens."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    issued = []
    for _ in range(MAX_TOKENS + 3):
        r = login(email, 'Passw0rd1')
        assert r.status_code == 200
        issued.append(r.json()['refreshToken'])
    # First three should be trimmed
    for old in issued[:3]:
        rr = refresh(old)
        assert rr.status_code in (400, 401), f"old token should be trimmed: {old}"
    # A couple of the newest should still work
    for newest in issued[-2:]:
        ok = refresh(newest)
        assert ok.status_code == 200, ok.text


def test_revoke_then_issue_keeps_within_cap_and_preserves_newest():
    """Revoking one token then issuing a new one should not force-trim the newest tokens and stay within cap."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    rts = [login(email, 'Passw0rd1').json()['refreshToken'] for _ in range(MAX_TOKENS)]
    newest = rts[-1]
    # Revoke newest, then issue one more
    lo = requests.post(url('/api/auth/logout'), json={'refreshToken': newest})
    assert lo.status_code in (200, 204)
    r_new = login(email, 'Passw0rd1')
    assert r_new.status_code == 200
    new_rt = r_new.json()['refreshToken']
    # New token should work
    ok1 = refresh(new_rt)
    assert ok1.status_code == 200
    # And an older-but-still-recent token should also work (not trimmed unexpectedly)
    ok2 = refresh(rts[-2])
    assert ok2.status_code == 200


def test_login_sets_refresh_token_count_header_and_never_exceeds_cap():
    """Login responses that issue refresh tokens must include X-Refresh-Token-Count <= MAX_TOKENS."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    counts = []
    for i in range(MAX_TOKENS + 1):
        r = login(email, 'Passw0rd1')
        assert r.status_code == 200
        hdr = r.headers.get('X-Refresh-Token-Count')
        assert hdr is not None and hdr.isdigit(), f"missing/invalid header: {hdr}"
        counts.append(int(hdr))
    # Counts should be non-decreasing and capped at MAX_TOKENS
    assert all(counts[i] <= counts[i+1] for i in range(len(counts)-1))
    assert counts[-1] <= MAX_TOKENS


def test_refresh_sets_refresh_token_count_header_and_never_exceeds_cap():
    """Refresh responses must include X-Refresh-Token-Count and never exceed MAX_TOKENS after rotation."""
    email = unique_email()
    assert register(email, 'Passw0rd1').status_code == 201
    # Fill to cap
    rts = [login(email, 'Passw0rd1').json()['refreshToken'] for _ in range(MAX_TOKENS)]
    # Rotate newest a few times
    cur = rts[-1]
    for _ in range(2):
        rr = refresh(cur)
        assert rr.status_code == 200
        hdr = rr.headers.get('X-Refresh-Token-Count')
        assert hdr is not None and hdr.isdigit()
        assert int(hdr) <= MAX_TOKENS
        cur = rr.json()['refreshToken']
