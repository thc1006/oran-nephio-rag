#!/bin/bash
# O-RAN × Nephio RAG 系統生產環境專用啟動腳本
# 針對生產環境優化的啟動流程

set -eo pipefail

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 日誌函數
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date -u '+%Y-%m-%dT%H:%M:%SZ') - $1" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date -u '+%Y-%m-%dT%H:%M:%SZ') - $1" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date -u '+%Y-%m-%dT%H:%M:%SZ') - $1" >&2
}

# 生產環境變數設定
export PYTHONPATH="/app"
export APP_ENV="production"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export WORKERS="${WORKERS:-4}"
export WORKER_TIMEOUT="${WORKER_TIMEOUT:-120}"
export MAX_REQUESTS="${MAX_REQUESTS:-1000}"
export MAX_REQUESTS_JITTER="${MAX_REQUESTS_JITTER:-100}"
export PRELOAD_APP="${PRELOAD_APP:-true}"

# 安全檢查
security_check() {
    log_info "執行生產環境安全檢查..."
    
    # 檢查是否以root用戶運行
    if [[ $(id -u) -eq 0 ]]; then
        log_error "安全警告：不應以root用戶運行生產應用"
        exit 1
    fi
    
    # 檢查敏感環境變數
    local required_vars=("ANTHROPIC_API_KEY" "SECRET_KEY")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            log_error "生產環境必須設定 ${var}"
            exit 1
        fi
    done
    
    # 檢查敏感文件權限
    local sensitive_files=(".env")
    for file in "${sensitive_files[@]}"; do
        if [[ -f "/app/${file}" ]]; then
            local perms=$(stat -c %a "/app/${file}" 2>/dev/null || echo "000")
            if [[ "${perms}" != "600" ]] && [[ "${perms}" != "400" ]]; then
                log_warn "敏感文件 ${file} 權限過於寬鬆: ${perms}"
            fi
        fi
    done
    
    log_info "安全檢查完成"
}

# 等待依賴服務
wait_for_dependencies() {
    log_info "等待依賴服務..."
    
    # 等待Redis
    if [[ -n "${REDIS_HOST}" && -n "${REDIS_PORT}" ]]; then
        local timeout=60
        local count=0
        
        while ! timeout 1 bash -c "cat < /dev/null > /dev/tcp/${REDIS_HOST}/${REDIS_PORT}" 2>/dev/null; do
            if [[ ${count} -ge ${timeout} ]]; then
                log_error "Redis 連線超時"
                exit 1
            fi
            sleep 1
            count=$((count + 1))
        done
        log_info "Redis 連線正常"
    fi
    
    # 等待資料庫（如果有的話）
    if [[ -n "${DATABASE_URL}" ]]; then
        log_info "檢查資料庫連線..."
        # 這裡可以加入資料庫連線檢查
    fi
}

# 預加載檢查
preload_check() {
    log_info "執行預加載檢查..."
    
    # 檢查Python模組
    if ! python -c "
import sys
sys.path.insert(0, '/app')
from src.config import Config, validate_config
from src.oran_nephio_rag import ORANNephioRAG
validate_config()
print('所有模組載入成功')
" 2>/dev/null; then
        log_error "模組預加載失敗"
        exit 1
    fi
    
    # 檢查向量資料庫
    if [[ -d "/app/oran_nephio_vectordb" ]] && [[ -n "$(ls -A /app/oran_nephio_vectordb 2>/dev/null)" ]]; then
        log_info "向量資料庫已存在"
    else
        log_warn "向量資料庫不存在，請確保已正確初始化"
    fi
    
    log_info "預加載檢查完成"
}

# 優雅關閉
graceful_shutdown() {
    log_info "收到關閉信號，開始優雅關閉..."
    
    # 發送SIGTERM給Gunicorn主程序
    if [[ -n "${GUNICORN_PID}" ]]; then
        kill -TERM "${GUNICORN_PID}" 2>/dev/null || true
        
        # 等待最多30秒
        local count=0
        while kill -0 "${GUNICORN_PID}" 2>/dev/null && [[ ${count} -lt 30 ]]; do
            sleep 1
            count=$((count + 1))
        done
        
        # 如果還在運行，強制結束
        if kill -0 "${GUNICORN_PID}" 2>/dev/null; then
            log_warn "強制結束應用程序"
            kill -KILL "${GUNICORN_PID}" 2>/dev/null || true
        fi
    fi
    
    log_info "應用程序已關閉"
    exit 0
}

