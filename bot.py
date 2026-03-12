import os, time, requests, pandas as pd, pandas_ta as ta
from datetime import datetime

# الإعدادات
TOKEN = '7900130533:AAFP7ZYnrdUOEf-8E1rQIKWdgRfD8oJZSuw'
CHAT_ID = '6424409099'

# إضافة "هوية متصفح" لإقناع سيرفرات Binance بأننا لسنا بوتات
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}, timeout=15)
    except: pass

def get_data(symbol):
    # استخدام قائمة متنوعة من السيرفرات العالمية لبينا نس
    urls = [
        f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=30m&limit=100",
        f"https://api1.binance.com/api/v3/klines?symbol={symbol}&interval=30m&limit=100",
        f"https://api2.binance.com/api/v3/klines?symbol={symbol}&interval=30m&limit=100",
        f"https://api3.binance.com/api/v3/klines?symbol={symbol}&interval=30m&limit=100"
    ]
    for url in urls:
        for attempt in range(3): # زيادة عدد المحاولات لـ 3 لضمان الاستقرار
            try:
                # إضافة headers=HEADERS هي المفتاح هنا لتجنب الحظر
                res = requests.get(url, headers=HEADERS, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    if isinstance(data, list) and len(data) > 0:
                        df = pd.DataFrame(data, columns=['t','o','h','l','c','v','ct','q','tr','tb','tq','i'])
                        df[['h','l','c']] = df[['h','l','c']].astype(float)
                        return df
                elif res.status_code == 429: # في حال تم حظر الـ IP مؤقتاً
                    print(f"⚠️ تحذير: Binance تطلب إبطاء السرعة (Rate Limit).")
                    time.sleep(5) # انتظار 5 ثوانٍ قبل المحاولة التالية
            except:
                time.sleep(2)
                continue
    return pd.DataFrame()

def run_radar():
    now_time = datetime.now().strftime('%H:%M')
    print(f"🚀 [1/4] {now_time} | بدء دورة التحليل المضمونة")
    try:
        # 1. تحليل البيتكوين
        print("⏳ [2/4] (25%) | جاري جلب بيانات البيتكوين بأمان...")
        btc = get_data('BTCUSDT')
        if btc.empty: 
            print("❌ لا تزال هناك مشكلة في الاتصال بـ Binance. سأحاول مرة أخرى في النبض القادم.")
            return
            
        btc_change = ((btc['c'].iloc[-1] - btc['c'].iloc[-2]) / btc['c'].iloc[-2]) * 100
        status = "🟢 صاعد" if btc_change >= 0 else "🔴 هابط"
        print(f"📊 نتيجة البيتكوين: {status} ({btc_change:.2f}%)")

        if btc_change < 0:
            print(f"🛑 البيتكوين هابط. تم إيقاف التحليل لحمايتك.")
            return

        # 2. تحليل السيولة
        print("⏳ [3/4] (50%) | جاري فحص سيولة السوق...")
        try:
            r = requests.get("https://api.binance.com/api/v3/ticker/24hr", headers=HEADERS, timeout=15).json()
            valid = [i['symbol'] for i in r if i['symbol'].endswith('USDT') and float(i['quoteVolume']) > 20000000]
            print(f"✅ تم العثور على {len(valid)} عملة نشطة سيولتها > 20M$.")
        except:
            print("❌ فشل في جلب قائمة العملات.")
            return

        # 3. التحليل الفني
        print(f"⏳ [4/4] (75%) | فحص المؤشرات لـ {len(valid)} عملة...")
        found_signals = 0
        for s in valid:
            df = get_data(s)
            if not df.empty and len(df) >= 50:
                m = df.ta.macd(close='c')
                ic = df.ta.ichimoku(high='h', low='l', close='c')[0]
                cp = df['c'].iloc[-1]
                # استراتيجية MACD + Ichimoku
                if m.iloc[-1][0] > m.iloc[-1][2] and cp > ic['ISA_9'].iloc[-1] and cp > ic['ISB_26'].iloc[-1]:
                    send_msg(f"🚀 **دخول جديد: {s}**\n💰 السعر: {cp}\n📊 BTC: {btc_change:.2f}%")
                    print(f"📡 تم إرسال إشارة: {s}")
                    found_signals += 1
        
        print(f"🏁 (100%) | انتهى التحليل. إجمالي الإشارات: {found_signals}")
        print("--------------------------------------------------")

    except Exception as e:
        print(f"⚠️ خطأ غير متوقع: {e}")

send_msg("🤖 رادار Railway المطور (نسخة الاستقرار القصوى) يعمل الآن")
last_pulse = -1

while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)
