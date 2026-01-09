-- LearnHub PostgreSQL Indexes
-- 創建日期: 2024-01-08

-- ============================================
-- 1. users 表索引
-- ============================================
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_signup_date ON users(signup_date);
CREATE INDEX IF NOT EXISTS idx_users_country ON users(country);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- ============================================
-- 2. courses 表索引
-- ============================================
CREATE INDEX IF NOT EXISTS idx_courses_instructor_id ON courses(instructor_id);
CREATE INDEX IF NOT EXISTS idx_courses_category_id ON courses(category_id);
CREATE INDEX IF NOT EXISTS idx_courses_difficulty_level ON courses(difficulty_level);
CREATE INDEX IF NOT EXISTS idx_courses_is_published ON courses(is_published);
CREATE INDEX IF NOT EXISTS idx_courses_published_date ON courses(published_date);
CREATE INDEX IF NOT EXISTS idx_courses_average_rating ON courses(average_rating DESC);

-- 全文搜尋索引（課程標題和描述）
CREATE INDEX IF NOT EXISTS idx_courses_title_search ON courses USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_courses_description_search ON courses USING gin(to_tsvector('english', description));

-- ============================================
-- 3. subscriptions 表索引
-- ============================================
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan_id ON subscriptions(plan_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_start_date ON subscriptions(start_date);
CREATE INDEX IF NOT EXISTS idx_subscriptions_end_date ON subscriptions(end_date);

-- 複合索引（常用查詢組合）
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_status ON subscriptions(user_id, status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status_end_date ON subscriptions(status, end_date);

-- ============================================
-- 4. payments 表索引
-- ============================================
CREATE INDEX IF NOT EXISTS idx_payments_subscription_id ON payments(subscription_id);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_payment_status ON payments(payment_status);
CREATE INDEX IF NOT EXISTS idx_payments_paid_at ON payments(paid_at);
CREATE INDEX IF NOT EXISTS idx_payments_transaction_id ON payments(transaction_id);

-- ============================================
-- 5. course_enrollments 表索引
-- ============================================
CREATE INDEX IF NOT EXISTS idx_enrollments_user_id ON course_enrollments(user_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON course_enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_enrolled_at ON course_enrollments(enrolled_at);
CREATE INDEX IF NOT EXISTS idx_enrollments_completed_at ON course_enrollments(completed_at);

-- 複合索引
CREATE INDEX IF NOT EXISTS idx_enrollments_user_progress ON course_enrollments(user_id, progress_percentage);

-- ============================================
-- 驗證索引創建
-- ============================================
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;