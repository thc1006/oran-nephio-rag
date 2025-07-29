#!/bin/bash
# O-RAN × Nephio RAG 系統清理腳本
# 用於清理Docker資源、日誌和臨時文件

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
ENVIRONMENT="${1:-all}"
CLEANUP_TYPE="${2:-containers}"
FORCE="${3:-false}"

# 確認操作
confirm_action() {
    local message="$1"
    
    if [[ "${FORCE}" == "true" ]]; then
        return 0
    fi
    
    echo -e "${YELLOW}警告: ${message}${NC}"
    read -p "是否繼續? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "操作已取消"
        exit 0
    fi
}

# 停止並移除容器
cleanup_containers() {
    local env_filter="$1"
    
    log_info "清理容器 (環境: ${env_filter})..."
    
    # 取得容器列表
    local containers
    if [[ "${env_filter}" == "all" ]]; then
        containers=$(docker ps -aq --filter "label=com.docker.compose.project=oran-rag-development" \
                                   --filter "label=com.docker.compose.project=oran-rag-production" 2>/dev/null || true)
    else
        containers=$(docker ps -aq --filter "label=com.docker.compose.project=oran-rag-${env_filter}" 2>/dev/null || true)
    fi
    
    if [[ -n "${containers}" ]]; then
        log_info "停止容器..."
        docker stop ${containers} 2>/dev/null || true
        
        log_info "移除容器..."
        docker rm ${containers} 2>/dev/null || true
        
        log_info "容器清理完成"
    else
        log_info "沒有找到相關容器"
    fi
}

# 清理映像
cleanup_images() {
    local env_filter="$1"
    
    log_info "清理映像 (環境: ${env_filter})..."
    
    # 清理未使用的映像
    local unused_images=$(docker images -f "dangling=true" -q 2>/dev/null || true)
    if [[ -n "${unused_images}" ]]; then
        log_info "清理懸掛映像..."
        docker rmi ${unused_images} 2>/dev/null || true
    fi
    
    # 清理專案相關映像
    local project_images
    if [[ "${env_filter}" == "all" ]]; then
        project_images=$(docker images --filter "reference=oran-rag*" -q 2>/dev/null || true)
    elif [[ "${env_filter}" == "development" ]]; then
        project_images=$(docker images --filter "reference=oran-rag:dev*" -q 2>/dev/null || true)
    elif [[ "${env_filter}" == "production" ]]; then
        project_images=$(docker images --filter "reference=oran-rag:production*" -q 2>/dev/null || true)
    fi
    
    if [[ -n "${project_images}" ]]; then
        confirm_action "這將刪除專案相關的 Docker 映像"
        log_info "清理專案映像..."
        docker rmi ${project_images} 2>/dev/null || true
    fi
    
    log_info "映像清理完成"
}

# 清理數據卷
cleanup_volumes() {
    local env_filter="$1"
    
    log_info "清理數據卷 (環境: ${env_filter})..."
    
    # 清理未使用的數據卷
    local unused_volumes=$(docker volume ls -f dangling=true -q 2>/dev/null || true)
    if [[ -n "${unused_volumes}" ]]; then
        log_info "清理未使用的數據卷..."
        docker volume rm ${unused_volumes} 2>/dev/null || true
    fi
    
    # 清理專案相關數據卷
    local project_volumes
    if [[ "${env_filter}" == "all" ]]; then
        project_volumes=$(docker volume ls --filter "name=oran-rag-" -q 2>/dev/null || true)
    else
        project_volumes=$(docker volume ls --filter "name=oran-rag-.*-${env_filter}" -q 2>/dev/null || true)
    fi
    
    if [[ -n "${project_volumes}" ]]; then
        confirm_action "這將刪除專案數據卷，包含所有數據"
        log_info "清理專案數據卷..."
        docker volume rm ${project_volumes} 2>/dev/null || true
    fi
    
    log_info "數據卷清理完成"
}

