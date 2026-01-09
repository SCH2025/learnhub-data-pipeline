-- LearnHub PostgreSQL Schema
-- 創建日期: 2024-01-08

-- ============================================
-- 1. 用戶表 (users)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(200),
    password_hash VARCHAR(255) NOT NULL,
    signup_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    country VARCHAR(2), -- ISO 3166-1 alpha-2
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE users IS '用戶基本資料表';
COMMENT ON COLUMN users.country IS 'ISO 3166-1 alpha-2 國碼 (TW, SG, US...)';

-- ============================================
-- 2. 課程分類表 (course_categories)
-- ============================================
CREATE TABLE IF NOT EXISTS course_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL,
    category_slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_category_id INTEGER REFERENCES course_categories(category_id),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE course_categories IS '課程分類表（支援階層結構）';

-- ============================================
-- 3. 講師表 (instructors)
-- ============================================
CREATE TABLE IF NOT EXISTS instructors (
    instructor_id SERIAL PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    bio TEXT,
    profile_image_url VARCHAR(500),
    linkedin_url VARCHAR(500),
    website_url VARCHAR(500),
    total_students INTEGER DEFAULT 0,
    total_courses INTEGER DEFAULT 0,
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    joined_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE instructors IS '課程講師資料表';

-- ============================================
-- 4. 課程表 (courses)
-- ============================================
CREATE TABLE IF NOT EXISTS courses (
    course_id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    slug VARCHAR(300) UNIQUE NOT NULL,
    description TEXT,
    instructor_id INTEGER NOT NULL REFERENCES instructors(instructor_id),
    category_id INTEGER NOT NULL REFERENCES course_categories(category_id),
    difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced', 'all_levels')),
    duration_minutes INTEGER NOT NULL, -- 總課程時長（分鐘）
    total_lectures INTEGER DEFAULT 0,
    language VARCHAR(10) DEFAULT 'zh-TW', -- BCP 47 語言標籤
    subtitle_languages TEXT[], -- 支援的字幕語言
    thumbnail_url VARCHAR(500),
    preview_video_url VARCHAR(500),
    price_usd DECIMAL(10,2) DEFAULT 0.00,
    is_published BOOLEAN DEFAULT FALSE,
    published_date TIMESTAMP,
    total_enrollments INTEGER DEFAULT 0,
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    total_reviews INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE courses IS '課程目錄資料表';
COMMENT ON COLUMN courses.duration_minutes IS '課程總時長（分鐘）';
COMMENT ON COLUMN courses.subtitle_languages IS 'PostgreSQL Array 儲存多語言字幕';

-- ============================================
-- 5. 訂閱方案表 (subscription_plans)
-- ============================================
CREATE TABLE IF NOT EXISTS subscription_plans (
    plan_id SERIAL PRIMARY KEY,
    plan_name VARCHAR(50) UNIQUE NOT NULL,
    plan_type VARCHAR(20) CHECK (plan_type IN ('basic', 'professional', 'enterprise')),
    price_monthly DECIMAL(10,2) NOT NULL,
    price_annual DECIMAL(10,2) NOT NULL,
    max_users INTEGER DEFAULT 1, -- 企業版支援多用戶
    features JSONB, -- 方案功能（JSON 格式）
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE subscription_plans IS '訂閱方案設定表';
COMMENT ON COLUMN subscription_plans.features IS 'JSON 格式儲存方案功能細節';

-- 插入預設方案
INSERT INTO subscription_plans (plan_name, plan_type, price_monthly, price_annual, features) VALUES
('基礎版', 'basic', 9.99, 95.90, '{"max_courses": 500, "video_quality": "720p", "download": false, "certificate": 3}'::jsonb),
('專業版', 'professional', 29.99, 287.90, '{"max_courses": 2000, "video_quality": "1080p", "download": true, "certificate": -1}'::jsonb),
('企業版', 'enterprise', 99.99, 959.90, '{"max_courses": 2000, "video_quality": "1080p", "download": true, "certificate": -1, "api_access": true}'::jsonb);

-- ============================================
-- 6. 訂閱記錄表 (subscriptions)
-- ============================================
CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    plan_id INTEGER NOT NULL REFERENCES subscription_plans(plan_id),
    status VARCHAR(20) CHECK (status IN ('active', 'cancelled', 'expired', 'past_due', 'trialing')) NOT NULL,
    billing_cycle VARCHAR(10) CHECK (billing_cycle IN ('monthly', 'annual')) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    trial_end_date TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    cancelled_at TIMESTAMP,
    cancellation_reason TEXT,
    auto_renew BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE subscriptions IS '用戶訂閱記錄表';
COMMENT ON COLUMN subscriptions.cancel_at_period_end IS '是否在當前週期結束後取消';

-- ============================================
-- 7. 付款記錄表 (payments)
-- ============================================
CREATE TABLE IF NOT EXISTS payments (
    payment_id SERIAL PRIMARY KEY,
    subscription_id INTEGER NOT NULL REFERENCES subscriptions(subscription_id),
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50), -- credit_card, paypal, bank_transfer
    payment_status VARCHAR(20) CHECK (payment_status IN ('succeeded', 'pending', 'failed', 'refunded')) NOT NULL,
    transaction_id VARCHAR(255) UNIQUE,
    payment_gateway VARCHAR(50), -- stripe, paypal, etc.
    paid_at TIMESTAMP,
    refunded_at TIMESTAMP,
    refund_amount DECIMAL(10,2),
    failure_reason TEXT,
    metadata JSONB, -- 額外的付款元數據
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE payments IS '付款交易記錄表';
COMMENT ON COLUMN payments.metadata IS 'JSON 格式儲存額外付款資訊';

-- ============================================
-- 8. 課程註冊表 (course_enrollments)
-- ============================================
CREATE TABLE IF NOT EXISTS course_enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    course_id INTEGER NOT NULL REFERENCES courses(course_id),
    enrolled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP,
    progress_percentage DECIMAL(5,2) DEFAULT 0.00 CHECK (progress_percentage BETWEEN 0 AND 100),
    completed_at TIMESTAMP,
    certificate_issued_at TIMESTAMP,
    certificate_url VARCHAR(500),
    total_watch_time_minutes INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, course_id)
);

COMMENT ON TABLE course_enrollments IS '用戶課程註冊記錄表';
COMMENT ON COLUMN course_enrollments.progress_percentage IS '課程完成進度（0-100%）';

-- ============================================
-- 創建更新時間觸發器函數
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 為所有資料表添加自動更新 updated_at 的觸發器
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN 
        SELECT table_name 
        FROM information_schema.columns 
        WHERE column_name = 'updated_at' 
        AND table_schema = 'public'
    LOOP
        EXECUTE format('
            DROP TRIGGER IF EXISTS update_%I_updated_at ON %I;
            CREATE TRIGGER update_%I_updated_at
                BEFORE UPDATE ON %I
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        ', t, t, t, t);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 驗證資料表創建
-- ============================================
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;