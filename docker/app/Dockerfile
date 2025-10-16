# FastAPI-MCP Server with miniconda3
FROM continuumio/miniconda3

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# 環境のパスを追加
ENV PATH /opt/conda/envs/fastapi-mcp/bin:$PATH
# シェルの初期化時に環境を有効化
RUN echo "source activate fastapi-mcp" > ~/.bashrc

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create conda environment
RUN conda create -n fastapi-mcp python=3.11 -y \
    && conda clean -afy

# Activate environment in shell
RUN echo "source activate fastapi-mcp" > ~/.bashrc

# Create directories for FastAPI-MCP
RUN mkdir -p /usr/src/app/data \
    && mkdir -p /usr/src/app/logs

# Copy dependency files
COPY ./pyproject.toml ./uv.lock* /usr/src/app/

# install Python dependencies (including dev dependencies for testing)
RUN /bin/bash -c "source activate fastapi-mcp && \
    pip install --upgrade pip setuptools wheel && \
    pip install uv && \
    uv sync --frozen --all-extras"

# Ensure .venv/bin is in PATH for uvで作成された仮想環境
ENV PATH=/usr/src/app/.venv/bin:$PATH

# Test alembic installation
RUN /bin/bash -c "source activate fastapi-mcp && \
    source .venv/bin/activate && \
    which alembic && \
    alembic --version"

# Copy environment files
COPY ./.env.example /usr/src/app/
RUN if [ ! -f /usr/src/app/.env ]; then cp /usr/src/app/.env.example /usr/src/app/.env; fi

# Copy application source code
COPY ./app /usr/src/app/app
COPY ./docker /usr/src/app/docker

# Setup entrypoint script permissions
RUN chmod +x /usr/src/app/docker/app/entrypoint.sh

# 環境変数でモード切り替え（デフォルトはproduction）
ENV APP_ENV=production

# Expose ports
EXPOSE 8000

# 統一エントリーポイント（開発・プロダクション両対応）
CMD ["/usr/src/app/docker/app/entrypoint.sh"]
