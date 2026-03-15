 # استخدام نسخة بايثون الرسمية
FROM python:3.12-slim

# تثبيت كافة أدوات البناء والمكتبات النظامية المطلوبة
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    python3-dev \
    libffi-dev \
    libssl-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# تحديد مسار العمل
WORKDIR /app

# نسخ الملفات
COPY requirements.txt .

# تحديث pip وتثبيت المتطلبات بصبر (بدون مهلة زمنية)
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي الكود
COPY . .

# تشغيل البوت
CMD ["python", "crypto_bot_final.py"]
