"""
測試 DAG - 驗證 Airflow 環境是否正常運作
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# 預設參數
default_args = {
    'owner': 'learnhub',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 定義 DAG
dag = DAG(
    'test_environment',
    default_args=default_args,
    description='測試 Airflow 環境和資料庫連線',
    schedule_interval=None,  # 手動觸發
    catchup=False,
    tags=['test', 'setup'],
)

# Task 1: 測試 Python 環境
def test_python():
    import sys
    import platform
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print("✅ Python 環境正常!")
    return "success"

test_python_task = PythonOperator(
    task_id='test_python_environment',
    python_callable=test_python,
    dag=dag,
)

# Task 2: 測試 PostgreSQL 連線
def test_postgres():
    import psycopg2
    
    try:
        conn = psycopg2.connect(
            host='postgres',
            port=5432,
            database='learnhub_prod',
            user='admin',
            password='admin123'
        )
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()
        print(f"PostgreSQL version: {version[0]}")
        cursor.close()
        conn.close()
        print("✅ PostgreSQL 連線成功!")
        return "success"
    except Exception as e:
        print(f"❌ PostgreSQL 連線失敗: {e}")
        raise

test_postgres_task = PythonOperator(
    task_id='test_postgres_connection',
    python_callable=test_postgres,
    dag=dag,
)

# Task 3: 測試 MongoDB 連線
def test_mongodb():
    from pymongo import MongoClient
    
    try:
        client = MongoClient(
            'mongodb://admin:admin123@mongodb:27017/',
            serverSelectionTimeoutMS=5000
        )
        # 測試連線
        client.admin.command('ping')
        print(f"MongoDB version: {client.server_info()['version']}")
        print("✅ MongoDB 連線成功!")
        client.close()
        return "success"
    except Exception as e:
        print(f"❌ MongoDB 連線失敗: {e}")
        raise

test_mongodb_task = PythonOperator(
    task_id='test_mongodb_connection',
    python_callable=test_mongodb,
    dag=dag,
)

# Task 4: 顯示環境資訊
print_env_task = BashOperator(
    task_id='print_environment_info',
    bash_command='echo "=== Environment Info ===" && date && hostname && echo "✅ Bash 命令執行成功!"',
    dag=dag,
)

# 定義任務執行順序
test_python_task >> print_env_task >> [test_postgres_task, test_mongodb_task]
