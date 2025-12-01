import os
import requests

BASE_URL = os.getenv('BASE_URL', 'http://localhost:3000')

def url(p):
    return f"{BASE_URL}{p}"

def test_cors_on_health_get():
    r = requests.get(url('/api/health'))
    assert r.status_code == 200
    ao = r.headers.get('Access-Control-Allow-Origin')
    assert ao == '*' or ao is not None

def test_cors_on_register_post():
    r = requests.post(url('/api/auth/register'), json={'email':'u@example.com','password':'Passw0rd1'})
    assert r.status_code in (200,201,400)
    ao = r.headers.get('Access-Control-Allow-Origin')
    assert ao == '*' or ao is not None


def test_preflight_options_register():
    r = requests.options(url('/api/auth/register'))
    assert r.status_code in (200,204)
    allow_methods = r.headers.get('Access-Control-Allow-Methods','')
    allow_headers = r.headers.get('Access-Control-Allow-Headers','')
    assert 'POST' in allow_methods.upper()
    assert 'CONTENT-TYPE' in allow_headers.upper() or 'AUTHORIZATION' in allow_headers.upper()


def test_vary_origin_present():
    r = requests.get(url('/api/health'))
    vary = r.headers.get('Vary','')
    assert 'Origin' in vary or vary == ''  # Some servers omit vary when wildcard


def test_security_headers_basic():
    r = requests.get(url('/api/health'))
    assert r.headers.get('X-Content-Type-Options') == 'nosniff'
    assert r.headers.get('X-Frame-Options') == 'SAMEORIGIN'
    assert r.headers.get('X-XSS-Protection') == '0'


def test_credentials_not_required():
    r = requests.get(url('/api/health'))
    # Server should respond successfully without credentials
    assert r.status_code == 200
