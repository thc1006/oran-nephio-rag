#!/bin/bash
# O-RAN × Nephio RAG 系統部署腳本
# 支援開發和生產環境的自動化部署

set -euo pipefail

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo -e "${BLUE}[DEBUG]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
    fi
}

# 設定變數
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ENVIRONMENT="${1:-development}"
ACTION="${2:-deploy}"
VERSION="${3:-latest}"

# 配置文件路徑
ENV_FILE="${PROJECT_ROOT}/docker/config/${ENVIRONMENT}.env"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.${ENVIRONMENT}.yml"

# 檢查環境
check_environment() {
    log_info "檢查部署環境..."
    
    # 檢查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安裝或不在 PATH 中"
        exit 1
    fi
    
    # 檢查 Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose 未安裝"
        exit 1
    fi
    
    # 檢查配置文件
    if [[ ! -f "${ENV_FILE}" ]]; then
        log_error "環境配置文件不存在: ${ENV_FILE}"
        exit 1
    fi
    
    if [[ ! -f "${COMPOSE_FILE}" ]]; then
        log_error "Docker Compose 文件不存在: ${COMPOSE_FILE}"
        exit 1
    fi
    
    log_info "環境檢查完成"
}

# 載入環境變數
load_environment() {
    log_info "載入環境變數..."
    
    # 載入環境配置
    set -a
    source "${ENV_FILE}"
    set +a
    
    # 設定額外變數
    export VERSION="${VERSION}"
    export COMPOSE_PROJECT_NAME="oran-rag-${ENVIRONMENT}"
    export DATA_PATH="${DATA_PATH:-/data/oran-rag}"
    
    log_info "環境變數載入完成"
}

# 檢查必要環境變數
check_required_variables() {
    log_info "檢查必要環境變數..."
    
    local required_vars=("ANTHROPIC_API_KEY")
    
    if [[ "${ENVIRONMENT}" == "production" ]]; then
        required_vars+=("SECRET_KEY" "REDIS_PASSWORD")
    fi
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("${var}")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "缺少必要環境變數: ${missing_vars[*]}"
        log_error "請在 ${ENV_FILE} 中設定這些變數"
        exit 1
    fi
    
    log_info "環境變數檢查完成"
}

# 準備資料目錄
prepare_data_directories() {
    log_info "準備資料目錄..."
    
    local dirs=(
        "${DATA_PATH}"
        "${DATA_PATH}/logs"
        "${DATA_PATH}/vectordb"
        "${DATA_PATH}/embeddings"
        "${DATA_PATH}/backup"
    )
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "${dir}" ]]; then
            log_info "創建目錄: ${dir}"
            mkdir -p "${dir}"
            
            # 設定權限 (生產環境更嚴格)
            if [[ "${ENVIRONMENT}" == "production" ]]; then
                chmod 750 "${dir}"
            else
                chmod 755 "${dir}"
            fi
        fi
    done
    
    log_info "資料目錄準備完成"
}

# 建構映像
build_images() {
    log_info "建構 Docker 映像..."
    
    cd "${PROJECT_ROOT}"
    
    if [[ "${ENVIRONMENT}" == "production" ]]; then
        # 生產環境建構
        docker build \
            --file Dockerfile.production \
            --target production \
            --build-arg PYTHON_VERSION=3.11 \
            --tag "oran-rag:${VERSION}" \
            --tag "oran-rag:latest" \
            .
    else
        # 開發環境建構
        docker build \
            --file Dockerfile \
            --target development \
            --build-arg PYTHON_VERSION=3.11 \
            --tag "oran-rag:dev-${VERSION}" \
            --tag "oran-rag:dev-latest" \
            .
    fi
    
    log_info "映像建構完成"
}

# 拉取映像
pull_images() {
    log_info "拉取依賴映像..."
    
    cd "${PROJECT_ROOT}"
    
    # 使用 docker-compose 拉取映像
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "${COMPOSE_FILE}" pull
    else
        docker compose -f "${COMPOSE_FILE}" pull
    fi
    
    log_info "映像拉取完成"
}

