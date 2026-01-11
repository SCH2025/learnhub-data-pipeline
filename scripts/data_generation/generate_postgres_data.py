#!/usr/bin/env python3
"""
PostgreSQL 測試數據生成器 - 優化版
解決 psycopg2 executemany 與 RETURNING 的衝突問題
"""

import random
import psycopg2
from psycopg2.extras import execute_values  # 引入高效批次插入工具
from faker import Faker
from datetime import datetime, timedelta
import numpy as np
from tqdm import tqdm

# 初始化 Faker
fake = Faker(['zh_TW', 'en_US'])
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# 資料庫連線配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'learnhub_prod',
    'user': 'admin',
    'password': 'admin123'
}

# 業務參數
START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2024, 1, 8)
TOTAL_DAYS = (END_DATE - START_DATE).days

# --- 輔助函式 ---

def get_signup_date():
    """模擬指數增長註冊日期"""
    progress = np.random.beta(2, 5)
    days_offset = int(progress * TOTAL_DAYS)
    return START_DATE + timedelta(days=days_offset)

COUNTRIES = {
    'TW': 0.35, 'SG': 0.20, 'HK': 0.15, 'MY': 0.12, 'VN': 0.10, 'US': 0.05, 'JP': 0.03
}

def weighted_choice(choices):
    items, weights = zip(*choices.items())
    return random.choices(items, weights=weights)[0]

# --- 數據生成函式 ---

def generate_categories(cursor):
    print("\n📂 生成課程分類...")
    categories = [
        ('程式開發', 'programming', '學習各種程式語言和開發技能'),
        ('數據科學', 'data-science', '數據分析、機器學習、AI 相關課程'),
        ('UI/UX 設計', 'design', 'UI/UX、平面設計、使用者體驗'),
        ('數位行銷', 'marketing', 'SEO、社群媒體、內容行銷'),
        ('商業管理', 'business', '專案管理、領導力、商業策略'),
        ('語言學習', 'languages', '英語、日語等語言課程'),
        ('個人成長', 'personal-development', '時間管理、溝通技巧'),
        ('財務金融', 'finance', '投資理財、會計、金融分析'),
        ('辦公技能', 'office-skills', 'Excel、PowerPoint、Office 工具'),
        ('攝影影像', 'photography', '攝影技巧、影片剪輯'),
        ('音樂藝術', 'music-art', '音樂創作、繪畫、藝術'),
        ('健康健身', 'health-fitness', '瑜伽、健身、營養學'),
        ('生活風格', 'lifestyle', '烹飪、園藝、手工藝'),
        ('教學教育', 'teaching', '教學方法、課程設計'),
        ('資訊安全', 'cybersecurity', '網路安全、資安防護')
    ]
    query = "INSERT INTO course_categories (category_name, category_slug, description) VALUES %s ON CONFLICT (category_slug) DO NOTHING"
    execute_values(cursor, query, categories)
    print(f"✅ 已生成 {len(categories)} 個分類")

def generate_instructors(cursor, count=200):
    print(f"\n👨‍🏫 生成 {count} 位講師...")
    instructor_data = []
    for _ in range(count):
        instructor_data.append((
            fake.name(),
            fake.email(),
            fake.text(max_nb_chars=300),
            START_DATE + timedelta(days=random.randint(0, TOTAL_DAYS - 180)),
            True
        ))
    
    query = "INSERT INTO instructors (full_name, email, bio, joined_date, is_active) VALUES %s RETURNING instructor_id"
    # 使用 fetch=True 獲取回傳的 ID
    ids = execute_values(cursor, query, instructor_data, fetch=True)
    print(f"✅ 已生成 {len(ids)} 位講師")
    return [row[0] for row in ids]

