// LearnHub MongoDB Collections 初始化
// 創建日期: 2024-01-08

// 連接到 learnhub_logs 資料庫
db = db.getSiblingDB('learnhub_logs');

print('===========================================');
print('初始化 LearnHub MongoDB Collections');
print('===========================================\n');

// ============================================
// 1. user_events Collection
// ============================================
print('創建 user_events collection...');
db.createCollection('user_events', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['event_id', 'user_id', 'event_type', 'timestamp'],
            properties: {
                event_id: {
                    bsonType: 'string',
                    description: '事件唯一識別碼'
                },
                user_id: {
                    bsonType: 'int',
                    description: '用戶 ID（對應 PostgreSQL users.user_id）'
                },
                session_id: {
                    bsonType: 'string',
                    description: '用戶會話 ID'
                },
                event_type: {
                    enum: ['page_view', 'video_start', 'video_progress', 'video_complete', 
                           'course_enroll', 'course_complete', 'search', 'download', 
                           'certificate_download', 'login', 'logout'],
                    description: '事件類型'
                },
                timestamp: {
                    bsonType: 'date',
                    description: '事件發生時間'
                },
                properties: {
                    bsonType: 'object',
                    description: '事件屬性（靈活欄位）'
                },
                device: {
                    bsonType: 'object',
                    description: '設備資訊'
                },
                location: {
                    bsonType: 'object',
                    description: '地理位置資訊'
                }
            }
        }
    }
});

// 插入範例文檔
db.user_events.insertOne({
    event_id: 'evt_example_001',
    user_id: 1,
    session_id: 'sess_abc123',
    event_type: 'video_progress',
    timestamp: new Date(),
    properties: {
        course_id: 101,
        video_id: 'vid_001',
        watch_duration: 320,
        total_duration: 600,
        completion_rate: 0.53,
        quality: '1080p'
    },
    device: {
        type: 'mobile',
        os: 'iOS',
        browser: 'Safari',
        screen_width: 390,
        screen_height: 844
    },
    location: {
        country: 'TW',
        city: 'Taipei',
        ip_address: '192.168.1.1'
    }
});

print('✅ user_events collection 創建完成\n');

// ============================================
// 2. course_reviews Collection
// ============================================
print('創建 course_reviews collection...');
db.createCollection('course_reviews', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['review_id', 'user_id', 'course_id', 'rating', 'created_at'],
            properties: {
                review_id: {
                    bsonType: 'string',
                    description: '評論唯一識別碼'
                },
                user_id: {
                    bsonType: 'int',
                    description: '用戶 ID'
                },
                course_id: {
                    bsonType: 'int',
                    description: '課程 ID'
                },
                rating: {
                    bsonType: 'double',
                    minimum: 1,
                    maximum: 5,
                    description: '評分（1-5星）'
                },
                title: {
                    bsonType: 'string',
                    description: '評論標題'
                },
                comment: {
                    bsonType: 'string',
                    description: '評論內容'
                },
                tags: {
                    bsonType: 'array',
                    description: '標籤列表'
                },
                helpful_count: {
                    bsonType: 'int',
                    description: '有幫助數'
                },
                replies: {
                    bsonType: 'array',
                    description: '嵌套的回覆列表'
                },
                created_at: {
                    bsonType: 'date',
                    description: '創建時間'
                },
                updated_at: {
                    bsonType: 'date',
                    description: '更新時間'
                }
            }
        }
    }
});

// 插入範例文檔
db.course_reviews.insertOne({
    review_id: 'rev_example_001',
    user_id: 1,
    course_id: 101,
    rating: 4.5,
    title: '非常實用的課程！',
    comment: '講師講解清晰，案例豐富，學到很多實戰技巧。唯一建議是可以加快一點節奏。',
    tags: ['beginner-friendly', 'practical', 'well-structured'],
    helpful_count: 23,
    replies: [
        {
            reply_id: 'rep_001',
            user_id: 999,
            user_name: '講師回覆',
            comment: '感謝您的寶貴意見！我們會在下次更新時調整節奏。',
            created_at: new Date()
        }
    ],
    created_at: new Date('2024-01-05'),
    updated_at: new Date('2024-01-05')
});

