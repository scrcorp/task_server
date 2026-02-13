import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.core.dependencies import get_auth_service


def _make_mock_service():
    return AsyncMock()


class TestVerifyEmailEndpoint:
    def test_verify_email_200(self):
        mock_service = _make_mock_service()
        mock_service.verify_email.return_value = {
            "message": "Email verified successfully."
        }
        app.dependency_overrides[get_auth_service] = lambda: mock_service
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/auth/verify-email",
                json={"email": "test@example.com", "code": "123456"},
            )
            assert response.status_code == 200
            assert response.json()["message"] == "Email verified successfully."
        finally:
            app.dependency_overrides.clear()

    def test_verify_email_400_invalid_code(self):
        mock_service = _make_mock_service()
        mock_service.verify_email.side_effect = Exception(
            "Invalid or expired verification code."
        )
        app.dependency_overrides[get_auth_service] = lambda: mock_service
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/auth/verify-email",
                json={"email": "test@example.com", "code": "000000"},
            )
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()

    def test_verify_email_429_rate_limited(self):
        mock_service = _make_mock_service()
        mock_service.verify_email.side_effect = Exception(
            "Too many requests. Please try again later."
        )
        app.dependency_overrides[get_auth_service] = lambda: mock_service
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/auth/verify-email",
                json={"email": "test@example.com", "code": "123456"},
            )
            assert response.status_code == 429
        finally:
            app.dependency_overrides.clear()


class TestResendVerificationEndpoint:
    def test_resend_200(self):
        mock_service = _make_mock_service()
        mock_service.resend_verification_email.return_value = {
            "message": "Verification code sent."
        }
        app.dependency_overrides[get_auth_service] = lambda: mock_service
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/auth/resend-verification",
                json={"email": "test@example.com"},
            )
            assert response.status_code == 200
            assert response.json()["message"] == "Verification code sent."
        finally:
            app.dependency_overrides.clear()

    def test_resend_400_already_verified(self):
        mock_service = _make_mock_service()
        mock_service.resend_verification_email.side_effect = Exception(
            "Email is already verified."
        )
        app.dependency_overrides[get_auth_service] = lambda: mock_service
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/auth/resend-verification",
                json={"email": "test@example.com"},
            )
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()

    def test_resend_404_no_account(self):
        mock_service = _make_mock_service()
        mock_service.resend_verification_email.side_effect = Exception(
            "No account found with this email."
        )
        app.dependency_overrides[get_auth_service] = lambda: mock_service
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/auth/resend-verification",
                json={"email": "nobody@example.com"},
            )
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_resend_429_rate_limited(self):
        mock_service = _make_mock_service()
        mock_service.resend_verification_email.side_effect = Exception(
            "Too many requests. Please try again later."
        )
        app.dependency_overrides[get_auth_service] = lambda: mock_service
        try:
            client = TestClient(app)
            response = client.post(
                "/api/v1/auth/resend-verification",
                json={"email": "test@example.com"},
            )
            assert response.status_code == 429
        finally:
            app.dependency_overrides.clear()
