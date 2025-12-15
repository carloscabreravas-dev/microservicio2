FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# 🔥 LIBRERÍAS DNS OBLIGATORIAS PARA K8s / OpenShift
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6 \
    libnss3 \
    ca-certificates \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "app.py"]
