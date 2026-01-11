#!/usr/bin/env python3
"""
MongoDB 測試數據生成器
生成用戶行為日誌、課程評論、客服工單
"""

import random
from faker import Faker
from datetime import datetime, timedelta
from pymongo import MongoClient
import numpy as np
from tqdm import tqdm
import psycopg2

fake = Faker(['zh_TW', 'en_US'])
Faker.seed(42)
random.seed(42)

# MongoDB 連線
MONGO_CONFIG = {
    'host': 'localhost',
    'port': 27017,
    'username': 'admin',
    'password': 'admin123',
    'database': 'learnhub_logs'
}

# PostgreSQL 連線（讀取參考數據）
PG_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'learnhub_prod',
    'user': 'admin',
    'password': 'admin123'
}

# ============================================
# 1. 生成用戶行為事件
# ============================================
def generate_user_events(collection, user_ids, course_ids, count=5000000):
    """生成用戶行為日誌"""
    print(f"\n📊 生成 {count:,} 筆用戶行為事件...")
    
    event_types = [
        'page_view',
        'video_start',
        'video_progress',
        'video_complete',
        'course_enroll',
        'search',
        'download',
        'login',
        'logout'
    ]
    
    devices = [
        {'type': 'desktop', 'os': 'Windows', 'browser': 'Chrome'},
        {'type': 'desktop', 'os': 'MacOS', 'browser': 'Safari'},
        {'type': 'mobile', 'os': 'iOS', 'browser': 'Safari'},
        {'type': 'mobile', 'os': 'Android', 'browser': 'Chrome'},
        {'type': 'tablet', 'os': 'iOS', 'browser': 'Safari'}
    ]
    
    batch_size = 10000
    
    for batch_start in tqdm(range(0, count, batch_size)):
        batch_end = min(batch_start + batch_size, count)
        batch_data = []
        
        for i in range(batch_start, batch_end):
            user_id = random.choice(user_ids)
            event_type = random.choice(event_types)
            
            # 時間戳（過去 2 年內）
            timestamp = datetime(2022, 1, 1) + timedelta(
                seconds=random.randint(0, 63072000)  # 2 年的秒數
            )
            
            device = random.choice(devices)
            
            # 事件屬性
            properties = {}
            
            if event_type in ['video_start', 'video_progress', 'video_complete']:
                course_id = random.choice(course_ids)
                properties = {
                    'course_id': course_id,
                    'video_id': f"vid_{random.randint(1, 50)}",
                    'watch_duration': random.randint(10, 3600),
                    'quality': random.choice(['360p', '720p', '1080p'])
                }
                
                if event_type == 'video_progress':
                    properties['completion_rate'] = round(random.uniform(0.1, 0.9), 2)
            
            elif event_type == 'search':
                properties = {
                    'query': fake.sentence(nb_words=3),
                    'results_count': random.randint(0, 100)
                }
            
            elif event_type == 'course_enroll':
                properties = {
                    'course_id': random.choice(course_ids),
                    'source': random.choice(['search', 'recommendation', 'direct'])
                }
            
            doc = {
                'event_id': f"evt_{i+1}",
                'user_id': user_id,
                'session_id': fake.uuid4(),
                'event_type': event_type,
                'timestamp': timestamp,
                'properties': properties,
                'device': device,
                'location': {
                    'country': random.choice(['TW', 'SG', 'HK', 'MY', 'VN']),
                    'city': fake.city(),
                    'ip_address': fake.ipv4()
                }
            }
            
            batch_data.append(doc)
        
        collection.insert_many(batch_data)
    
    print(f"✅ 已生成 {count:,} 筆用戶行為事件")

# ============================================
# 2. 生成課程評論
# ============================================
def generate_course_reviews(collection, user_ids, course_ids, count=50000):
    """生成課程評論"""
    print(f"\n⭐ 生成 {count:,} 筆課程評論...")
    
    positive_comments = [
        "非常實用的課程！",
        "講師講解清晰，案例豐富",
        "學到很多實戰技巧",
        "課程結構完整，循序漸進",
        "物超所值，強烈推薦"
    ]
    
    negative_comments = [
        "內容有點過時",
        "節奏太慢了",
        "範例不夠多",
        "講師口音較重",
        "期待更新內容"
    ]
    
    tags_pool = [
        'beginner-friendly',
        'practical',
        'well-structured',
        'outdated',
        'advanced',
        'interactive',
        'comprehensive'
    ]
    
    batch_data = []
    
    for i in tqdm(range(count)):
        user_id = random.choice(user_ids)
        course_id = random.choice(course_ids)
        
        # 評分（偏向高分）
        rating = np.random.beta(8, 2) * 4 + 1  # 1-5 星，偏向 4-5 星
        rating = round(rating, 1)
        
        # 根據評分選擇評論
        if rating >= 4.0:
            comment = random.choice(positive_comments) + " " + fake.sentence()
        else:
            comment = random.choice(negative_comments) + " " + fake.sentence()
        
        # 隨機標籤
        tags = random.sample(tags_pool, k=random.randint(1, 3))
        
        # 有幫助數（高分評論更多人覺得有幫助）
        helpful_count = int(np.random.exponential(10 if rating >= 4 else 3))
        
        created_at = datetime(2022, 1, 1) + timedelta(days=random.randint(0, 730))
        
        doc = {
            'review_id': f"rev_{i+1}",
            'user_id': user_id,
            'course_id': course_id,
            'rating': rating,
            'title': fake.sentence(nb_words=5),
            'comment': comment,
            'tags': tags,
            'helpful_count': helpful_count,
            'replies': [],
            'created_at': created_at,
            'updated_at': created_at
        }
        
        # 10% 的評論有講師回覆
        if random.random() < 0.1:
            doc['replies'].append({
                'reply_id': f"rep_{fake.uuid4()}",
                'user_id': 9999,
                'user_name': '講師回覆',
                'comment': '感謝您的寶貴意見！' + fake.sentence(),
                'created_at': created_at + timedelta(days=random.randint(1, 7))
            })
        
        batch_data.append(doc)
        
        # 批次插入
        if len(batch_data) >= 1000:
            collection.insert_many(batch_data)
            batch_data = []
    
    if batch_data:
        collection.insert_many(batch_data)
    
    print(f"✅ 已生成 {count:,} 筆課程評論")

