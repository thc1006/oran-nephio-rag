# O-RAN × Nephio RAG 系統基礎 Dockerfile
# 支援開發和生產環境的多階段構建

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim as base

# 設定維護者資訊
LABEL maintainer="hctsai@linux.com"
LABEL description="O-RAN × Nephio RAG System - Intelligent Retrieval-Augmented Generation"
LABEL version="1.0.0"

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app \
    APP_HOME=/app \
    APP_USER=raguser \
    APP_GROUP=raguser

# 創建非root用戶
RUN groupadd -r ${APP_GROUP} && \
    useradd -r -g ${APP_GROUP} -d ${APP_HOME} -s /bin/bash ${APP_USER}

# 安裝系統依賴 (包含瀏覽器自動化支援)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libssl-dev \
    libffi-dev \
    gcc \
    g++ \
    make \
    pkg-config \
    wget \
    gnupg \
    unzip \
    xvfb \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 安裝 Chrome 瀏覽器 (for browser automation)
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 設定工作目錄
WORKDIR ${APP_HOME}

# 複製requirements文件 (使用constraint-compliant版本)
COPY requirements-fixed.txt ./requirements.txt

# 安裝Python依賴 (瀏覽器自動化版本)
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY . .

# 創建必要目錄 (瀏覽器自動化版本)
RUN mkdir -p logs \
    oran_nephio_vectordb \
    data \
    && chown -R ${APP_USER}:${APP_GROUP} ${APP_HOME}

# 設定瀏覽器環境變數
ENV DISPLAY=:99 \
    CHROME_BIN=/usr/bin/google-chrome \
    CHROME_PATH=/usr/bin/google-chrome

# 複製啟動腳本
COPY docker/scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 切換到非root用戶
USER ${APP_USER}

# 健康檢查 - 改為檢查基本系統狀態而非配置驗證
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import os, sys; sys.path.insert(0, '/app/src'); \
        exit(0 if os.path.exists('/app/logs') and os.path.exists('/app/src/config.py') else 1)" || exit 1

# 暴露埠
EXPOSE 8000

# 預設啟動命令
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "main.py"]

# =============================================================================
# 開發環境階段
# =============================================================================
FROM base as development

# 安裝開發工具
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    pytest-asyncio \
    black \
    flake8 \
    mypy \
    ipython \
    jupyter \
    notebook

# 開發環境設定
ENV FLASK_ENV=development \
    LOG_LEVEL=DEBUG \
    AUTO_RELOAD=true

# 暴露Jupyter埠
EXPOSE 8888

# =============================================================================
# 生產環境階段  
# =============================================================================
FROM base as production

# 移除不必要的套件
RUN pip uninstall -y pip setuptools wheel

# 生產環境設定
ENV FLASK_ENV=production \
    LOG_LEVEL=INFO \
    AUTO_RELOAD=false

# 生產環境安全設定
RUN find ${APP_HOME} -name "*.pyc" -delete && \
    find ${APP_HOME} -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 最小化權限
USER ${APP_USER}

# 生產環境啟動命令
CMD ["python", "-O", "main.py"]