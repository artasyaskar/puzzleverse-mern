import os
import requests

BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')

def url(p):
    return f"{BASE_URL}{p}"

def test_cors_on_health_get():
    """GET /api/health responds 200 and includes an Access-Control-Allow-Origin header (wildcard or specific)."""
    r = requests.get(url('/api/health'))
    assert r.status_code == 200
    ao = r.headers.get('Access-Control-Allow-Origin')
    assert ao == '*' or ao is not None

def test_cors_on_register_post():
    """POST /api/auth/register returns success/created/validation and includes Access-Control-Allow-Origin header."""
    r = requests.post(url('/api/auth/register'), json={'email':'u@example.com','password':'Passw0rd1'})
    assert r.status_code in (200,201,400)
    ao = r.headers.get('Access-Control-Allow-Origin')
    assert ao == '*' or ao is not None


def test_preflight_options_register():
    """OPTIONS preflight on /api/auth/register returns 200/204 and exposes POST in methods and common headers."""
    r = requests.options(url('/api/auth/register'))
    assert r.status_code in (200,204)
    allow_methods = r.headers.get('Access-Control-Allow-Methods','')
    allow_headers = r.headers.get('Access-Control-Allow-Headers','')
    assert 'POST' in allow_methods.upper()
    assert 'CONTENT-TYPE' in allow_headers.upper() or 'AUTHORIZATION' in allow_headers.upper()


def test_vary_origin_present():
    """/api/health response includes Vary: Origin when not using wildcard, or empty when wildcard is used."""
    r = requests.get(url('/api/health'))
    vary = r.headers.get('Vary','')
    assert 'Origin' in vary or vary == ''  # Some servers omit vary when wildcard


def test_security_headers_basic():
    """/api/health includes basic security headers: nosniff, SAMEORIGIN, and disables XSS protection."""
    r = requests.get(url('/api/health'))
    assert r.headers.get('X-Content-Type-Options') == 'nosniff'
    assert r.headers.get('X-Frame-Options') == 'SAMEORIGIN'
    assert r.headers.get('X-XSS-Protection') == '0'


def test_credentials_not_required():
    """/api/health succeeds without credentials; CORS/security checks should not require auth."""
    r = requests.get(url('/api/health'))
    # Server should respond successfully without credentials
    assert r.status_code == 200
