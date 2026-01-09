// LearnHub MongoDB Indexes
// 創建日期: 2024-01-08

db = db.getSiblingDB('learnhub_logs');

print('===========================================');
print('創建 MongoDB Indexes');
print('===========================================\n');

// ============================================
// 1. user_events Indexes
// ============================================
print('創建 user_events 索引...');

db.user_events.createIndex({ user_id: 1, timestamp: -1 });
db.user_events.createIndex({ event_type: 1 });
db.user_events.createIndex({ timestamp: -1 });
db.user_events.createIndex({ session_id: 1 });
db.user_events.createIndex({ 'properties.course_id': 1 });

// 複合索引（常用查詢）
db.user_events.createIndex({ user_id: 1, event_type: 1, timestamp: -1 });

print('✅ user_events 索引創建完成\n');

// ============================================
// 2. course_reviews Indexes
// ============================================
print('創建 course_reviews 索引...');

db.course_reviews.createIndex({ course_id: 1, created_at: -1 });
db.course_reviews.createIndex({ user_id: 1 });
db.course_reviews.createIndex({ rating: -1 });
db.course_reviews.createIndex({ helpful_count: -1 });

// 複合索引
db.course_reviews.createIndex({ course_id: 1, rating: -1 });

// 文字搜尋索引
db.course_reviews.createIndex({ title: 'text', comment: 'text' });

print('✅ course_reviews 索引創建完成\n');

// ============================================
// 3. support_tickets Indexes
// ============================================
print('創建 support_tickets 索引...');

db.support_tickets.createIndex({ user_id: 1, created_at: -1 });
db.support_tickets.createIndex({ status: 1 });
db.support_tickets.createIndex({ priority: 1 });
db.support_tickets.createIndex({ issue_type: 1 });
db.support_tickets.createIndex({ assigned_agent: 1 });

// 複合索引
db.support_tickets.createIndex({ status: 1, priority: -1, created_at: -1 });

print('✅ support_tickets 索引創建完成\n');

// ============================================
// 驗證索引創建
// ============================================
print('===========================================');
print('驗證索引創建結果:');
print('===========================================\n');

['user_events', 'course_reviews', 'support_tickets'].forEach(function(colName) {
    print(`${colName} 索引列表:`);
    const indexes = db[colName].getIndexes();
    indexes.forEach(function(idx) {
        print(`  - ${idx.name}: ${JSON.stringify(idx.key)}`);
    });
    print('');
});

print('✅ MongoDB Indexes 創建完成！');