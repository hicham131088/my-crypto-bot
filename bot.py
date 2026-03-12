import os, time, requests, pandas as pd, pandas_ta as ta
from datetime import datetime

TOKEN = '7900130533:AAFP7ZYnrdUOEf-8E1rQIKWdgRfD8oJZSuw'
CHAT_ID = '6424409099'

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}, timeout=10)
    except: pass

def get_data(symbol):
    # استخدام روابط متعددة لضمان جلب البيانات
    urls = [
        f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=30m&limit=100",
        f"https://api1.binance.com/api/v3/klines?symbol={symbol}&interval=30m&limit=100",
        f"https://api2.binance.com/api/v3/klines?symbol={symbol}&interval=30m&limit=100"
    ]
    for url in urls:
        try:
            res = requests.get(url, timeout=10).json()
            if isinstance(res, list) and len(res) > 0:
                df = pd.DataFrame(res, columns=['t','o','h','l','c','v','ct','q','tr','tb','tq','i'])
                df[['h','l','c']] = df[['h','l','c']].astype(float)
                return df
        except: continue
    return pd.DataFrame()

def run_radar():
    print(f"🚀 [1/4] بدء دورة التحليل الشاملة: {datetime.now().strftime('%H:%M')}")
    try:
        # مرحلة 1: تحليل البيتكوين
        print("⏳ [2/4] جاري تحليل اتجاه البيتكوين... (25%)")
        btc = get_data('BTCUSDT')
        if btc.empty: 
            print("❌ فشل جلب بيانات البيتكوين بعد محاولة كافة الروابط.")
            return
            
        btc_change = ((btc['c'].iloc[-1] - btc['c'].iloc[-2]) / btc['c'].iloc[-2]) * 100
        status = "🟢 صاعد" if btc_change >= 0 else "🔴 هابط"
        print(f"📊 نتيجة البيتكوين: {status} ({btc_change:.2f}%)")

        if btc_change < 0:
            print(f"🛑 البيتكوين نازل بقوة ({btc_change:.2f}%). إنهاء التحليل فوراً للحماية.")
            return

        # مرحلة 2: تحليل السيولة
        print("⏳ [3/4] جاري فحص سيولة السوق... (50%)")
        try:
            r = requests.get("https://api.binance.com/api/v3/ticker/24hr").json()
            valid = [i['symbol'] for i in r if i['symbol'].endswith('USDT') and float(i['quoteVolume']) > 20000000]
            print(f"✅ تحليل السيولة: تم إيجاد {len(valid)} عملة تحقق الشرط (>20M$)")
        except:
            print("❌ فشل جلب بيانات السيولة.")
            return

        # مرحلة 3: تحليل الإشارات الفنية
        print(f"⏳ [4/4] جاري فحص الإشارات الفنية لـ {len(valid)} عملة... (75%)")
        found_signals = 0
        for s in valid:
            df = get_data(s)
            if not df.empty and len(df) >= 50:
                m = df.ta.macd(close='c')
                ic = df.ta.ichimoku(high='h', low='l', close='c')[0]
                cp = df['c'].iloc[-1]
                # استراتيجية MACD + Ichimoku
                if m.iloc[-1][0] > m.iloc[-1][2] and cp > ic['ISA_9'].iloc[-1] and cp > ic['ISB_26'].iloc[-1]:
                    send_msg(f"🚀 **دخول: {s}**\n💰 السعر: {cp}\n📊 BTC: {btc_change:.2f}%")
                    print(f"📡 إشارة فنية مؤكدة: {s}")
                    found_signals += 1
        
        print(f"🏁 انتهى التحليل. الإشارات المرسلة: {found_signals} (100%)")
        print("--------------------------------------------------")

    except Exception as e:
        print(f"⚠️ حدث خطأ غير متوقع: {e}")

send_msg("🤖 رادار Railway المطور بدأ العمل (نظام التقارير الحية)")
last_pulse = -1

while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        
        if now.minute in [0, 30]:
            run_radar()
            
    time.sleep(1)
