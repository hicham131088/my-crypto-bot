# استخدام نسخة بايثون 3.11 الرسمية والمستقرة
FROM python:3.11-slim

# تحديث النظام وتثبيت أدوات البناء الأساسية لحل مشكلة مكتبة pandas وغيرها
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# تحديد مسار العمل داخل السيرفر
WORKDIR /app

# نسخ ملف المتطلبات أولاً لتسريع عملية البناء مستقبلاً
COPY requirements.txt .

# تحديث pip وتثبيت المكتبات
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات البوت
COPY . .

# أمر تشغيل البوت 
# (مهم: إذا كان اسم ملفك الأساسي ليس main.py، قم بتغييره هنا)
CMD ["python", "main.py"]
