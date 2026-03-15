FROM python:3.12-slim

# تثبيت الأدوات الأساسية فقط
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# تحديث pip قبل كل شيء
RUN pip install --upgrade pip

COPY requirements.txt .

# تثبيت المكتبات مع السماح بالنسخ التجريبية لـ pandas-ta
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# تأكد أن اسم الملف هو نفس اسم ملف الكود الخاص بك
CMD ["python", "crypto_bot_final.py.py"]

