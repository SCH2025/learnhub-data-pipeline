#!/bin/bash

echo "=========================================="
echo "Week 1 環境驗證腳本"
echo "=========================================="
echo ""

echo "1️⃣ 檢查 Docker 容器狀態..."
docker-compose ps
echo ""

echo "2️⃣ 測試 PostgreSQL..."
docker exec -it learnhub_postgres psql -U admin -d learnhub_prod -c "SELECT 'PostgreSQL OK' AS status;" 2>/dev/null && echo "✅ PostgreSQL 正常" || echo "❌ PostgreSQL 異常"
echo ""

echo "3️⃣ 測試 MongoDB..."
docker exec -it learnhub_mongodb mongosh --username admin --password admin123 --quiet --eval "print('MongoDB OK')" 2>/dev/null && echo "✅ MongoDB 正常" || echo "❌ MongoDB 異常"
echo ""

echo "4️⃣ 測試 Airflow..."
curl -s http://localhost:8080/health | grep -q "healthy" && echo "✅ Airflow 正常" || echo "❌ Airflow 異常"
echo ""

echo "5️⃣ 列出 Airflow DAGs..."
docker exec -it airflow_webserver airflow dags list 2>/dev/null
echo ""

echo "=========================================="
echo "驗證完成！"
echo "=========================================="