def generate_courses(cursor, instructor_ids, count=2000):
    print(f"\n📚 生成 {count} 門課程...")
    cursor.execute("SELECT category_id FROM course_categories;")
    category_ids = [row[0] for row in cursor.fetchall()]
    
    difficulty_levels = ['beginner', 'intermediate', 'advanced', 'all_levels']
    languages = ['zh-TW', 'en-US', 'zh-CN']
    
    course_data = []
    for i in range(count):
        is_published = random.random() < 0.9
        pub_date = START_DATE + timedelta(days=random.randint(0, TOTAL_DAYS - 30))
        course_data.append((
            f"{fake.catch_phrase()} - {fake.bs()}",
            f"course-{i+1}-{fake.slug()}",
            fake.text(max_nb_chars=500),
            random.choice(instructor_ids),
            random.choice(category_ids),
            random.choice(difficulty_levels),
            random.randint(30, 2400),
            random.randint(5, 200),
            random.choice(languages),
            round(random.uniform(9.99, 199.99), 2),
            is_published,
            pub_date if is_published else None
        ))
    
    query = """
        INSERT INTO courses (
            title, slug, description, instructor_id, category_id,
            difficulty_level, duration_minutes, total_lectures,
            language, price_usd, is_published, published_date
        ) VALUES %s RETURNING course_id
    """
    ids = execute_values(cursor, query, course_data, fetch=True)
    print(f"✅ 已生成 {len(ids)} 門課程")
    return [row[0] for row in ids]

def generate_users(cursor, count=50000):
    print(f"\n👥 生成 {count} 位用戶...")
    user_ids = []
    batch_size = 5000 # 增加批次大小提高效率
    
    for batch_start in tqdm(range(0, count, batch_size)):
        batch_end = min(batch_start + batch_size, count)
        batch_data = []
        for i in range(batch_start, batch_end):
            batch_data.append((
                f"user{i+1}@example.com",
                f"user{i+1}",
                fake.name(),
                fake.sha256(),
                get_signup_date(),
                weighted_choice(COUNTRIES),
                random.random() < 0.8,
                random.random() < 0.7
            ))
        
        query = """
            INSERT INTO users (
                email, username, full_name, password_hash,
                signup_date, country, is_active, email_verified
            ) VALUES %s RETURNING user_id
        """
        # 修正：使用 execute_values 並設定 fetch=True 獲取 ID
        results = execute_values(cursor, query, batch_data, fetch=True)
        user_ids.extend([row[0] for row in results])
        
    print(f"✅ 已生成 {len(user_ids)} 位用戶")
    return user_ids

def generate_subscriptions(cursor, user_ids, count=120000):
    print(f"\n💳 生成 {count} 筆訂閱記錄...")
    cursor.execute("SELECT plan_id, plan_type FROM subscription_plans;")
    plans = {row[1]: row[0] for row in cursor.fetchall()}
    
    plan_weights = {'basic': 0.45, 'professional': 0.40, 'enterprise': 0.15}
    subscription_data = []
    
    # 為了後續 Payment 生成，需要暫存一些資訊
    # 但為了效能，我們分批寫入資料庫
    all_sub_info = []
    batch_size = 10000
    
    # 獲取所有用戶註冊日期，減少重複查詢
    cursor.execute("SELECT user_id, signup_date FROM users")
    user_signup_map = {row[0]: row[1] for row in cursor.fetchall()}

    for _ in tqdm(range(count)):
        user_id = random.choice(user_ids)
        plan_type = weighted_choice(plan_weights)
        plan_id = plans[plan_type]
        billing_cycle = random.choices(['monthly', 'annual'], weights=[0.8, 0.2])[0]
        
        signup_date = user_signup_map[user_id]
        start_date = signup_date + timedelta(days=random.randint(0, 30))
        
        if random.random() < 0.8:
            status, end_date, cancelled_at = 'active', None, None
        else:
            status = random.choice(['cancelled', 'expired'])
            cancelled_at = start_date + timedelta(days=random.randint(30, 180))
            end_date = cancelled_at
            
        subscription_data.append((
            user_id, plan_id, status, billing_cycle,
            start_date, end_date, cancelled_at, status == 'active'
        ))

    query = """
        INSERT INTO subscriptions (
            user_id, plan_id, status, billing_cycle,
            start_date, end_date, cancelled_at, auto_renew
        ) VALUES %s RETURNING subscription_id, user_id, start_date
    """
    results = execute_values(cursor, query, subscription_data, fetch=True)
    print(f"✅ 已生成 {len(results)} 筆訂閱")
    return results # 回傳包含 (id, user_id, start_date) 的元組列表

