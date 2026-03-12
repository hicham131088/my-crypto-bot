import os, time, requests, pandas as pd, pandas_ta as ta
from datetime import datetime

# --- الإعدادات والمفاتيح ---
TOKEN = '7900130533:AAFP7ZYnrdUOEf-8E1rQIKWdgRfD8oJZSuw'
CHAT_ID = '6424409099'

# مفاتيح Binance الخاصة بك لضمان استقرار الاتصال
BINANCE_API_KEY = 'QSooAvoTOq2v4YYhG9J3rZa7Xk0AaHLY0xKZsYaTtdFC2LhPlSiRU5cGWGrxKL4X'

# نرسل المفتاح في كل طلب لإثبات الهوية للسيرفر
HEADERS = {
    'X-MBX-APIKEY': BINANCE_API_KEY,
    'User-Agent': 'Mozilla/5.0'
}

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}, timeout=15)
    except: pass

def get_data(symbol):
    # استخدام الرابط الرسمي مع المفاتيح
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=30m&limit=100"
    for attempt in range(3):
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code == 200:
                data = res.json()
                df = pd.DataFrame(data, columns=['t','o','h','l','c','v','ct','q','tr','tb','tq','i'])
                df[['h','l','c']] = df[['h','l','c']].astype(float)
                return df
            elif res.status_code == 429:
                time.sleep(10) # انتظار إذا طلب السيرفر ذلك
        except:
            time.sleep(2)
    return pd.DataFrame()

def run_radar():
    print(f"🚀 [1/4] {datetime.now().strftime('%H:%M')} | بدء دورة التحليل الاحترافية (API Mode)")
    try:
        # 1. تحليل البيتكوين
        print("⏳ [2/4] (25%) | فحص اتجاه البيتكوين...")
        btc = get_data('BTCUSDT')
        if btc.empty:
            print("❌ تعذر الاتصال بـ Binance حتى مع استخدام API Key.")
            return
            
        btc_change = ((btc['c'].iloc[-1] - btc['c'].iloc[-2]) / btc['c'].iloc[-2]) * 100
        status = "🟢 صاعد" if btc_change >= 0 else "🔴 هابط"
        print(f"📊 نتيجة البيتكوين: {status} ({btc_change:.2f}%)")

        if btc_change < 0:
            print(f"🛑 البيتكوين هابط. تم إنهاء الدورة لحماية المحفظة.")
            return

        # 2. تحليل السيولة
        print("⏳ [3/4] (50%) | فحص سيولة السوق (Volume > 20M)...")
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr", headers=HEADERS).json()
        valid = [i['symbol'] for i in r if i['symbol'].endswith('USDT') and float(i['quoteVolume']) > 20000000]
        print(f"✅ تم إيجاد {len(valid)} عملة مرشحة.")

        # 3. التحليل الفني
        print(f"⏳ [4/4] (75%) | فحص MACD و Ichimoku...")
        found = 0
        for s in valid:
            df = get_data(s)
            if not df.empty and len(df) >= 50:
                m = df.ta.macd(close='c')
                ic = df.ta.ichimoku(high='h', low='l', close='c')[0]
                cp = df['c'].iloc[-1]
                if m.iloc[-1][0] > m.iloc[-1][2] and cp > ic['ISA_9'].iloc[-1] and cp > ic['ISB_26'].iloc[-1]:
                    send_msg(f"🚀 **إشارة دخول: {s}**\n💰 السعر: {cp}\n📊 BTC: {btc_change:.2f}%")
                    print(f"📡 إشارة مؤكدة: {s}")
                    found += 1
        
        print(f"🏁 (100%) | اكتمل التحليل. الإشارات: {found}")
    except Exception as e:
        print(f"⚠️ خطأ: {e}")

send_msg("🤖 رادار Railway يعمل الآن بالمفاتيح الرسمية 🔑")
last_pulse = -1

while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)
