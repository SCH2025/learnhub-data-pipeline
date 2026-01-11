#!/usr/bin/env python3
"""
數據品質驗證腳本
"""

import psycopg2
from pymongo import MongoClient

PG_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'learnhub_prod',
    'user': 'admin',
    'password': 'admin123'
}

def verify_postgres():
    print("=" * 60)
    print("PostgreSQL 數據驗證")
    print("=" * 60)
    
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor()
    
    # 1. 數量驗證
    print("\n📊 數據量統計：")
    tables = ['users', 'courses', 'instructors', 'subscriptions', 'payments', 'course_enrollments']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count:,}")
    
    # 2. 流失率驗證
    print("\n📉 訂閱流失率：")
    cursor.execute("""
        SELECT 
            status,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM subscriptions
        GROUP BY status
        ORDER BY count DESC;
    """)
    for status, count, pct in cursor.fetchall():
        print(f"  {status}: {count:,} ({pct}%)")
    
    # 3. 訂閱方案分布
    print("\n💳 訂閱方案分布：")
    cursor.execute("""
        SELECT 
            sp.plan_type,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM subscriptions s
        JOIN subscription_plans sp ON s.plan_id = sp.plan_id
        GROUP BY sp.plan_type
        ORDER BY count DESC;
    """)
    for plan, count, pct in cursor.fetchall():
        print(f"  {plan}: {count:,} ({pct}%)")
    
    # 4. 國家分布
    print("\n🌍 用戶國家分布：")
    cursor.execute("""
        SELECT 
            country,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM users
        GROUP BY country
        ORDER BY count DESC
        LIMIT 10;
    """)
    for country, count, pct in cursor.fetchall():
        print(f"  {country}: {count:,} ({pct}%)")
    
    # 5. 數據完整性檢查
    print("\n✅ 數據完整性檢查：")
    
    # 檢查孤立的訂閱
    cursor.execute("""
        SELECT COUNT(*) FROM subscriptions s
        WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.user_id = s.user_id);
    """)
    orphan_subs = cursor.fetchone()[0]
    print(f"  孤立訂閱（無對應用戶）: {orphan_subs} {'✅' if orphan_subs == 0 else '❌'}")
    
    # 檢查無效的付款
    cursor.execute("""
        SELECT COUNT(*) FROM payments p
        WHERE NOT EXISTS (SELECT 1 FROM subscriptions s WHERE s.subscription_id = p.subscription_id);
    """)
    orphan_payments = cursor.fetchone()[0]
    print(f"  孤立付款（無對應訂閱）: {orphan_payments} {'✅' if orphan_payments == 0 else '❌'}")
    
    # 6. 時間邏輯檢查
    print("\n⏰ 時間邏輯檢查：")
    cursor.execute("""
        SELECT COUNT(*) FROM subscriptions
        WHERE end_date IS NOT NULL AND end_date < start_date;
    """)
    invalid_dates = cursor.fetchone()[0]
    print(f"  結束日期早於開始日期: {invalid_dates} {'✅' if invalid_dates == 0 else '❌'}")
    
    cursor.close()
    conn.close()

def verify_mongodb():
    print("\n" + "=" * 60)
    print("MongoDB 數據驗證")
    print("=" * 60)
    
    client = MongoClient('mongodb://admin:admin123@localhost:27017/')
    db = client['learnhub_logs']
    
    # 1. 數量統計
    print("\n📊 數據量統計：")
    print(f"  user_events: {db.user_events.count_documents({}):,}")
    print(f"  course_reviews: {db.course_reviews.count_documents({}):,}")
    print(f"  support_tickets: {db.support_tickets.count_documents({}):,}")
    
    # 2. 事件類型分布
    print("\n📈 事件類型分布：")
    pipeline = [
        {'$group': {'_id': '$event_type', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 10}
    ]
    for doc in db.user_events.aggregate(pipeline):
        print(f"  {doc['_id']}: {doc['count']:,}")
    
    # 3. 評分分布
    print("\n⭐ 課程評分分布：")
    pipeline = [
        {
            '$bucket': {
                'groupBy': '$rating',
                'boundaries': [1, 2, 3, 4, 5, 5.1],
                'default': 'Other',
                'output': {'count': {'$sum': 1}}
            }
        }
    ]
    for doc in db.course_reviews.aggregate(pipeline):
        rating_range = f"{doc['_id']}-{doc['_id']+1}"
        print(f"  {rating_range} 星: {doc['count']:,}")
    
    # 4. 工單狀態分布
    print("\n🎫 客服工單狀態：")
    pipeline = [
        {'$group': {'_id': '$status', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    for doc in db.support_tickets.aggregate(pipeline):
        print(f"  {doc['_id']}: {doc['count']:,}")
    
    client.close()

if __name__ == '__main__':
    verify_postgres()
    verify_mongodb()
    
    print("\n" + "=" * 60)
    print("✅ 驗證完成！")
    print("=" * 60)