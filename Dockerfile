FROM python:3.11-slim

# System deps for engines (minimal; extend as needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg imagemagick poppler-utils libreoffice \
    tini curl ca-certificates file && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY . /app
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["/usr/bin/tini", "--"]
