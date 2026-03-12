import os, time, requests, pandas as pd, pandas_ta as ta, ccxt
from datetime import datetime

# --- الإعدادات ---
TOKEN = '7900130533:AAFP7ZYnrdUOEf-8E1rQIKWdgRfD8oJZSuw'
CHAT_ID = '6424409099'
API_KEY = 'QSooAvoTOq2v4YYhG9J3rZa7Xk0AaHLY0xKZsYaTtdFC2LhPlSiRU5cGWGrxKL4X'

# إعداد المحرك للعمل على سوق العقود الآجلة (أحياناً يتجاوز حظر السبوت)
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'} 
})

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}, timeout=15)
    except: pass

def get_data(symbol):
    try:
        # محاولة جلب البيانات (استخدام صيغة BTC/USDT لـ CCXT)
        bars = exchange.fetch_ohlcv(symbol, timeframe='30m', limit=100)
        df = pd.DataFrame(bars, columns=['t', 'o', 'h', 'l', 'c', 'v'])
        df[['h', 'l', 'c']] = df[['h', 'l', 'c']].astype(float)
        return df
    except Exception as e:
        return pd.DataFrame()

def run_radar():
    print(f"🚀 [1/4] {datetime.now().strftime('%H:%M')} | بدء دورة التحليل (Ultimate Mode)")
    try:
        # 1. تحليل البيتكوين
        print("⏳ [2/4] (25%) | فحص البيتكوين عبر قنوات بديلة...")
        btc = get_data('BTC/USDT')
        
        if btc.empty:
            print("❌ لا يزال الجدار قائماً. سأحاول تغيير بروتوكول الاتصال في المرة القادمة.")
            return
            
        btc_change = ((btc['c'].iloc[-1] - btc['c'].iloc[-2]) / btc['c'].iloc[-2]) * 100
        status = "🟢 صاعد" if btc_change >= 0 else "🔴 هابط"
        print(f"📊 نتيجة البيتكوين: {status} ({btc_change:.2f}%)")

        if btc_change < 0:
            print(f"🛑 حماية: الاتجاه سلبي حالياً. تم إنهاء التحليل.")
            return

        # 2. تحليل السيولة
        print("⏳ [3/4] (50%) | فحص سيولة العملات...")
        tickers = exchange.fetch_tickers()
        # اختيار العملات التي تزيد سيولتها عن 20 مليون
        valid = [s for s, t in tickers.items() if s.endswith('/USDT') and t.get('quoteVolume', 0) > 20000000]
        print(f"✅ تم إيجاد {len(valid)} عملة نشطة.")

        # 3. التحليل الفني
        print(f"⏳ [4/4] (75%) | فحص الإشارات الفنية...")
        found = 0
        for s in valid[:40]: # فحص أهم 40 عملة لتوفير الوقت
            df = get_data(s)
            if not df.empty and len(df) >= 50:
                m = df.ta.macd(close='c')
                ic = df.ta.ichimoku(high='h', low='l', close='c')[0]
                cp = df['c'].iloc[-1]
                # استراتيجية التقاطع الإيجابي فوق السحابة
                if m.iloc[-1][0] > m.iloc[-1][2] and cp > ic['ISA_9'].iloc[-1] and cp > ic['ISB_26'].iloc[-1]:
                    send_msg(f"🚀 **إشارة دخول: {s.replace('/', '')}**\n💰 السعر: {cp}\n📊 BTC: {btc_change:.2f}%")
                    print(f"📡 تم إرسال إشارة: {s}")
                    found += 1
        
        print(f"🏁 (100%) | اكتمل التحليل. الإشارات المرسلة: {found}")
    except Exception as e:
        print(f"⚠️ خطأ مفاجئ: {e}")

send_msg("🤖 رادار Railway المطور (النسخة النهائية) بدأ العمل")
last_pulse = -1

while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)
