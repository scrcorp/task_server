import pytest
from pathlib import Path
from app.core.email import _load_template, TEMPLATE_DIR


class TestLoadTemplate:
    def test_template_dir_exists(self):
        assert TEMPLATE_DIR.exists()

    def test_verify_email_template_exists(self):
        assert (TEMPLATE_DIR / "verify_email.html").exists()

    def test_reset_password_template_exists(self):
        assert (TEMPLATE_DIR / "reset_password.html").exists()

    def test_load_template_substitutes_variables(self):
        html = _load_template(
            "verify_email.html",
            code="123456",
            expire_minutes=10,
            app_name="TestApp",
        )
        assert "123456" in html
        assert "10" in html
        assert "TestApp" in html

    def test_load_template_no_raw_placeholders(self):
        html = _load_template(
            "verify_email.html",
            code="654321",
            expire_minutes=5,
            app_name="MyApp",
        )
        assert "{{code}}" not in html
        assert "{{expire_minutes}}" not in html
        assert "{{app_name}}" not in html

    def test_reset_password_template_substitutes(self):
        html = _load_template(
            "reset_password.html",
            code="999888",
            expire_minutes=15,
            app_name="ResetApp",
        )
        assert "999888" in html
        assert "15" in html
        assert "ResetApp" in html
        assert "{{code}}" not in html
