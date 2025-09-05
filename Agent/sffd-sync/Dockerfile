FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 先安裝 cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# 複製同步程式 & crontab 設定
COPY sffd_sync.py .
COPY crontab /etc/cron.d/sffd-cron

# 設定權限，讓 cron 能讀取
RUN chmod 0644 /etc/cron.d/sffd-cron

# 啟用 crontab
RUN crontab /etc/cron.d/sffd-cron

# 前景執行 cron
CMD ["cron", "-f"]
