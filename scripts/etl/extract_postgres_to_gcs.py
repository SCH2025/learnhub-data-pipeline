#!/usr/bin/env python3
"""
ETL Pipeline: PostgreSQL → GCS
從 PostgreSQL 抽取數據並上傳到 Google Cloud Storage (Parquet 格式)
"""

import os
import psycopg2
import pandas as pd
from google.cloud import storage
from datetime import datetime
import logging
from pathlib import Path

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# 配置
# ============================================
PG_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'learnhub_prod',
    'user': 'admin',
    'password': 'admin123'
}

GCS_BUCKET = 'learnhub-raw-data-2025-0112'  
GCS_PREFIX = 'raw/'

# 設定 Service Account 金鑰路徑
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './config/gcp/service-account-key.json'

# ============================================
# 要抽取的資料表
# ============================================
TABLES = [
    'users',
    'subscriptions',
    'courses',
    'instructors',
    'course_categories',
    'subscription_plans',
    'payments',
    'course_enrollments'
]

# ============================================
# 抽取數據
# ============================================
def extract_table(conn, table_name):
    """從 PostgreSQL 抽取單一資料表"""
    logger.info(f"📥 抽取資料表：{table_name}")
    
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql(query, conn)
    
    logger.info(f"  ✅ 抽取完成：{len(df):,} 筆記錄")
    return df

# ============================================
# 上傳到 GCS
# ============================================
def upload_to_gcs(df, table_name, bucket_name, prefix):
    """上傳 DataFrame 到 GCS（Parquet 格式）"""
    logger.info(f"☁️  上傳到 GCS：{table_name}")
    
    # 生成檔案名稱（含日期）
    date_str = datetime.now().strftime('%Y%m%d')
    filename = f"{table_name}_{date_str}.parquet"
    
    # 暫存到本地
    local_path = f"/tmp/{filename}"
    df.to_parquet(local_path, index=False, compression='snappy', engine='pyarrow', coerce_timestamps='us', allow_truncated_timestamps=True)
    
    # 上傳到 GCS
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob_path = f"{prefix}{table_name}/{filename}"
    blob = bucket.blob(blob_path)
    
    blob.upload_from_filename(local_path)
    
    # 清理暫存檔案
    os.remove(local_path)
    
    logger.info(f"  ✅ 上傳完成：gs://{bucket_name}/{blob_path}")
    logger.info(f"  📊 檔案大小：{blob.size / 1024 / 1024:.2f} MB")
    
    return blob_path

# ============================================
# 主程式
# ============================================
def main():
    logger.info("=" * 60)
    logger.info("ETL Pipeline: PostgreSQL → GCS")
    logger.info("=" * 60)
    
    try:
        # 連接 PostgreSQL
        logger.info("\n🔌 連接 PostgreSQL...")
        conn = psycopg2.connect(**PG_CONFIG)
        logger.info("✅ PostgreSQL 連線成功")
        
        # 測試 GCS 連線
        logger.info("\n🔌 測試 GCS 連線...")
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET)
        if bucket.exists():
            logger.info(f"✅ GCS Bucket 存在：{GCS_BUCKET}")
        else:
            raise Exception(f"❌ GCS Bucket 不存在：{GCS_BUCKET}")
        
        # 開始 ETL
        logger.info("\n🚀 開始 ETL 流程...")
        logger.info(f"將抽取 {len(TABLES)} 個資料表\n")
        
        results = []
        
        for table in TABLES:
            try:
                # 抽取
                df = extract_table(conn, table)
                
                # 上傳
                blob_path = upload_to_gcs(df, table, GCS_BUCKET, GCS_PREFIX)
                
                results.append({
                    'table': table,
                    'rows': len(df),
                    'status': 'success',
                    'path': blob_path
                })
                
                logger.info("")  # 空行分隔
                
            except Exception as e:
                logger.error(f"❌ 處理 {table} 時發生錯誤：{e}")
                results.append({
                    'table': table,
                    'rows': 0,
                    'status': 'failed',
                    'error': str(e)
                })
        
        # 關閉連線
        conn.close()
        
        # 總結
        logger.info("=" * 60)
        logger.info("ETL 完成總結")
        logger.info("=" * 60)
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        total_rows = sum(r['rows'] for r in results if r['status'] == 'success')
        
        logger.info(f"✅ 成功：{success_count}/{len(TABLES)} 個資料表")
        logger.info(f"📊 總計：{total_rows:,} 筆記錄")
        
        if success_count < len(TABLES):
            logger.warning(f"⚠️  失敗：{len(TABLES) - success_count} 個資料表")
        
        logger.info("\n詳細結果：")
        for r in results:
            status_icon = "✅" if r['status'] == 'success' else "❌"
            logger.info(f"  {status_icon} {r['table']}: {r['rows']:,} 筆")
        
    except Exception as e:
        logger.error(f"❌ ETL 失敗：{e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())