# ============================================
# 3. 生成客服工單
# ============================================
def generate_support_tickets(collection, user_ids, count=10000):
    """生成客服工單"""
    print(f"\n🎫 生成 {count:,} 筆客服工單...")
    
    issue_types = [
        'login_issue',
        'payment_issue',
        'technical_issue',
        'course_content',
        'refund_request',
        'other'
    ]
    
    priorities = ['low', 'medium', 'high', 'urgent']
    statuses = ['open', 'in_progress', 'waiting_user', 'resolved', 'closed']
    
    batch_data = []
    
    for i in tqdm(range(count)):
        user_id = random.choice(user_ids)
        issue_type = random.choice(issue_types)
        priority = random.choices(priorities, weights=[0.4, 0.3, 0.2, 0.1])[0]
        status = random.choices(statuses, weights=[0.1, 0.15, 0.1, 0.4, 0.25])[0]
        
        created_at = datetime(2022, 1, 1) + timedelta(days=random.randint(0, 730))
        
        # 生成對話歷史
        messages = []
        num_messages = random.randint(2, 8)
        
        for j in range(num_messages):
            sender = 'user' if j % 2 == 0 else 'agent'
            messages.append({
                'message_id': f"msg_{fake.uuid4()}",
                'sender': sender,
                'sender_name': fake.name() if sender == 'user' else '客服專員',
                'text': fake.sentence(nb_words=15),
                'timestamp': created_at + timedelta(hours=j * 2),
                'attachments': []
            })
        
        resolved_at = None
        if status in ['resolved', 'closed']:
            resolved_at = created_at + timedelta(hours=num_messages * 2)
        
        doc = {
            'ticket_id': f"tick_{i+1}",
            'user_id': user_id,
            'subject': fake.sentence(nb_words=6),
            'issue_type': issue_type,
            'priority': priority,
            'status': status,
            'messages': messages,
            'assigned_agent': f"agent_{random.randint(1, 20)}",
            'tags': random.sample(['login', 'billing', 'technical', 'content'], k=random.randint(1, 2)),
            'attachments': [],
            'created_at': created_at,
            'updated_at': created_at + timedelta(hours=(num_messages - 1) * 2),
            'resolved_at': resolved_at
        }
        
        batch_data.append(doc)
        
        if len(batch_data) >= 1000:
            collection.insert_many(batch_data)
            batch_data = []
    
    if batch_data:
        collection.insert_many(batch_data)
    
    print(f"✅ 已生成 {count:,} 筆客服工單")

# ============================================
# 主程式
# ============================================
def main():
    print("=" * 60)
    print("LearnHub MongoDB 測試數據生成器")
    print("=" * 60)
    
    try:
        # 從 PostgreSQL 讀取用戶和課程 ID
        print("\n🔌 連接 PostgreSQL 讀取參考數據...")
        pg_conn = psycopg2.connect(**PG_CONFIG)
        cursor = pg_conn.cursor()
        
        cursor.execute("SELECT user_id FROM users LIMIT 10000;")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT course_id FROM courses;")
        course_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        pg_conn.close()
        
        print(f"✅ 讀取到 {len(user_ids):,} 位用戶, {len(course_ids):,} 門課程")
        
        # 連接 MongoDB
        print("\n🔌 連接 MongoDB...")
        client = MongoClient(
            f"mongodb://{MONGO_CONFIG['username']}:{MONGO_CONFIG['password']}@{MONGO_CONFIG['host']}:{MONGO_CONFIG['port']}/"
        )
        db = client[MONGO_CONFIG['database']]
        print("✅ MongoDB 連線成功")
        
        # 清空現有數據
        print("\n⚠️  是否清空現有數據？(y/n): ", end='')
        if input().lower() == 'y':
            print("🗑️  清空現有數據...")
            db.user_events.drop()
            db.course_reviews.drop()
            db.support_tickets.drop()
            print("✅ 數據已清空")
        
        # 開始生成數據
        start_time = datetime.now()
        
        # 1. 用戶行為事件
        generate_user_events(db.user_events, user_ids, course_ids, count=5000000)
        
        # 2. 課程評論
        generate_course_reviews(db.course_reviews, user_ids, course_ids, count=50000)
        
        # 3. 客服工單
        generate_support_tickets(db.support_tickets, user_ids, count=10000)
        
        # 完成
        elapsed = datetime.now() - start_time
        print("\n" + "=" * 60)
        print("✅ MongoDB 數據生成完成！")
        print("=" * 60)
        print(f"⏱️  總耗時：{elapsed}")
        print()
        
        # 統計
        print(f"📊 用戶行為事件：{db.user_events.count_documents({}):,}")
        print(f"⭐ 課程評論：{db.course_reviews.count_documents({}):,}")
        print(f"🎫 客服工單：{db.support_tickets.count_documents({}):,}")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ 錯誤：{e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()