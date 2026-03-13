# 🚀 بوت التحليل الفني للعملات الرقمية

## ✅ ما تم تصحيحه:
1. ✨ إزالة تحذيرات `Pandas4Warning` عن `'d'` vs `'D'`
2. 🔧 تحديث طريقة استدعاء `.ewm()` لـ EMA
3. 📊 تحسين معالجة الأخطاء
4. 🛡️ إضافة `warnings.filterwarnings('ignore')`

## 📦 الملفات المطلوبة:
```
├── bot.py                 (البوت الرئيسي)
├── requirements.txt       (المكتبات)
├── Procfile              (تعليمات Railway)
└── runtime.txt           (إصدار Python)
```

## 🔑 خطوات النشر على Railway:

### 1️⃣ إعداد Repository:
```bash
# انسخ الملفات الأربعة إلى مجلد المشروع
git add .
git commit -m "تحديث البوت - حل تحذيرات pandas"
git push origin main
```

### 2️⃣ على Railway:
1. اذهب إلى https://railway.app/
2. اختر **"Deploy from GitHub"**
3. اختر Repository الخاص بك
4. Railway سيكتشف تلقائياً `Procfile` و `requirements.txt`

### 3️⃣ المتغيرات البيئية (اختياري):
إذا أردت حماية التوكن:
```
TOKEN=7900130533:AAFP7ZYnrdUOEf-8E1rQIKWdgRfD8oJZSuw
CHAT_ID=6424409099
```

ثم عدّل في bot.py:
```python
import os
TOKEN = os.getenv('TOKEN', '...')
CHAT_ID = os.getenv('CHAT_ID', '...')
```

## 📊 الميزات:
- ✅ فحص 40 عملة رقمية
- 📈 مؤشرات فنية: MACD + Ichimoku
- 🔊 إرسال إشارات عبر Telegram
- 🕒 مسح كل 30 دقيقة (في أوقات الذروة)
- 🛡️ معالجة أخطاء قوية

## ⚠️ ملاحظات مهمة:
- **تأكد أن Telegram Bot Token صحيح**
- **تحقق من CHAT_ID (يجب أن يكون رقمك الشخصي أو Group ID)**
- **Railway يدعم free tier لكن السرعة محدودة**

## 🔍 اختبار محلي (اختياري):
```bash
pip install -r requirements.txt
python bot.py
```

---
**آخر تحديث:** مارس 2026 | Railway Deployment ✅
