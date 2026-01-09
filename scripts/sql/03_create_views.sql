-- LearnHub PostgreSQL Views
-- 創建日期: 2024-01-08

-- ============================================
-- 1. 活躍訂閱視圖
-- ============================================
CREATE OR REPLACE VIEW v_active_subscriptions AS
SELECT 
    s.subscription_id,
    s.user_id,
    u.email,
    u.full_name,
    sp.plan_name,
    sp.plan_type,
    s.billing_cycle,
    s.start_date,
    s.end_date,
    CASE 
        WHEN s.billing_cycle = 'monthly' THEN sp.price_monthly
        WHEN s.billing_cycle = 'annual' THEN sp.price_annual
    END AS current_price,
    s.status,
    s.auto_renew
FROM subscriptions s
JOIN users u ON s.user_id = u.user_id
JOIN subscription_plans sp ON s.plan_id = sp.plan_id
WHERE s.status = 'active'
ORDER BY s.start_date DESC;

COMMENT ON VIEW v_active_subscriptions IS '活躍訂閱詳細資訊視圖';

-- ============================================
-- 2. 課程詳細資訊視圖
-- ============================================
CREATE OR REPLACE VIEW v_course_details AS
SELECT 
    c.course_id,
    c.title,
    c.slug,
    c.description,
    i.full_name AS instructor_name,
    i.instructor_id,
    cc.category_name,
    c.difficulty_level,
    c.duration_minutes,
    c.total_lectures,
    c.language,
    c.total_enrollments,
    c.average_rating,
    c.total_reviews,
    c.is_published,
    c.published_date,
    c.created_at
FROM courses c
JOIN instructors i ON c.instructor_id = i.instructor_id
JOIN course_categories cc ON c.category_id = cc.category_id
ORDER BY c.published_date DESC;

COMMENT ON VIEW v_course_details IS '課程完整資訊視圖（含講師和分類）';

-- ============================================
-- 3. 用戶學習進度視圖
-- ============================================
CREATE OR REPLACE VIEW v_user_learning_progress AS
SELECT 
    u.user_id,
    u.email,
    u.full_name,
    COUNT(ce.enrollment_id) AS total_enrolled_courses,
    COUNT(ce.completed_at) AS completed_courses,
    ROUND(AVG(ce.progress_percentage), 2) AS avg_progress_percentage,
    SUM(ce.total_watch_time_minutes) AS total_watch_time_minutes,
    MAX(ce.last_accessed_at) AS last_learning_activity
FROM users u
LEFT JOIN course_enrollments ce ON u.user_id = ce.user_id
WHERE u.is_active = TRUE
GROUP BY u.user_id, u.email, u.full_name
ORDER BY total_enrolled_courses DESC;

COMMENT ON VIEW v_user_learning_progress IS '用戶學習進度統計視圖';

-- ============================================
-- 4. 每月營收視圖 (MRR - Monthly Recurring Revenue)
-- ============================================
CREATE OR REPLACE VIEW v_monthly_revenue AS
SELECT 
    DATE_TRUNC('month', p.paid_at) AS revenue_month,
    sp.plan_type,
    COUNT(DISTINCT p.user_id) AS paying_users,
    COUNT(p.payment_id) AS total_payments,
    SUM(p.amount) AS total_revenue,
    AVG(p.amount) AS avg_payment_amount
FROM payments p
JOIN subscriptions s ON p.subscription_id = s.subscription_id
JOIN subscription_plans sp ON s.plan_id = sp.plan_id
WHERE p.payment_status = 'succeeded'
GROUP BY DATE_TRUNC('month', p.paid_at), sp.plan_type
ORDER BY revenue_month DESC, sp.plan_type;

COMMENT ON VIEW v_monthly_revenue IS '每月營收統計視圖（按方案類型分組）';

-- ============================================
-- 5. 熱門課程排行視圖
-- ============================================
CREATE OR REPLACE VIEW v_popular_courses AS
SELECT 
    c.course_id,
    c.title,
    i.full_name AS instructor_name,
    cc.category_name,
    c.total_enrollments,
    c.average_rating,
    c.total_reviews,
    COUNT(ce.enrollment_id) AS active_students,
    ROUND(AVG(ce.progress_percentage), 2) AS avg_completion_rate
FROM courses c
JOIN instructors i ON c.instructor_id = i.instructor_id
JOIN course_categories cc ON c.category_id = cc.category_id
LEFT JOIN course_enrollments ce ON c.course_id = ce.course_id
WHERE c.is_published = TRUE
GROUP BY c.course_id, c.title, i.full_name, cc.category_name, 
         c.total_enrollments, c.average_rating, c.total_reviews
ORDER BY c.total_enrollments DESC
LIMIT 50;

COMMENT ON VIEW v_popular_courses IS '熱門課程排行榜（前50名）';