print('✅ course_reviews collection 創建完成\n');

// ============================================
// 3. support_tickets Collection
// ============================================
print('創建 support_tickets collection...');
db.createCollection('support_tickets', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['ticket_id', 'user_id', 'status', 'created_at'],
            properties: {
                ticket_id: {
                    bsonType: 'string',
                    description: '工單唯一識別碼'
                },
                user_id: {
                    bsonType: 'int',
                    description: '用戶 ID'
                },
                subject: {
                    bsonType: 'string',
                    description: '工單主題'
                },
                issue_type: {
                    enum: ['login_issue', 'payment_issue', 'technical_issue', 
                           'course_content', 'refund_request', 'other'],
                    description: '問題類型'
                },
                priority: {
                    enum: ['low', 'medium', 'high', 'urgent'],
                    description: '優先級'
                },
                status: {
                    enum: ['open', 'in_progress', 'waiting_user', 'resolved', 'closed'],
                    description: '工單狀態'
                },
                messages: {
                    bsonType: 'array',
                    description: '對話訊息歷史（嵌套文檔）'
                },
                assigned_agent: {
                    bsonType: 'string',
                    description: '負責客服人員'
                },
                tags: {
                    bsonType: 'array',
                    description: '標籤'
                },
                attachments: {
                    bsonType: 'array',
                    description: '附件列表'
                },
                created_at: {
                    bsonType: 'date',
                    description: '創建時間'
                },
                updated_at: {
                    bsonType: 'date',
                    description: '最後更新時間'
                },
                resolved_at: {
                    bsonType: 'date',
                    description: '解決時間'
                }
            }
        }
    }
});

// 插入範例文檔
db.support_tickets.insertOne({
    ticket_id: 'tick_example_001',
    user_id: 1,
    subject: '無法登入帳號',
    issue_type: 'login_issue',
    priority: 'high',
    status: 'resolved',
    messages: [
        {
            message_id: 'msg_001',
            sender: 'user',
            sender_name: '王小明',
            text: '我無法登入我的帳號，一直顯示密碼錯誤。',
            timestamp: new Date('2024-01-05T10:00:00Z'),
            attachments: []
        },
        {
            message_id: 'msg_002',
            sender: 'agent',
            sender_name: '客服 Lisa',
            text: '您好，請問您是否有嘗試「忘記密碼」功能？',
            timestamp: new Date('2024-01-05T10:15:00Z'),
            attachments: []
        },
        {
            message_id: 'msg_003',
            sender: 'user',
            sender_name: '王小明',
            text: '有的，但沒有收到重設密碼的郵件。',
            timestamp: new Date('2024-01-05T10:20:00Z'),
            attachments: []
        },
        {
            message_id: 'msg_004',
            sender: 'agent',
            sender_name: '客服 Lisa',
            text: '我已經幫您重新發送重設郵件到您的註冊信箱，請查收垃圾郵件匣。',
            timestamp: new Date('2024-01-05T10:25:00Z'),
            attachments: []
        },
        {
            message_id: 'msg_005',
            sender: 'user',
            sender_name: '王小明',
            text: '收到了，謝謝！已成功重設密碼並登入。',
            timestamp: new Date('2024-01-05T10:35:00Z'),
            attachments: []
        }
    ],
    assigned_agent: 'agent_lisa',
    tags: ['login', 'password_reset', 'resolved'],
    attachments: [],
    created_at: new Date('2024-01-05T10:00:00Z'),
    updated_at: new Date('2024-01-05T10:35:00Z'),
    resolved_at: new Date('2024-01-05T10:35:00Z')
});

print('✅ support_tickets collection 創建完成\n');

// ============================================
// 驗證 Collections 創建
// ============================================
print('===========================================');
print('驗證 Collections 創建結果:');
print('===========================================');

const collections = db.getCollectionNames();
print('Collections 列表:');
collections.forEach(function(col) {
    const count = db[col].countDocuments();
    print(`  - ${col}: ${count} 筆文檔`);
});

print('\n✅ MongoDB Collections 初始化完成！');