# 清理網路
cleanup_networks() {
    local env_filter="$1"
    
    log_info "清理網路 (環境: ${env_filter})..."
    
    # 清理未使用的網路
    local unused_networks=$(docker network ls --filter "driver=bridge" --filter "scope=local" -q 2>/dev/null | \
                           xargs docker network inspect --format '{{.Name}} {{.Containers}}' 2>/dev/null | \
                           awk '$2 == "map[]" {print $1}' || true)
    
    if [[ -n "${unused_networks}" ]]; then
        log_info "清理未使用的網路..."
        echo "${unused_networks}" | xargs -r docker network rm 2>/dev/null || true
    fi
    
    # 清理專案相關網路
    local project_networks
    if [[ "${env_filter}" == "all" ]]; then
        project_networks=$(docker network ls --filter "name=oran-rag-" -q 2>/dev/null || true)
    else
        project_networks=$(docker network ls --filter "name=oran-rag-.*-${env_filter}" -q 2>/dev/null || true)
    fi
    
    if [[ -n "${project_networks}" ]]; then
        log_info "清理專案網路..."
        docker network rm ${project_networks} 2>/dev/null || true
    fi
    
    log_info "網路清理完成"
}

# 清理日誌文件
cleanup_logs() {
    local env_filter="$1"
    local data_path="/data/oran-rag"
    
    log_info "清理日誌文件 (環境: ${env_filter})..."
    
    # 清理應用日誌
    if [[ -d "${data_path}/logs" ]]; then
        log_info "清理應用日誌..."
        find "${data_path}/logs" -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
        find "${data_path}/logs" -name "*.log.*" -type f -mtime +3 -delete 2>/dev/null || true
    fi
    
    # 清理 Docker 日誌
    log_info "清理 Docker 容器日誌..."
    local containers
    if [[ "${env_filter}" == "all" ]]; then
        containers=$(docker ps -aq 2>/dev/null || true)
    else
        containers=$(docker ps -aq --filter "label=com.docker.compose.project=oran-rag-${env_filter}" 2>/dev/null || true)
    fi
    
    if [[ -n "${containers}" ]]; then
        for container in ${containers}; do
            local log_file=$(docker inspect --format='{{.LogPath}}' "${container}" 2>/dev/null || true)
            if [[ -n "${log_file}" && -f "${log_file}" ]]; then
                log_debug "清理容器 ${container} 的日誌文件: ${log_file}"
                echo "" > "${log_file}" 2>/dev/null || true
            fi
        done
    fi
    
    log_info "日誌清理完成"
}

# 清理臨時文件
cleanup_temp_files() {
    log_info "清理臨時文件..."
    
    # 清理系統臨時文件
    local temp_dirs=("/tmp" "/var/tmp")
    for temp_dir in "${temp_dirs[@]}"; do
        if [[ -d "${temp_dir}" ]]; then
            find "${temp_dir}" -name "oran-rag-*" -type f -mtime +1 -delete 2>/dev/null || true
            find "${temp_dir}" -name "docker-*" -type d -empty -mtime +1 -delete 2>/dev/null || true
        fi
    done
    
    # 清理專案臨時文件
    if [[ -d "${PROJECT_ROOT}" ]]; then
        find "${PROJECT_ROOT}" -name "*.pyc" -delete 2>/dev/null || true
        find "${PROJECT_ROOT}" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        find "${PROJECT_ROOT}" -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
        find "${PROJECT_ROOT}" -name "*.tmp" -delete 2>/dev/null || true
    fi
    
    log_info "臨時文件清理完成"
}

# 系統清理 (謹慎使用)
system_cleanup() {
    confirm_action "這將執行系統級清理，可能影響其他 Docker 應用"
    
    log_info "執行系統級 Docker 清理..."
    
    # Docker 系統清理
    docker system prune -f --volumes 2>/dev/null || true
    
    # 清理建構快取
    docker builder prune -f 2>/dev/null || true
    
    log_info "系統清理完成"
}

# 清理備份文件
cleanup_backups() {
    local data_path="/data/oran-rag"
    local retention_days="${BACKUP_RETENTION_DAYS:-30}"
    
    log_info "清理舊備份文件 (保留 ${retention_days} 天)..."
    
    if [[ -d "${data_path}/backup" ]]; then
        find "${data_path}/backup" -name "*.tar.gz" -type f -mtime +${retention_days} -delete 2>/dev/null || true
        log_info "舊備份文件清理完成"
    else
        log_info "備份目錄不存在，跳過"
    fi
}

