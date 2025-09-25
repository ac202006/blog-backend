# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# 系统依赖（图片处理需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 先安装依赖，尽量利用缓存
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 拷贝项目源码
COPY . /app

EXPOSE 8000

# 直接运行 Flask 应用（开发版调试 False；如需生产见 README）
CMD ["python", "app.py"]
