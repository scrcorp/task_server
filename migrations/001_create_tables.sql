-- ============================================================
-- Task Server DB Migration v2
-- Supabase (PostgreSQL) - Complete Table Creation
--
-- Total: 20 tables (18 domain + email_verification_codes + notice_confirmations)
-- Execution: Supabase Dashboard > SQL Editor > Paste & Run
-- ============================================================

-- Enable UUID extension (Supabase has this by default, but just in case)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- 1. companies - 회사 (최상위 조직)
-- ============================================================
CREATE TABLE companies (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    code        varchar(20) NOT NULL,
    name        varchar     NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_companies_code UNIQUE (code)
);

-- ============================================================
-- 2. brands - 브랜드 (→ companies)
-- ============================================================
CREATE TABLE brands (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id  uuid        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name        varchar     NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_brands_company_name UNIQUE (company_id, name)
);

CREATE INDEX idx_brands_company_id ON brands(company_id);

-- ============================================================
-- 3. branches - 지점 (→ brands)
-- ============================================================
CREATE TABLE branches (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id    uuid        NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    name        varchar     NOT NULL,
    address     varchar,
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_branches_brand_id ON branches(brand_id);

-- ============================================================
-- 4. group_types - 그룹 유형 (→ branches)
-- ============================================================
CREATE TABLE group_types (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    branch_id   uuid        NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    priority    integer     NOT NULL,
    label       varchar(50) NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_group_types_branch_priority UNIQUE (branch_id, priority),
    CONSTRAINT chk_group_types_priority CHECK (priority BETWEEN 1 AND 3)
);

CREATE INDEX idx_group_types_branch_id ON group_types(branch_id);

-- ============================================================
-- 5. groups - 그룹 (→ group_types)
-- ============================================================
CREATE TABLE groups (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    group_type_id   uuid        NOT NULL REFERENCES group_types(id) ON DELETE CASCADE,
    name            varchar     NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_groups_type_name UNIQUE (group_type_id, name)
);

CREATE INDEX idx_groups_group_type_id ON groups(group_type_id);

-- ============================================================
-- 6. user_profiles - 사용자 프로필 (→ companies)
-- ============================================================
CREATE TABLE user_profiles (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      uuid        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    email           varchar     NOT NULL,
    login_id        varchar     NOT NULL,
    password_hash   text        NOT NULL,
    full_name       varchar     NOT NULL,
    role            varchar     NOT NULL DEFAULT 'staff',
    status          varchar     NOT NULL DEFAULT 'pending',
    language        varchar     NOT NULL DEFAULT 'en',
    email_verified  boolean     NOT NULL DEFAULT false,
    profile_image   varchar,
    join_date       timestamptz,
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_user_profiles_email    UNIQUE (email),
    CONSTRAINT uq_user_profiles_login_id UNIQUE (login_id),
    CONSTRAINT chk_user_profiles_role    CHECK (role IN ('staff', 'manager', 'admin')),
    CONSTRAINT chk_user_profiles_status  CHECK (status IN ('pending', 'active', 'inactive'))
);

CREATE INDEX idx_user_profiles_company_id ON user_profiles(company_id);
CREATE INDEX idx_user_profiles_login_id   ON user_profiles(login_id);
CREATE INDEX idx_user_profiles_role       ON user_profiles(role);
CREATE INDEX idx_user_profiles_status     ON user_profiles(status);

-- ============================================================
-- 7. email_verification_codes - 이메일 인증 코드 (→ user_profiles)
-- ============================================================
CREATE TABLE email_verification_codes (
    id          uuid            PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     uuid            NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    email       varchar(255)    NOT NULL,
    code        varchar(6)      NOT NULL,
    expires_at  timestamptz     NOT NULL,
    used        boolean         NOT NULL DEFAULT false,
    created_at  timestamptz     NOT NULL DEFAULT now()
);

CREATE INDEX idx_verification_codes_email_active ON email_verification_codes(email, used, expires_at DESC);

-- ============================================================
-- 8. checklist_templates - 체크리스트 템플릿 (→ companies, brands, branches)
-- ============================================================
CREATE TABLE checklist_templates (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id  uuid        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    brand_id    uuid        REFERENCES brands(id) ON DELETE SET NULL,
    branch_id   uuid        REFERENCES branches(id) ON DELETE SET NULL,
    name        varchar     NOT NULL,
    recurrence  jsonb       NOT NULL DEFAULT '{"type":"daily"}',
    is_active   boolean     NOT NULL DEFAULT true,
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_templates_company_id ON checklist_templates(company_id);
CREATE INDEX idx_templates_branch_id  ON checklist_templates(branch_id);
CREATE INDEX idx_templates_is_active  ON checklist_templates(is_active);

-- ============================================================
-- 9. template_items - 템플릿 항목 (→ checklist_templates)
-- ============================================================
CREATE TABLE template_items (
    id                  uuid    PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id         uuid    NOT NULL REFERENCES checklist_templates(id) ON DELETE CASCADE,
    content             varchar NOT NULL,
    verification_type   varchar NOT NULL DEFAULT 'none',
    sort_order          integer NOT NULL DEFAULT 0,

    CONSTRAINT chk_template_items_verification_type CHECK (verification_type IN ('none', 'photo', 'signature'))
);

CREATE INDEX idx_template_items_template_id ON template_items(template_id);

-- ============================================================
-- 10. template_groups - 템플릿-그룹 매핑 (→ checklist_templates, groups)
-- ============================================================
CREATE TABLE template_groups (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id uuid NOT NULL REFERENCES checklist_templates(id) ON DELETE CASCADE,
    group_id    uuid NOT NULL REFERENCES groups(id) ON DELETE CASCADE,

    CONSTRAINT uq_template_groups_template_group UNIQUE (template_id, group_id)
);

CREATE INDEX idx_template_groups_template_id ON template_groups(template_id);
CREATE INDEX idx_template_groups_group_id    ON template_groups(group_id);

-- ============================================================
-- 11. daily_checklists - 일일 체크리스트 (→ checklist_templates, branches)
-- ============================================================
CREATE TABLE daily_checklists (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id     uuid        NOT NULL REFERENCES checklist_templates(id) ON DELETE RESTRICT,
    branch_id       uuid        NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    date            date        NOT NULL,
    checklist_data  jsonb       NOT NULL,
    group_ids       uuid[],
    created_at      timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_daily_checklists_template_branch_date UNIQUE (template_id, branch_id, date)
);

CREATE INDEX idx_daily_checklists_branch_date  ON daily_checklists(branch_id, date);
CREATE INDEX idx_daily_checklists_template_id  ON daily_checklists(template_id);
CREATE INDEX idx_daily_checklists_date         ON daily_checklists(date);

-- ============================================================
-- 12. assignments - 할당 업무 (→ companies, branches, user_profiles)
-- ============================================================
CREATE TABLE assignments (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id  uuid        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    branch_id   uuid        REFERENCES branches(id) ON DELETE SET NULL,
    title       varchar     NOT NULL,
    description text,
    priority    varchar     NOT NULL DEFAULT 'normal',
    status      varchar     NOT NULL DEFAULT 'todo',
    due_date    timestamptz,
    recurrence  jsonb,
    created_by  uuid        REFERENCES user_profiles(id) ON DELETE SET NULL,
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT chk_assignments_priority CHECK (priority IN ('urgent', 'normal', 'low')),
    CONSTRAINT chk_assignments_status   CHECK (status IN ('todo', 'in_progress', 'done'))
);

CREATE INDEX idx_assignments_company_id ON assignments(company_id);
CREATE INDEX idx_assignments_branch_id  ON assignments(branch_id);
CREATE INDEX idx_assignments_status     ON assignments(status);
CREATE INDEX idx_assignments_due_date   ON assignments(due_date);
CREATE INDEX idx_assignments_created_by ON assignments(created_by);

-- ============================================================
-- 13. assignment_assignees - 할당 담당자 (→ assignments, user_profiles)
-- ============================================================
CREATE TABLE assignment_assignees (
    assignment_id   uuid        NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    user_id         uuid        NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    assigned_at     timestamptz NOT NULL DEFAULT now(),

    PRIMARY KEY (assignment_id, user_id)
);

CREATE INDEX idx_assignees_user_id ON assignment_assignees(user_id);

-- ============================================================
-- 14. comments - 댓글 (→ assignments, user_profiles)
-- ============================================================
CREATE TABLE comments (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id   uuid        NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    user_id         uuid        NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    content         text,
    content_type    varchar     NOT NULL DEFAULT 'text',
    attachments     jsonb,
    user_name       varchar,
    is_manager      boolean     NOT NULL DEFAULT false,
    created_at      timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT chk_comments_content_type CHECK (content_type IN ('text', 'image', 'video', 'file'))
);

CREATE INDEX idx_comments_assignment_id ON comments(assignment_id);
CREATE INDEX idx_comments_created_at    ON comments(created_at);

-- ============================================================
-- 15. attendance - 출퇴근 기록 (→ companies, user_profiles, branches)
-- ============================================================
CREATE TABLE attendance (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id  uuid        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id     uuid        NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    branch_id   uuid        REFERENCES branches(id) ON DELETE SET NULL,
    clock_in    timestamptz,
    clock_out   timestamptz,
    location    varchar,
    status      varchar     NOT NULL DEFAULT 'not_started',
    work_hours  float,

    CONSTRAINT chk_attendance_status CHECK (status IN ('not_started', 'on_duty', 'off_duty', 'completed'))
);

CREATE INDEX idx_attendance_company_user ON attendance(company_id, user_id);
CREATE INDEX idx_attendance_clock_in     ON attendance(clock_in);
CREATE INDEX idx_attendance_branch_id    ON attendance(branch_id);

-- ============================================================
-- 16. opinions - 건의사항 (→ companies, user_profiles)
-- ============================================================
CREATE TABLE opinions (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id  uuid        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id     uuid        NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    content     text        NOT NULL,
    status      varchar     NOT NULL DEFAULT 'submitted',
    created_at  timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT chk_opinions_status CHECK (status IN ('submitted', 'reviewed', 'resolved'))
);

CREATE INDEX idx_opinions_company_id ON opinions(company_id);
CREATE INDEX idx_opinions_user_id    ON opinions(user_id);
CREATE INDEX idx_opinions_status     ON opinions(status);

-- ============================================================
-- 17. notifications - 알림 (→ companies, user_profiles)
-- ============================================================
CREATE TABLE notifications (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      uuid        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id         uuid        NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    type            varchar     NOT NULL,
    title           varchar     NOT NULL,
    message         text        NOT NULL,
    reference_id    uuid,
    reference_type  varchar,
    action_url      varchar,
    is_read         boolean     NOT NULL DEFAULT false,
    created_at      timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT chk_notifications_type CHECK (type IN ('task_assigned', 'task_updated', 'notice', 'feedback', 'system'))
);

CREATE INDEX idx_notifications_company_user ON notifications(company_id, user_id);
CREATE INDEX idx_notifications_unread       ON notifications(user_id, is_read) WHERE is_read = false;
CREATE INDEX idx_notifications_created_at   ON notifications(created_at);

-- ============================================================
-- 18. notices - 공지사항 (→ companies, branches, user_profiles)
-- ============================================================
CREATE TABLE notices (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      uuid        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    branch_id       uuid        REFERENCES branches(id) ON DELETE SET NULL,
    author_id       uuid        REFERENCES user_profiles(id) ON DELETE SET NULL,
    author_name     varchar     NOT NULL,
    author_role     varchar,
    title           varchar     NOT NULL,
    content         text        NOT NULL,
    is_important    boolean     NOT NULL DEFAULT false,
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_notices_company_id   ON notices(company_id);
CREATE INDEX idx_notices_branch_id    ON notices(branch_id);
CREATE INDEX idx_notices_created_at   ON notices(created_at);
CREATE INDEX idx_notices_is_important ON notices(is_important);

-- ============================================================
-- 19. notice_confirmations - 공지 확인 (→ notices, user_profiles)
-- ============================================================
CREATE TABLE notice_confirmations (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    notice_id   uuid        NOT NULL REFERENCES notices(id) ON DELETE CASCADE,
    user_id     uuid        NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    created_at  timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_notice_confirmations_notice_user UNIQUE (notice_id, user_id)
);

-- ============================================================
-- 20. feedbacks - 피드백 (→ companies, assignments, branches, user_profiles)
-- ============================================================
CREATE TABLE feedbacks (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      uuid        NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    assignment_id   uuid        REFERENCES assignments(id) ON DELETE SET NULL,
    branch_id       uuid        REFERENCES branches(id) ON DELETE SET NULL,
    author_id       uuid        NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    target_user_id  uuid        REFERENCES user_profiles(id) ON DELETE SET NULL,
    content         text        NOT NULL,
    status          varchar,
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_feedbacks_company_id     ON feedbacks(company_id);
CREATE INDEX idx_feedbacks_assignment_id  ON feedbacks(assignment_id);
CREATE INDEX idx_feedbacks_author_id      ON feedbacks(author_id);
CREATE INDEX idx_feedbacks_target_user_id ON feedbacks(target_user_id);

-- ============================================================
-- updated_at 자동 갱신 트리거 함수
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- updated_at 트리거 적용 (updated_at 컬럼이 있는 테이블)
CREATE TRIGGER trg_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_checklist_templates_updated_at
    BEFORE UPDATE ON checklist_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_assignments_updated_at
    BEFORE UPDATE ON assignments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
