import pytest
import requests
import json
import time
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "http://localhost:5000/api"
TEST_USER = {
    "name": "Test User",
    "email": f"test_{int(datetime.now().timestamp())}@example.com",
    "password": "TestPass123!"
}

class TestUserAuthentication:
    def test_register_user(self):
        """Test user registration with valid data"""
        response = requests.post(
            f"{BASE_URL}/users/register",
            json=TEST_USER
        )
        assert response.status_code == 201
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_USER["email"]
        assert "password" not in data["user"]

    def test_register_duplicate_email(self):
        """Test that duplicate email registration fails"""
        response = requests.post(
            f"{BASE_URL}/users/register",
            json={
                "name": "Another User",
                "email": TEST_USER["email"],
                "password": "DifferentPass123!"
            }
        )
        assert response.status_code == 400
        assert "User already exists" in response.text

    def test_login_success(self):
        """Test successful user login"""
        response = requests.post(
            f"{BASE_URL}/users/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_USER["email"]

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/users/login",
            json={
                "email": TEST_USER["email"],
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "Invalid credentials" in response.text

    def test_protected_route_without_token(self):
        """Test accessing protected route without token"""
        response = requests.get(f"{BASE_URL}/users/me")
        assert response.status_code == 401
        assert "No token provided" in response.text

    def test_protected_route_with_valid_token(self):
        """Test accessing protected route with valid token"""
        # First login to get token
        login_response = requests.post(
            f"{BASE_URL}/users/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
        )
        token = login_response.json()["token"]
        
        # Access protected route
        response = requests.get(
            f"{BASE_URL}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_USER["email"]
        assert "password" not in data

    def test_token_expiration(self):
        """Test that token expires after specified time"""
        # This test requires the token to be set to expire quickly for testing
        # In a real scenario, you'd mock the time or use a test configuration
        pass  # Implementation depends on how token expiration is handled

if __name__ == "__main__":
    pytest.main(["-v"])
