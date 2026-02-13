-- ============================================================
-- Migration 003: Email verification before signup
-- user_id nullable (코드 발송 시 아직 계정 없음)
-- ============================================================

ALTER TABLE email_verification_codes
    ALTER COLUMN user_id DROP NOT NULL;
