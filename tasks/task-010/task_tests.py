import os
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


def test_all_responses_include_request_id_header():
    """Every response includes a non-empty X-Request-Id header value."""
    r = requests.get(url('/api/health'))
    rid = r.headers.get('X-Request-Id')
    assert isinstance(rid, str) and len(rid.strip()) > 0


def test_echoes_incoming_request_id_header():
    """If a client sends X-Request-Id, the same value is echoed in the response header."""
    incoming = 'test-id-1234'
    r = requests.get(url('/api/health'), headers={'X-Request-Id': incoming})
    assert r.headers.get('X-Request-Id') == incoming


def test_404_returns_json_with_request_id_and_header_matches_body():
    """Unknown routes return 404 JSON with {error, requestId} and header matches body.requestId."""
    r = requests.get(url('/no-such-route'))
    assert r.status_code == 404
    assert r.headers.get('Content-Type','').lower().startswith('application/json')
    rid = r.headers.get('X-Request-Id')
    body = r.json()
    assert 'error' in body and isinstance(body['error'], str)
    assert body.get('requestId') == rid and len(body['requestId']) > 0


def test_login_400_json_has_request_id_and_matches_header():
    """Validation errors on /api/auth/login return 400 JSON with requestId matching the header."""
    # Missing password triggers 400
    r = requests.post(url('/api/auth/login'), json={'email': 'user@example.com'})
    assert r.status_code == 400
    assert r.headers.get('Content-Type','').lower().startswith('application/json')
    rid = r.headers.get('X-Request-Id')
    body = r.json()
    assert 'error' in body and isinstance(body['error'], str)
    assert body.get('requestId') == rid


def test_me_401_json_has_request_id_and_matches_header():
    """Unauthorized /api/me returns 401 JSON with requestId matching the header."""
    r = requests.get(url('/api/me'), headers={'Authorization': 'Bearer not-a-token'})
    assert r.status_code == 401
    assert r.headers.get('Content-Type','').lower().startswith('application/json')
    rid = r.headers.get('X-Request-Id')
    body = r.json()
    assert 'error' in body and isinstance(body['error'], str)
    assert body.get('requestId') == rid


def test_generated_request_ids_are_unique_when_not_provided():
    """Two sequential requests without incoming X-Request-Id yield different generated IDs."""
    r1 = requests.get(url('/api/health'))
    r2 = requests.get(url('/api/health'))
    id1 = r1.headers.get('X-Request-Id')
    id2 = r2.headers.get('X-Request-Id')
    assert id1 and id2 and id1 != id2


def test_404_echoes_incoming_request_id_in_body():
    """404 JSON body.requestId must echo the incoming X-Request-Id sent by the client."""
    incoming = 'cid-404-echo'
    r = requests.get(url('/no-such-route'), headers={'X-Request-Id': incoming})
    assert r.status_code == 404
    body = r.json()
    assert body.get('requestId') == incoming


def test_login_400_echoes_incoming_request_id_in_body():
    """Login 400 JSON must echo incoming X-Request-Id in body.requestId and header."""
    incoming = 'cid-400-echo'
    r = requests.post(
        url('/api/auth/login'),
        json={'email': 'user@example.com'},
        headers={'X-Request-Id': incoming},
    )
    assert r.status_code == 400
    assert r.headers.get('X-Request-Id') == incoming
    assert r.json().get('requestId') == incoming


def test_me_401_echoes_incoming_request_id_in_body():
    """/api/me 401 JSON must echo incoming X-Request-Id in body.requestId and header."""
    incoming = 'cid-401-echo'
    r = requests.get(
        url('/api/me'),
        headers={'Authorization': 'Bearer not-a-token', 'X-Request-Id': incoming},
    )
    assert r.status_code == 401
    assert r.headers.get('X-Request-Id') == incoming
    assert r.json().get('requestId') == incoming
