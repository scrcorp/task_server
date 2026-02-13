-- ============================================================
-- Migration 002: Rename user_profiles → users
-- ============================================================

-- 1. Rename table
ALTER TABLE user_profiles RENAME TO users;

-- 2. Rename constraints
ALTER TABLE users RENAME CONSTRAINT uq_user_profiles_email    TO uq_users_email;
ALTER TABLE users RENAME CONSTRAINT uq_user_profiles_login_id TO uq_users_login_id;
ALTER TABLE users RENAME CONSTRAINT chk_user_profiles_role    TO chk_users_role;
ALTER TABLE users RENAME CONSTRAINT chk_user_profiles_status  TO chk_users_status;

-- 3. Rename indexes
ALTER INDEX idx_user_profiles_company_id RENAME TO idx_users_company_id;
ALTER INDEX idx_user_profiles_login_id   RENAME TO idx_users_login_id;
ALTER INDEX idx_user_profiles_role       RENAME TO idx_users_role;
ALTER INDEX idx_user_profiles_status     RENAME TO idx_users_status;

-- 4. Rename trigger
DROP TRIGGER IF EXISTS trg_user_profiles_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