def generate_payments(cursor, subscription_results):
    print(f"\n💰 生成付款記錄...")
    
    # 預先載入方案價格
    cursor.execute("SELECT plan_id, price_monthly, price_annual FROM subscription_plans")
    plans_price = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
    
    # 預先載入訂閱的方案 ID (subscription_results 只包含 ID, User, Date)
    # 這裡需要訂閱與方案的對應關係
    cursor.execute("SELECT subscription_id, plan_id, status, billing_cycle FROM subscriptions")
    sub_detail_map = {row[0]: (row[1], row[2], row[3]) for row in cursor.fetchall()}

    payment_data = []
    for sub_id, user_id, start_date in tqdm(subscription_results):
        plan_id, status, billing_cycle = sub_detail_map[sub_id]
        price_monthly, price_annual = plans_price[plan_id]
        
        if status == 'active':
            months_active = (END_DATE - start_date).days // 30
            num_payments = min(months_active, 24) if billing_cycle == 'monthly' else max(1, months_active // 12)
        else:
            num_payments = random.randint(1, 3)
            
        for i in range(num_payments):
            pay_date = start_date + timedelta(days=(30 if billing_cycle == 'monthly' else 365) * i)
            if pay_date > END_DATE: break
            
            is_success = random.random() < 0.95
            payment_data.append((
                sub_id, user_id, float(price_monthly if billing_cycle == 'monthly' else price_annual),
                'USD', random.choice(['credit_card', 'paypal', 'bank_transfer']),
                'succeeded' if is_success else 'failed', f"txn_{fake.uuid4()}",
                random.choice(['stripe', 'paypal', 'ecpay']), pay_date if is_success else None
            ))

    query = """
        INSERT INTO payments (
            subscription_id, user_id, amount, currency,
            payment_method, payment_status, transaction_id,
            payment_gateway, paid_at
        ) VALUES %s
    """
    # 支付數據通常很多，分批寫入
    for i in range(0, len(payment_data), 10000):
        execute_values(cursor, query, payment_data[i:i+10000])
    print(f"✅ 已生成 {len(payment_data)} 筆付款記錄")

def generate_enrollments(cursor, user_ids, course_ids, count=300000):
    print(f"\n📖 生成 {count} 筆課程註冊...")
    
    cursor.execute("SELECT user_id, signup_date FROM users")
    user_signup_map = {row[0]: row[1] for row in cursor.fetchall()}
    cursor.execute("SELECT course_id, duration_minutes FROM courses")
    course_duration_map = {row[0]: row[1] for row in cursor.fetchall()}

    enrollment_data = []
    for _ in range(count):
        user_id = random.choice(user_ids)
        course_id = random.choice(course_ids)
        signup_date = user_signup_map[user_id]
        enrolled_at = signup_date + timedelta(days=random.randint(0, 365))
        
        if enrolled_at > END_DATE: continue
        
        progress = random.choices([0, 25, 50, 75, 100], weights=[0.3, 0.2, 0.2, 0.15, 0.15])[0]
        comp_at = enrolled_at + timedelta(days=random.randint(7, 60)) if progress == 100 else None
        watch_time = int(course_duration_map[course_id] * progress / 100)
        
        enrollment_data.append((user_id, course_id, enrolled_at, progress, comp_at, watch_time))

    # 處理衝突並寫入
    query = """
        INSERT INTO course_enrollments (
            user_id, course_id, enrolled_at, progress_percentage,
            completed_at, total_watch_time_minutes
        ) VALUES %s ON CONFLICT (user_id, course_id) DO NOTHING
    """
    for i in range(0, len(enrollment_data), 10000):
        execute_values(cursor, query, enrollment_data[i:i+10000])
    print(f"✅ 已完成課程註冊數據生成")

# --- 主程式 ---

def main():
    print("=" * 60)
    print("LearnHub PostgreSQL 測試數據生成器 (Optimized)")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✅ 資料庫連線成功")
        
        print("\n⚠️  是否清空現有數據？(y/n): ", end='')
        if input().lower() == 'y':
            cursor.execute("TRUNCATE TABLE payments, course_enrollments, subscriptions, users, courses, instructors, course_categories CASCADE;")
            conn.commit()
            print("✅ 數據已清空")
        
        start_time = datetime.now()
        
        # 依序執行
        generate_categories(cursor)
        inst_ids = generate_instructors(cursor)
        course_ids = generate_courses(cursor, inst_ids)
        user_ids = generate_users(cursor)
        sub_results = generate_subscriptions(cursor, user_ids)
        generate_payments(cursor, sub_results)
        generate_enrollments(cursor, user_ids, course_ids)
        
        conn.commit()
        
        elapsed = datetime.now() - start_time
        print(f"\n✨ 全部完成！總耗時：{elapsed}")
        
    except Exception as e:
        print(f"\n❌ 錯誤：{e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    main()