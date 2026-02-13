import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock

from app.services.auth_service import AuthService, _generate_otp
from app.schemas.user import UserCreate


class TestGenerateOTP:
    def test_otp_is_6_digits(self):
        code = _generate_otp()
        assert len(code) == 6
        assert code.isdigit()

    def test_otp_generates_different_codes(self):
        codes = {_generate_otp() for _ in range(100)}
        assert len(codes) > 1  # at least 2 different codes in 100 tries

    def test_otp_pads_with_zeros(self):
        """Ensure codes like 000042 are properly zero-padded."""
        with patch("secrets.randbelow", return_value=42):
            code = _generate_otp()
            assert code == "000042"
            assert len(code) == 6


class TestVerifyEmail:
    @pytest.mark.asyncio
    async def test_verify_email_success(self, auth_service, fake_auth_repo):
        # Setup: create a user and a valid code
        user_id = "user-1"
        email = "test@example.com"
        fake_auth_repo.users[user_id] = {
            "id": user_id,
            "email": email,
            "email_verified": False,
        }
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        await fake_auth_repo.save_verification_code(user_id, email, "123456", expires_at)

        result = await auth_service.verify_email(email, "123456")

        assert result["message"] == "Email verified successfully."
        assert fake_auth_repo.users[user_id]["email_verified"] is True

    @pytest.mark.asyncio
    async def test_verify_email_invalid_code(self, auth_service, fake_auth_repo):
        user_id = "user-1"
        email = "test@example.com"
        fake_auth_repo.users[user_id] = {
            "id": user_id,
            "email": email,
            "email_verified": False,
        }
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        await fake_auth_repo.save_verification_code(user_id, email, "123456", expires_at)

        with pytest.raises(Exception, match="Invalid or expired"):
            await auth_service.verify_email(email, "999999")

    @pytest.mark.asyncio
    async def test_verify_email_expired_code(self, auth_service, fake_auth_repo):
        user_id = "user-1"
        email = "test@example.com"
        fake_auth_repo.users[user_id] = {
            "id": user_id,
            "email": email,
            "email_verified": False,
        }
        # Expired 1 minute ago
        expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        await fake_auth_repo.save_verification_code(user_id, email, "123456", expires_at)

        with pytest.raises(Exception, match="Invalid or expired"):
            await auth_service.verify_email(email, "123456")

    @pytest.mark.asyncio
    async def test_verify_email_code_single_use(self, auth_service, fake_auth_repo):
        user_id = "user-1"
        email = "test@example.com"
        fake_auth_repo.users[user_id] = {
            "id": user_id,
            "email": email,
            "email_verified": False,
        }
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        await fake_auth_repo.save_verification_code(user_id, email, "123456", expires_at)

        # First use succeeds
        await auth_service.verify_email(email, "123456")

        # Second use fails (code already used)
        with pytest.raises(Exception, match="Invalid or expired"):
            await auth_service.verify_email(email, "123456")


class TestResendVerification:
    @pytest.mark.asyncio
    @patch("app.services.auth_service.send_verification_code", new_callable=AsyncMock)
    async def test_resend_success(self, mock_send, auth_service, fake_auth_repo):
        user_id = "user-1"
        email = "test@example.com"
        fake_auth_repo.users[user_id] = {
            "id": user_id,
            "email": email,
            "email_verified": False,
        }

        result = await auth_service.resend_verification_email(email)

        assert result["message"] == "Verification code sent."
        mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_resend_already_verified(self, auth_service, fake_auth_repo):
        user_id = "user-1"
        email = "test@example.com"
        fake_auth_repo.users[user_id] = {
            "id": user_id,
            "email": email,
            "email_verified": True,
        }

        with pytest.raises(Exception, match="already verified"):
            await auth_service.resend_verification_email(email)

    @pytest.mark.asyncio
    async def test_resend_no_account(self, auth_service):
        with pytest.raises(Exception, match="No account found"):
            await auth_service.resend_verification_email("nobody@example.com")

    @pytest.mark.asyncio
    @patch("app.services.auth_service.send_verification_code", new_callable=AsyncMock)
    async def test_resend_rate_limit(self, mock_send, auth_service, fake_auth_repo):
        user_id = "user-1"
        email = "test@example.com"
        fake_auth_repo.users[user_id] = {
            "id": user_id,
            "email": email,
            "email_verified": False,
        }

        # Send 5 codes (reach rate limit)
        for _ in range(5):
            await auth_service.resend_verification_email(email)

        # 6th should fail
        with pytest.raises(Exception, match="Too many requests"):
            await auth_service.resend_verification_email(email)


class TestSignup:
    @pytest.mark.asyncio
    @patch("app.services.auth_service.send_verification_code", new_callable=AsyncMock)
    async def test_signup_sends_verification_code(
        self, mock_send, auth_service
    ):
        user_data = UserCreate(
            email="new@example.com",
            login_id="newuser",
            password="password123",
            full_name="New User",
            company_id="temp",
        )

        result = await auth_service.signup(user_data, company_code="VALID")

        assert "verification code" in result["message"].lower()
        mock_send.assert_called_once()
        # Verify code is 6 digits
        sent_code = mock_send.call_args[0][1]
        assert len(sent_code) == 6
        assert sent_code.isdigit()