# 顯示磁碟使用情況
show_disk_usage() {
    log_info "Docker 磁碟使用情況:"
    docker system df 2>/dev/null || true
    
    echo ""
    log_info "數據目錄磁碟使用情況:"
    if [[ -d "/data/oran-rag" ]]; then
        du -sh /data/oran-rag/* 2>/dev/null || true
    else
        log_info "數據目錄不存在"
    fi
}

# 顯示幫助
show_help() {
    cat << EOF
O-RAN × Nephio RAG 系統清理腳本

使用方法:
    $0 <environment> <cleanup_type> [force]

參數:
    environment:   all | development | production
    cleanup_type:  containers | images | volumes | networks | logs | temp | backups | system | all
    force:         true | false (預設: false, 跳過確認提示)

清理類型:
    containers:  停止並移除容器
    images:      移除映像 (包含懸掛映像)
    volumes:     移除數據卷 (包含數據)
    networks:    移除網路
    logs:        清理日誌文件
    temp:        清理臨時文件
    backups:     清理舊備份文件
    system:      系統級清理 (謹慎使用)
    all:         執行所有清理操作

範例:
    $0 development containers         # 清理開發環境容器
    $0 production volumes            # 清理生產環境數據卷
    $0 all logs                      # 清理所有環境的日誌
    $0 development all true          # 強制清理開發環境的所有資源
    $0 all system true               # 強制執行系統級清理

注意事項:
    - 清理 volumes 會永久刪除數據，請先備份重要數據
    - system 清理會影響所有 Docker 應用，不僅限於本專案
    - 建議在清理前先停止相關服務

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
    if [[ "${ENVIRONMENT}" != "all" && "${ENVIRONMENT}" != "development" && "${ENVIRONMENT}" != "production" ]]; then
        log_error "無效的環境: ${ENVIRONMENT}"
        show_help
        exit 1
    fi
    
    # 驗證清理類型
    local valid_types=("containers" "images" "volumes" "networks" "logs" "temp" "backups" "system" "all")
    local type_valid=false
    for valid_type in "${valid_types[@]}"; do
        if [[ "${CLEANUP_TYPE}" == "${valid_type}" ]]; then
            type_valid=true
            break
        fi
    done
    
    if [[ "${type_valid}" == "false" ]]; then
        log_error "無效的清理類型: ${CLEANUP_TYPE}"
        show_help
        exit 1
    fi
    
    log_info "=========================================="
    log_info "O-RAN × Nephio RAG 系統清理"
    log_info "環境: ${ENVIRONMENT}"
    log_info "清理類型: ${CLEANUP_TYPE}"
    log_info "強制模式: ${FORCE}"
    log_info "=========================================="
    
    # 顯示清理前的磁碟使用情況
    show_disk_usage
    echo ""
    
    # 根據清理類型執行相應操作
    case "${CLEANUP_TYPE}" in
        "containers")
            cleanup_containers "${ENVIRONMENT}"
            ;;
        "images")
            cleanup_images "${ENVIRONMENT}"
            ;;
        "volumes")
            cleanup_volumes "${ENVIRONMENT}"
            ;;
        "networks")
            cleanup_networks "${ENVIRONMENT}"
            ;;
        "logs")
            cleanup_logs "${ENVIRONMENT}"
            ;;
        "temp")
            cleanup_temp_files
            ;;
        "backups")
            cleanup_backups
            ;;
        "system")
            system_cleanup
            ;;
        "all")
            cleanup_containers "${ENVIRONMENT}"
            cleanup_images "${ENVIRONMENT}"
            cleanup_networks "${ENVIRONMENT}"
            cleanup_logs "${ENVIRONMENT}"
            cleanup_temp_files
            cleanup_backups
            # 不包含 volumes 和 system，需要明確指定
            ;;
    esac
    
    echo ""
    log_info "清理完成"
    
    # 顯示清理後的磁碟使用情況
    show_disk_usage
}

# 執行主函數
main "$@"