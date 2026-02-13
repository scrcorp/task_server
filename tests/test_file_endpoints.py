import io
import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.dependencies import get_file_service
from app.core.security import get_current_user
from app.services.file_service import FileService
from app.schemas.user import User
from datetime import datetime


def _mock_user():
    return User(
        id="user-1",
        email="test@example.com",
        login_id="testuser",
        full_name="Test User",
        company_id="company-1",
        created_at=datetime(2026, 1, 1),
        updated_at=datetime(2026, 1, 1),
    )


def _mock_file_service():
    service = AsyncMock(spec=FileService)
    service.upload_file = AsyncMock(return_value={
        "file_url": "https://storage.example.com/uploads/abc.png",
        "file_name": "abc.png",
        "file_size": 1024,
        "content_type": "image/png",
    })
    service.get_presigned_url = AsyncMock(return_value="https://storage.example.com/signed/abc.png")
    service.delete_file = AsyncMock(return_value=True)
    return service


client = TestClient(app)


def test_upload_success():
    mock_service = _mock_file_service()
    app.dependency_overrides[get_file_service] = lambda: mock_service
    app.dependency_overrides[get_current_user] = _mock_user
    try:
        response = client.post(
            "/api/v1/files/upload",
            files={"file": ("test.png", b"fake image data", "image/png")},
            params={"folder": "uploads"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "file_url" in data
        assert data["content_type"] == "image/png"
    finally:
        app.dependency_overrides.clear()


def test_upload_too_large():
    mock_service = _mock_file_service()
    mock_service.upload_file = AsyncMock(side_effect=ValueError("File size exceeds 10MB limit."))
    app.dependency_overrides[get_file_service] = lambda: mock_service
    app.dependency_overrides[get_current_user] = _mock_user
    try:
        response = client.post(
            "/api/v1/files/upload",
            files={"file": ("big.png", b"x" * 100, "image/png")},
        )
        assert response.status_code == 413
    finally:
        app.dependency_overrides.clear()


def test_upload_bad_type():
    mock_service = _mock_file_service()
    mock_service.upload_file = AsyncMock(side_effect=ValueError("File type '.exe' is not allowed."))
    app.dependency_overrides[get_file_service] = lambda: mock_service
    app.dependency_overrides[get_current_user] = _mock_user
    try:
        response = client.post(
            "/api/v1/files/upload",
            files={"file": ("malware.exe", b"data", "application/octet-stream")},
        )
        assert response.status_code == 400
    finally:
        app.dependency_overrides.clear()


def test_delete_success():
    mock_service = _mock_file_service()
    app.dependency_overrides[get_file_service] = lambda: mock_service
    app.dependency_overrides[get_current_user] = _mock_user
    try:
        response = client.request(
            "DELETE",
            "/api/v1/files/delete",
            json={"file_path": "uploads/abc.png"},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "File deleted successfully."
    finally:
        app.dependency_overrides.clear()


def test_presigned_url_success():
    mock_service = _mock_file_service()
    app.dependency_overrides[get_file_service] = lambda: mock_service
    app.dependency_overrides[get_current_user] = _mock_user
    try:
        response = client.post(
            "/api/v1/files/presigned-url",
            json={"file_path": "uploads/abc.png"},
        )
        assert response.status_code == 200
        assert "url" in response.json()
    finally:
        app.dependency_overrides.clear()
