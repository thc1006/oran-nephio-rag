#!/bin/bash
# O-RAN × Nephio RAG 系統通用啟動腳本
# 支援開發和生產環境的統一入口點

set -e

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日誌函數
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_debug() {
    if [[ "${LOG_LEVEL}" == "DEBUG" ]]; then
        echo -e "${BLUE}[DEBUG]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
    fi
}

# 環境變數預設值
export PYTHONPATH="${PYTHONPATH:-/app}"
export APP_ENV="${APP_ENV:-development}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export WORKERS="${WORKERS:-1}"

# 檢查必要目錄
check_directories() {
    log_info "檢查必要目錄..."
    
    local dirs=("logs" "oran_nephio_vectordb" "embeddings_cache" "data")
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "/app/${dir}" ]]; then
            log_info "創建目錄: ${dir}"
            mkdir -p "/app/${dir}"
        fi
    done
}

# 等待依賴服務
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local timeout=${4:-30}
    
    log_info "等待 ${service_name} 服務啟動 (${host}:${port})..."
    
    local count=0
    while ! nc -z "${host}" "${port}" 2>/dev/null; do
        if [[ ${count} -ge ${timeout} ]]; then
            log_error "${service_name} 服務啟動超時"
            exit 1
        fi
        log_debug "等待 ${service_name}... (${count}/${timeout})"
        sleep 1
        count=$((count + 1))
    done
    
    log_info "${service_name} 服務已就緒"
}

# 檢查Redis連線
check_redis() {
    if [[ -n "${REDIS_HOST}" && -n "${REDIS_PORT}" ]]; then
        wait_for_service "${REDIS_HOST}" "${REDIS_PORT}" "Redis" 30
    fi
}

# 檢查環境變數
check_environment() {
    log_info "檢查環境配置..."
    
    # 必要環境變數
    local required_vars=("ANTHROPIC_API_KEY")
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            log_error "必要環境變數 ${var} 未設定"
            exit 1
        fi
    done
    
    # 生產環境額外檢查
    if [[ "${APP_ENV}" == "production" ]]; then
        if [[ -z "${SECRET_KEY}" ]]; then
            log_error "生產環境必須設定 SECRET_KEY"
            exit 1
        fi
    fi
    
    log_info "環境變數檢查完成"
}

# 初始化應用
initialize_app() {
    log_info "初始化應用程式..."
    
    # 檢查Python語法
    if ! python -m py_compile main.py; then
        log_error "Python語法檢查失敗"
        exit 1
    fi
    
    # 驗證配置
    if ! python -c "from src.config import validate_config; validate_config()"; then
        log_error "配置驗證失敗"
        exit 1
    fi
    
    # 檢查向量資料庫
    if [[ ! -d "/app/oran_nephio_vectordb" ]] || [[ -z "$(ls -A /app/oran_nephio_vectordb 2>/dev/null)" ]]; then
        log_warn "向量資料庫不存在，需要初始建立"
        # 這裡可以加入自動建立向量資料庫的邏輯
    fi
    
    log_info "應用程式初始化完成"
}

# 健康檢查
health_check() {
    log_info "執行健康檢查..."
    
    # 檢查Python模組
    if ! python -c "import src.oran_nephio_rag; print('RAG模組正常')"; then
        log_error "RAG模組檢查失敗"
        return 1
    fi
    
    # 檢查API連線（如果設定了的話）
    if [[ -n "${ANTHROPIC_API_KEY}" ]]; then
        log_debug "API金鑰已設定，跳過連線測試"
    fi
    
    log_info "健康檢查完成"
    return 0
}

# 信號處理
cleanup() {
    log_info "收到終止信號，正在清理..."
    
    # 終止子程序
    if [[ -n "${APP_PID}" ]]; then
        kill -TERM "${APP_PID}" 2>/dev/null || true
        wait "${APP_PID}" 2>/dev/null || true
    fi
    
    log_info "清理完成"
    exit 0
}

# 註冊信號處理
trap cleanup SIGTERM SIGINT

# 主函數
main() {
    log_info "==================================="
    log_info "O-RAN × Nephio RAG 系統啟動中..."
    log_info "環境: ${APP_ENV}"
    log_info "日誌級別: ${LOG_LEVEL}"
    log_info "==================================="
    
    # 執行檢查
    check_directories
    check_environment
    check_redis
    initialize_app
    
    # 健康檢查
    if ! health_check; then
        log_error "健康檢查失敗，啟動終止"
        exit 1
    fi
    
    log_info "所有檢查通過，啟動應用程式..."
    
    # 根據環境執行不同命令
    if [[ "$1" == "bash" ]] || [[ "$1" == "sh" ]]; then
        # 調試模式
        log_info "進入調試模式"
        exec "$@"
    elif [[ "$1" == "test" ]]; then
        # 測試模式
        log_info "執行測試"
        exec python -m pytest tests/ -v
    elif [[ "$1" == "init-db" ]]; then
        # 初始化資料庫
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
        # 正常啟動應用
        log_info "啟動主應用程式"
        
        # 在背景執行主程式
        "$@" &
        APP_PID=$!
        
        # 等待程式結束
        wait "${APP_PID}"
    fi
}

# 執行主函數
main "$@"