# 啟動服務
start_services() {
    log_info "啟動服務..."
    
    cd "${PROJECT_ROOT}"
    
    # 啟動依賴服務
    if [[ "${ENVIRONMENT}" == "production" ]]; then
        # 生產環境分階段啟動
        log_info "啟動基礎設施服務..."
        if command -v docker-compose &> /dev/null; then
            docker-compose -f "${COMPOSE_FILE}" up -d redis-master redis-sentinel prometheus
        else
            docker compose -f "${COMPOSE_FILE}" up -d redis-master redis-sentinel prometheus
        fi
        
        # 等待基礎服務就緒
        sleep 10
        
        log_info "啟動應用服務..."
        if command -v docker-compose &> /dev/null; then
            docker-compose -f "${COMPOSE_FILE}" up -d
        else
            docker compose -f "${COMPOSE_FILE}" up -d
        fi
    else
        # 開發環境直接啟動
        if command -v docker-compose &> /dev/null; then
            docker-compose -f "${COMPOSE_FILE}" up -d
        else
            docker compose -f "${COMPOSE_FILE}" up -d
        fi
    fi
    
    log_info "服務啟動完成"
}

# 停止服務
stop_services() {
    log_info "停止服務..."
    
    cd "${PROJECT_ROOT}"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "${COMPOSE_FILE}" down
    else
        docker compose -f "${COMPOSE_FILE}" down
    fi
    
    log_info "服務停止完成"
}

# 重啟服務
restart_services() {
    log_info "重啟服務..."
    
    stop_services
    sleep 5
    start_services
    
    log_info "服務重啟完成"
}

# 健康檢查
health_check() {
    log_info "執行健康檢查..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ ${attempt} -le ${max_attempts} ]]; do
        log_info "健康檢查嘗試 ${attempt}/${max_attempts}"
        
        # 檢查主應用
        if curl -f -s "http://localhost:8000/health" > /dev/null 2>&1; then
            log_info "主應用健康檢查通過"
            
            # 檢查其他服務
            local all_healthy=true
            
            # Redis
            if ! docker exec oran-rag-redis-${ENVIRONMENT} redis-cli ping > /dev/null 2>&1; then
                log_warn "Redis 健康檢查失敗"
                all_healthy=false
            fi
            
            if [[ "${all_healthy}" == "true" ]]; then
                log_info "所有服務健康檢查通過"
                return 0
            fi
        fi
        
        sleep 10
        attempt=$((attempt + 1))
    done
    
    log_error "健康檢查失敗"
    return 1
}

# 顯示狀態
show_status() {
    log_info "顯示服務狀態..."
    
    cd "${PROJECT_ROOT}"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "${COMPOSE_FILE}" ps
    else
        docker compose -f "${COMPOSE_FILE}" ps
    fi
    
    echo ""
    log_info "服務日誌 (最近10行):"
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "${COMPOSE_FILE}" logs --tail=10
    else
        docker compose -f "${COMPOSE_FILE}" logs --tail=10
    fi
}

# 查看日誌
view_logs() {
    local service="${3:-}"
    
    cd "${PROJECT_ROOT}"
    
    if [[ -n "${service}" ]]; then
        log_info "查看 ${service} 服務日誌..."
        if command -v docker-compose &> /dev/null; then
            docker-compose -f "${COMPOSE_FILE}" logs -f "${service}"
        else
            docker compose -f "${COMPOSE_FILE}" logs -f "${service}"
        fi
    else
        log_info "查看所有服務日誌..."
        if command -v docker-compose &> /dev/null; then
            docker-compose -f "${COMPOSE_FILE}" logs -f
        else
            docker compose -f "${COMPOSE_FILE}" logs -f
        fi
    fi
}

