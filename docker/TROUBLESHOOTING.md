# O-RAN × Nephio RAG 系統故障排除指南

本文檔提供了 O-RAN × Nephio RAG 系統在 Docker 環境中常見問題的診斷和解決方案。

## 目錄

1. [快速故障排除](#快速故障排除)
2. [服務啟動問題](#服務啟動問題)
3. [效能問題](#效能問題)
4. [網路連接問題](#網路連接問題)
5. [資料庫問題](#資料庫問題)
6. [日誌和監控問題](#日誌和監控問題)
7. [安全問題](#安全問題)
8. [資源不足問題](#資源不足問題)
9. [常用診斷命令](#常用診斷命令)
10. [緊急恢復程序](#緊急恢復程序)

---

## 快速故障排除

### 系統健康檢查

```bash
# 檢查所有服務狀態
./docker/scripts/deploy.sh production status

# 執行健康檢查
./docker/scripts/deploy.sh production health

# 查看系統資源使用情況
docker stats --no-stream
```

### 常見問題快速診斷

| 症狀 | 可能原因 | 快速解決方案 |
|------|----------|-------------|
| 服務無法啟動 | 端口衝突 | `docker ps -a` 檢查端口使用 |
| 響應緩慢 | 記憶體不足 | `docker stats` 檢查資源使用 |
| 無法連接 | 網路問題 | `docker network ls` 檢查網路 |
| 資料遺失 | 數據卷問題 | `docker volume ls` 檢查數據卷 |

---

## 服務啟動問題

### 1. 容器無法啟動

**症狀**: 容器狀態顯示 `Exited` 或持續重啟

**診斷步驟**:
```bash
# 查看容器狀態
docker ps -a

# 查看容器日誌
docker logs <container_name> --tail=50

# 檢查容器配置
docker inspect <container_name>
```

**常見原因和解決方案**:

1. **環境變數未設定**
   ```bash
   # 檢查環境檔案
   cat docker/config/production.env
   
   # 確保必要變數已設定
   grep -E "(ANTHROPIC_API_KEY|SECRET_KEY|REDIS_PASSWORD)" docker/config/production.env
   ```

2. **端口衝突**
   ```bash
   # 查看端口使用情況
   netstat -tlnp | grep :8000
   
   # 修改端口配置
   vim docker-compose.production.yml
   ```

3. **映像不存在或損壞**
   ```bash
   # 重新建構映像
   ./docker/scripts/deploy.sh production build
   
   # 清理損壞的映像
   docker image prune -f
   ```

### 2. 服務依賴問題

**症狀**: 應用程式連接不到 Redis、資料庫等服務

**診斷步驟**:
```bash
# 檢查服務啟動順序
docker-compose -f docker-compose.production.yml ps

# 測試服務連接
docker exec oran-rag-app-production ping redis-master
docker exec oran-rag-redis-production redis-cli ping
```

**解決方案**:
```bash
# 重啟依賴服務
docker-compose -f docker-compose.production.yml restart redis-master

# 檢查網路連接
docker network inspect oran-rag-network-production
```

---

## 效能問題

### 1. 響應時間過長

**症狀**: API 響應時間超過 5 秒

**診斷步驟**:
```bash
# 檢查應用程式指標
curl http://localhost:9100/metrics | grep rag_query_duration

# 監控系統資源
docker stats --no-stream

# 檢查 Grafana 儀表板
# 訪問 http://localhost:3000
```

**解決方案**:

1. **CPU 資源不足**
   ```bash
   # 增加 CPU 限制
   vim docker-compose.production.yml
   # 在 services.oran-rag-app.deploy.resources.limits 中調整 cpus
   ```

2. **記憶體不足**
   ```bash
   # 增加記憶體限制
   vim docker-compose.production.yml
   # 調整 memory 設定
   
   # 重啟服務
   ./docker/scripts/deploy.sh production restart
   ```

3. **向量資料庫效能問題**
   ```bash
   # 檢查向量資料庫日誌
   docker logs oran-rag-app-production | grep -i chroma
   
   # 重建向量索引
   docker-compose -f docker-compose.production.yml exec oran-rag-app python -m src.rebuild_index
   ```

### 2. 記憶體洩漏

**症狀**: 應用程式記憶體使用量持續增長

**診斷步驟**:
```bash
# 監控記憶體使用趨勢
docker stats oran-rag-app-production --format "table {{.MemUsage}}\t{{.MemPerc}}"

# 檢查 Python 記憶體使用
docker exec oran-rag-app-production python -c "
import psutil
process = psutil.Process()
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

**解決方案**:
```bash
# 定期重啟應用程式 (臨時方案)
crontab -e
# 添加: 0 2 * * * /path/to/docker/scripts/deploy.sh production restart

# 啟用記憶體限制
echo 'MEMORY_LIMIT=2g' >> docker/config/production.env
./docker/scripts/deploy.sh production restart
```

---

## 網路連接問題

### 1. 外部網路無法訪問

**症狀**: 無法從外部訪問服務

**診斷步驟**:
```bash
# 檢查端口綁定
docker port oran-rag-nginx-production

# 檢查防火牆設定
sudo ufw status
sudo iptables -L

# 測試本地連接
curl -I http://localhost:8000/health
```

**解決方案**:
```bash
# 開放必要端口
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000

# 重啟 Nginx
docker-compose -f docker-compose.production.yml restart nginx
```

### 2. 內部服務通信問題

**症狀**: 服務之間無法通信

**診斷步驟**:
```bash
# 檢查 Docker 網路
docker network ls
docker network inspect oran-rag-network-production

# 測試內部連接
docker exec oran-rag-app-production ping redis-master
docker exec oran-rag-app-production nslookup redis-master
```

**解決方案**:
```bash
# 重建網路
docker network rm oran-rag-network-production
./docker/scripts/deploy.sh production deploy

# 檢查 DNS 設定
docker exec oran-rag-app-production cat /etc/resolv.conf
```

---

## 資料庫問題

### 1. Redis 連接問題

**症狀**: 應用程式無法連接到 Redis

**診斷步驟**:
```bash
# 檢查 Redis 狀態
docker exec oran-rag-redis-production redis-cli ping
docker exec oran-rag-redis-production redis-cli info replication

# 檢查 Redis 日誌
docker logs oran-rag-redis-production --tail=100
```

**解決方案**:
```bash
# 重啟 Redis
docker-compose -f docker-compose.production.yml restart redis-master

# 檢查 Redis 配置
docker exec oran-rag-redis-production cat /etc/redis/redis.conf

# 清理 Redis 數據 (謹慎使用)
docker exec oran-rag-redis-production redis-cli FLUSHALL
```

### 2. 向量資料庫問題

**症狀**: 向量搜索功能異常

**診斷步驟**:
```bash
# 檢查向量資料庫文件
docker exec oran-rag-app-production ls -la /app/oran_nephio_vectordb/

# 檢查嵌入檔案
docker exec oran-rag-app-production python -c "
import chromadb
client = chromadb.PersistentClient(path='/app/oran_nephio_vectordb')
collections = client.list_collections()
print(f'Collections: {[c.name for c in collections]}')
"
```

**解決方案**:
```bash
# 重建向量資料庫
docker exec oran-rag-app-production python -c "
from src.document_loader import DocumentLoader
loader = DocumentLoader()
loader.sync_and_process_documents()
"

# 備份和恢復
./docker/scripts/deploy.sh production backup
# 恢復: 解壓備份檔案到 /data/oran-rag/vectordb/
```

---

## 日誌和監控問題

### 1. 日誌無法查看

**症狀**: Docker 日誌命令無回應或錯誤

**診斷步驟**:
```bash
# 檢查日誌檔案大小
docker exec oran-rag-app-production du -sh /app/logs/

# 檢查磁碟空間
df -h
docker system df
```

**解決方案**:
```bash
# 清理舊日誌
./docker/scripts/cleanup.sh production logs

# 設定日誌輪轉
echo 'LOG_ROTATION=true' >> docker/config/production.env
echo 'LOG_MAX_SIZE=100MB' >> docker/config/production.env

# 重啟服務
./docker/scripts/deploy.sh production restart
```

### 2. 監控系統異常

**症狀**: Grafana 或 Prometheus 無法正常工作

**診斷步驟**:
```bash
# 檢查 Prometheus 狀態
curl http://localhost:9090/-/healthy

# 檢查 Grafana 狀態
curl http://localhost:3000/api/health

# 檢查監控服務日誌
docker logs oran-rag-prometheus-production
docker logs oran-rag-grafana-production
```

**解決方案**:
```bash
# 重啟監控服務
docker-compose -f docker-compose.production.yml restart prometheus grafana

# 重新載入 Prometheus 配置
curl -X POST http://localhost:9090/-/reload

# 檢查配置檔案語法
docker exec oran-rag-prometheus-production promtool check config /etc/prometheus/prometheus.yml
```

---

## 安全問題

### 1. SSL 憑證問題

**症狀**: HTTPS 連接失敗或憑證警告

**診斷步驟**:
```bash
# 檢查憑證有效期
openssl x509 -in /data/oran-rag/ssl/cert.pem -text -noout | grep -A 2 "Validity"

# 檢查 Nginx SSL 配置
docker exec oran-rag-nginx-production nginx -t
```

**解決方案**:
```bash
# 更新憑證 (使用 Let's Encrypt)
certbot renew --nginx

# 重新載入 Nginx 配置
docker exec oran-rag-nginx-production nginx -s reload

# 手動更新憑證路徑
vim docker/nginx/prod.conf
# 更新 ssl_certificate 和 ssl_certificate_key 路徑
```

### 2. 異常訪問模式

**症狀**: 監控顯示異常流量或攻擊嘗試

**診斷步驟**:
```bash
# 檢查 Nginx 訪問日誌
docker logs oran-rag-nginx-production | grep -E "(40[0-9]|50[0-9])"

# 查看安全告警
curl http://localhost:9090/api/v1/alerts | jq '.data.alerts[] | select(.labels.category=="security")'
```

**解決方案**:
```bash
# 啟用速率限制
vim docker/nginx/prod.conf
# 取消 limit_req_zone 和 limit_req 的註解

# 封鎖惡意 IP
docker exec oran-rag-nginx-production nginx -s reload

# 查看防火牆日誌
sudo tail -f /var/log/ufw.log
```

---

## 資源不足問題

### 1. 磁碟空間不足

**症狀**: 服務停止或無法寫入日誌

**診斷步驟**:
```bash
# 檢查磁碟使用情況
df -h
docker system df

# 查找大檔案
find /data/oran-rag -size +100M -exec ls -lh {} \;
```

**解決方案**:
```bash
# 清理 Docker 資源
./docker/scripts/cleanup.sh production all

# 清理應用程式日誌
find /data/oran-rag/logs -name "*.log" -mtime +7 -delete

# 清理備份檔案
find /data/oran-rag/backup -name "*.tar.gz" -mtime +30 -delete

# 清理系統日誌
sudo journalctl --vacuum-time=7d
```

### 2. 記憶體不足

**症狀**: 系統緩慢或 OOM Killer 啟動

**診斷步驟**:
```bash
# 檢查記憶體使用
free -h
docker stats --no-stream

# 檢查 OOM 事件
dmesg | grep -i "killed process"
journalctl -u docker | grep -i oom
```

**解決方案**:
```bash
# 調整容器記憶體限制
vim docker-compose.production.yml
# 減少 memory 設定

# 啟用 swap (臨時方案)
sudo swapon /swapfile

# 重啟高記憶體使用的容器
docker restart oran-rag-app-production
```

---

## 常用診斷命令

### 系統狀態檢查

```bash
# 完整系統狀態
./docker/scripts/deploy.sh production status

# 詳細容器資訊
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 資源使用監控
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# 網路連接測試
docker exec oran-rag-app-production netstat -tlnp
```

### 日誌分析

```bash
# 查看關鍵錯誤
docker logs oran-rag-app-production 2>&1 | grep -i error | tail -20

# 監控實時日誌
docker logs -f oran-rag-app-production | grep -E "(ERROR|WARN|EXCEPTION)"

# 分析效能日誌
docker logs oran-rag-app-production | grep "response_time" | tail -50
```

### 效能監控

```bash
# CPU 和記憶體趨勢
watch -n 5 'docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemPerc}}"'

# 磁碟 I/O 監控
iostat -x 1

# 網路流量監控
iftop -i docker0
```

---

## 緊急恢復程序

### 完全系統故障恢復

1. **停止所有服務**
   ```bash
   ./docker/scripts/deploy.sh production stop
   ```

2. **備份現有資料**
   ```bash
   cp -r /data/oran-rag /backup/oran-rag-$(date +%Y%m%d_%H%M%S)
   ```

3. **清理 Docker 環境**
   ```bash
   ./docker/scripts/cleanup.sh production all true
   docker system prune -a -f
   ```

4. **恢復服務**
   ```bash
   ./docker/scripts/deploy.sh production deploy
   ```

5. **驗證服務**
   ```bash
   ./docker/scripts/deploy.sh production health
   ```

### 資料恢復程序

1. **從備份恢復向量資料庫**
   ```bash
   # 停止應用程式
   docker stop oran-rag-app-production
   
   # 恢復資料
   tar -xzf /backup/oran-rag-backup-YYYYMMDD_HHMMSS.tar.gz -C /data/oran-rag/
   
   # 設定權限
   chown -R 1000:1000 /data/oran-rag/vectordb
   
   # 重啟服務
   docker start oran-rag-app-production
   ```

2. **重建向量索引**
   ```bash
   docker exec oran-rag-app-production python -c "
   from src.document_loader import DocumentLoader
   loader = DocumentLoader()
   loader.rebuild_vector_index()
   "
   ```

### 緊急聯絡資訊

| 問題類型 | 聯絡方式 | 響應時間 |
|----------|----------|----------|
| 系統故障 | ops-team@company.com | 15 分鐘 |
| 安全問題 | security@company.com | 5 分鐘 |
| 資料問題 | data-team@company.com | 30 分鐘 |

### 故障報告模板

```
【故障報告】O-RAN RAG 系統

時間: YYYY-MM-DD HH:MM:SS
環境: [開發/生產]
影響範圍: [具體描述]

症狀描述:
[詳細描述觀察到的問題]

診斷步驟:
[已執行的診斷命令和結果]

解決方案:
[採取的解決措施]

根本原因:
[問題的根本原因分析]

預防措施:
[為防止類似問題的改進建議]
```

---

## 故障預防建議

1. **定期維護**
   - 每日執行健康檢查
   - 每週清理日誌和臨時檔案
   - 每月更新系統和依賴項

2. **監控設定**
   - 配置關鍵指標告警
   - 設定日誌監控規則
   - 定期檢查儀表板

3. **備份策略**
   - 每日自動備份向量資料庫
   - 每週完整系統備份
   - 備份檔案的異地存儲

4. **文檔更新**
   - 及時更新故障處理經驗
   - 記錄配置變更
   - 維護系統架構文檔

---

如需更多協助，請參考：
- [Docker 官方文檔](https://docs.docker.com/)
- [Prometheus 監控指南](https://prometheus.io/docs/)
- [Nginx 配置參考](https://nginx.org/en/docs/)
- [Redis 故障排除](https://redis.io/topics/problems)