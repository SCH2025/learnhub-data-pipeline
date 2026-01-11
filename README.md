# LearnHub Data Pipeline

## 📊 專案簡介
端到端的數據工程專案，模擬 SaaS 訂閱制平台（LearnHub）的完整數據管道。

## 🛠️ 技術堆疊
-**資料庫**: PostgreSQL, MongoDB
-**編排工具**: Apache Airflow
-**雲端服務**: Google Cloud Storage
-**數據倉儲**: Snowflake
-**轉換工具**: dbt
-**視覺化**: Tableau
-**容器化**: Docker, Docker Compose

## 🚀 快速開始

### 前置需求
-Docker Desktop
-Python 3.9+
-Git

### 啟動環境
\`\`\`bash
# Clone repository
git clone https://github.com/你的使用者名稱/learnhub-data-pipeline.git
cd learnhub-data-pipeline

# 啟動所有服務
docker-compose up -d

# 訪問 Airflow
open http://localhost:8080
# Username: admin, Password: admin123
\`\`\`

## 📁 專案結構
\`\`\`
learnhub-data-pipeline/
├── dags/              # Airflow DAGs
├── dbt_project/       # dbt models
├── scripts/           # 數據生成和 ETL 腳本
├── config/            # 配置檔案
└── docs/              # 文件和截圖
\`\`\`

## ✅ Week 1 完成項目
-[x] Docker Compose 環境建立
-[x] PostgreSQL 資料庫啟動
-[x] MongoDB 資料庫啟動
-[x] Airflow 工作流編排工具啟動
-[x] 測試 DAG 執行成功

### Week 2: 資料庫 Schema 設計 ✨ NEW
-[x] PostgreSQL Schema 建立（8 個資料表）
-[x] PostgreSQL 索引和視圖建立
-[x] MongoDB Collections 建立（3 個）
-[x] MongoDB 索引建立
-[ ] 資料字典文件完成
-[ ] ERD 圖設計完成

### Week 3: 測試數據生成 ✨ NEW
-[x] PostgreSQL 數據生成腳本（50K 用戶 + 2K 課程）
-[x] MongoDB 數據生成腳本（5M 行為事件）
-[x] 數據品質驗證腳本
-[x] 完整的數據統計和驗證

#### 數據規模
-👥 50,000 位用戶（2 年增長曲線）
-📚 2,000 門課程（15 個分類）
-👨‍🏫 200 位講師
-💳 120,000 筆訂閱（80% 活躍、20% 流失）
-💰 152,000+ 筆付款記錄
-📖 300,000 筆課程註冊
-📊 5,000,000 筆用戶行為事件
-⭐ 50,000 筆課程評論
-🎫 10,000 筆客服工單