# 設定信號處理
trap graceful_shutdown SIGTERM SIGINT SIGQUIT

# 健康檢查端點
setup_health_check() {
    log_info "設定健康檢查..."
    
    # 創建健康檢查腳本
    cat > /tmp/health_check.py << 'EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/app')

try:
    from src.config import Config
    from src.oran_nephio_rag import ORANNephioRAG
    
    # 簡單的健康檢查
    config = Config()
    print("OK")
    sys.exit(0)
except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)
EOF
    
    chmod +x /tmp/health_check.py
}

# 建立Gunicorn配置
create_gunicorn_config() {
    log_info "建立Gunicorn配置..."
    
    # 動態生成Gunicorn配置
    cat > /tmp/gunicorn.conf.py << EOF
import multiprocessing
import os

# 基本設定
bind = "0.0.0.0:8000"
workers = int(os.getenv("WORKERS", "4"))
worker_class = "sync"
worker_connections = 1000
timeout = int(os.getenv("WORKER_TIMEOUT", "120"))
keepalive = 2
max_requests = int(os.getenv("MAX_REQUESTS", "1000"))
max_requests_jitter = int(os.getenv("MAX_REQUESTS_JITTER", "100"))
preload_app = os.getenv("PRELOAD_APP", "true").lower() == "true"

# 日誌設定
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 程序名稱
proc_name = "oran-nephio-rag"

# 安全設定
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 效能調優
worker_tmp_dir = "/dev/shm"
tmp_upload_dir = "/tmp"

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal")
EOF
}

# 主函數
main() {
    log_info "========================================"
    log_info "O-RAN × Nephio RAG 生產環境啟動"
    log_info "Workers: ${WORKERS}"
    log_info "Timeout: ${WORKER_TIMEOUT}s"
    log_info "========================================"
    
    # 執行安全檢查
    security_check
    
    # 等待依賴服務
    wait_for_dependencies
    
    # 預加載檢查
    preload_check
    
    # 設定健康檢查
    setup_health_check
    
    # 建立Gunicorn配置
    create_gunicorn_config
    
    log_info "所有檢查通過，啟動生產服務器..."
    
    # 根據命令決定啟動方式
    if [[ "$1" == "health" ]]; then
        exec python /tmp/health_check.py
    elif [[ "$1" == "shell" ]]; then
        exec bash
    elif [[ "$1" == "init-db" ]]; then
        log_info "初始化向量資料庫"
        exec python -c "
from src.oran_nephio_rag import ORANNephioRAG
rag = ORANNephioRAG()
if rag.build_vector_database():
    print('向量資料庫初始化成功')
else:
    print('向量資料庫初始化失敗')
    exit(1)
"
    else
        # 啟動Gunicorn服務器
        log_info "啟動Gunicorn WSGI服務器"
        
        # 創建WSGI應用
        cat > /tmp/wsgi.py << 'EOF'
import sys
sys.path.insert(0, '/app')

from src.oran_nephio_rag import ORANNephioRAG, quick_query
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化RAG系統
rag_system = None

def init_rag():
    global rag_system
    if rag_system is None:
        try:
            rag_system = ORANNephioRAG()
            rag_system.load_existing_database()
            rag_system.setup_qa_chain()
            logger.info("RAG系統初始化成功")
        except Exception as e:
            logger.error(f"RAG系統初始化失敗: {e}")
            raise

@app.route('/health')
def health():
    try:
        if rag_system is None:
            init_rag()
        return jsonify({"status": "healthy", "service": "oran-nephio-rag"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/query', methods=['POST'])
def query():
    try:
        if rag_system is None:
            init_rag()
        
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Missing question"}), 400
        
        result = rag_system.query(data['question'])
        return jsonify(result)
    except Exception as e:
        logger.error(f"查詢錯誤: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_rag()
    app.run(host="0.0.0.0", port=8000)
EOF
        
        exec gunicorn \
            --config /tmp/gunicorn.conf.py \
            --pid /tmp/gunicorn.pid \
            wsgi:app &
        
        GUNICORN_PID=$!
        wait "${GUNICORN_PID}"
    fi
}

# 執行主函數
main "$@"