# 初始化資料庫
init_database() {
    log_info "初始化向量資料庫..."
    
    cd "${PROJECT_ROOT}"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose -f "${COMPOSE_FILE}" exec oran-rag-app /entrypoint.sh init-db
    else
        docker compose -f "${COMPOSE_FILE}" exec oran-rag-app /entrypoint.sh init-db
    fi
    
    log_info "資料庫初始化完成"
}

# 備份
backup() {
    log_info "執行系統備份..."
    
    local backup_dir="${DATA_PATH}/backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "${backup_dir}"
    
    # 備份向量資料庫
    if [[ -d "${DATA_PATH}/vectordb" ]]; then
        log_info "備份向量資料庫..."
        cp -r "${DATA_PATH}/vectordb" "${backup_dir}/"
    fi
    
    # 備份配置
    log_info "備份配置文件..."
    cp "${ENV_FILE}" "${backup_dir}/config.env"
    
    # 壓縮備份
    log_info "壓縮備份文件..."
    tar -czf "${backup_dir}.tar.gz" -C "$(dirname "${backup_dir}")" "$(basename "${backup_dir}")"
    rm -rf "${backup_dir}"
    
    log_info "備份完成: ${backup_dir}.tar.gz"
}

# 顯示幫助
show_help() {
    cat << EOF
O-RAN × Nephio RAG 系統部署腳本

使用方法:
    $0 <environment> <action> [version]

參數:
    environment: development | production
    action:      deploy | stop | restart | status | logs | health | init-db | backup | build | pull
    version:     映像版本標籤 (預設: latest)

範例:
    $0 development deploy        # 部署開發環境
    $0 production deploy v1.0.0  # 部署生產環境指定版本
    $0 development stop          # 停止開發環境
    $0 production status         # 查看生產環境狀態
    $0 development logs app      # 查看開發環境應用日誌
    $0 production health         # 檢查生產環境健康狀態
    $0 development init-db       # 初始化開發環境資料庫
    $0 production backup         # 備份生產環境資料

環境:
    development: 開發環境，包含所有開發工具
    production:  生產環境，高性能和安全性配置

動作:
    deploy:   完整部署 (建構映像 + 啟動服務 + 健康檢查)
    stop:     停止所有服務
    restart:  重啟所有服務
    status:   顯示服務狀態
    logs:     查看服務日誌
    health:   執行健康檢查
    init-db:  初始化向量資料庫
    backup:   備份系統資料
    build:    只建構映像
    pull:     只拉取映像

EOF
}

# 主函數
main() {
    # 檢查參數
    if [[ $# -lt 2 ]]; then
        show_help
        exit 1
    fi
    
    # 驗證環境參數
    if [[ "${ENVIRONMENT}" != "development" && "${ENVIRONMENT}" != "production" ]]; then
        log_error "無效的環境: ${ENVIRONMENT}"
        show_help
        exit 1
    fi
    
    log_info "=========================================="
    log_info "O-RAN × Nephio RAG 系統部署"
    log_info "環境: ${ENVIRONMENT}"
    log_info "動作: ${ACTION}"
    log_info "版本: ${VERSION}"
    log_info "=========================================="
    
    # 執行前置檢查
    check_environment
    load_environment
    check_required_variables
    
    # 根據動作執行相應操作
    case "${ACTION}" in
        "deploy")
            prepare_data_directories
            build_images
            pull_images
            start_services
            health_check
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            health_check
            ;;
        "status")
            show_status
            ;;
        "logs")
            view_logs
            ;;
        "health")
            health_check
            ;;
        "init-db")
            init_database
            ;;
        "backup")
            backup
            ;;
        "build")
            build_images
            ;;
        "pull")
            pull_images
            ;;
        *)
            log_error "無效的動作: ${ACTION}"
            show_help
            exit 1
            ;;
    esac
    
    log_info "操作完成"
}

# 執行主函數
main "$@"