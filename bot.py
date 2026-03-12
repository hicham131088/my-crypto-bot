import os, time, requests, pandas as pd, pandas_ta as ta, ccxt
from datetime import datetime

# --- الإعدادات والمفاتيح ---
TOKEN = '7900130533:AAFP7ZYnrdUOEf-8E1rQIKWdgRfD8oJZSuw'
CHAT_ID = '6424409099'
API_KEY = 'QSooAvoTOq2v4YYhG9J3rZa7Xk0AaHLY0xKZsYaTtdFC2LhPlSiRU5cGWGrxKL4X'

# إعداد مكتبة CCXT للاتصال الاحترافي
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'}
})

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}, timeout=15)
    except: pass

def get_data(symbol):
    try:
        # جلب البيانات عبر CCXT بدلاً من الطلبات العادية لتجاوز الحظر
        bars = exchange.fetch_ohlcv(symbol, timeframe='30m', limit=100)
        df = pd.DataFrame(bars, columns=['t', 'o', 'h', 'l', 'c', 'v'])
        df[['h', 'l', 'c']] = df[['h', 'l', 'c']].astype(float)
        return df
    except:
        return pd.DataFrame()

def run_radar():
    print(f"🚀 [1/4] {datetime.now().strftime('%H:%M')} | بدء دورة التحليل (CCXT Mode)")
    try:
        # 1. تحليل البيتكوين
        print("⏳ [2/4] (25%) | فحص البيتكوين عبر CCXT...")
        btc = get_data('BTC/USDT') # CCXT يستخدم الصيغة BTC/USDT
        if btc.empty:
            print("❌ لا تزال الشبكة محظورة. جاري محاولة تجاوز الجدار...")
            return
            
        btc_change = ((btc['c'].iloc[-1] - btc['c'].iloc[-2]) / btc['c'].iloc[-2]) * 100
        status = "🟢 صاعد" if btc_change >= 0 else "🔴 هابط"
        print(f"📊 نتيجة البيتكوين: {status} ({btc_change:.2f}%)")

        if btc_change < 0:
            print(f"🛑 حماية: البيتكوين هابط. إيقاف الدورة.")
            return

        # 2. تحليل السيولة
        print("⏳ [3/4] (50%) | جاري فحص السيولة...")
        tickers = exchange.fetch_tickers()
        valid = [s for s, t in tickers.items() if s.endswith('/USDT') and t['quoteVolume'] > 20000000]
        print(f"✅ تم العثور على {len(valid)} عملة نشطة.")

        # 3. التحليل الفني
        print(f"⏳ [4/4] (75%) | فحص المؤشرات الفنية...")
        found = 0
        for s in valid[:50]: # فحص أول 50 عملة سيولة لتجنب التأخير
            df = get_data(s)
            if not df.empty and len(df) >= 50:
                m = df.ta.macd(close='c')
                ic = df.ta.ichimoku(high='h', low='l', close='c')[0]
                cp = df['c'].iloc[-1]
                if m.iloc[-1][0] > m.iloc[-1][2] and cp > ic['ISA_9'].iloc[-1] and cp > ic['ISB_26'].iloc[-1]:
                    send_msg(f"🚀 **دخول: {s.replace('/', '')}**\n💰 السعر: {cp}\n📊 BTC: {btc_change:.2f}%")
                    print(f"📡 إشارة مؤكدة: {s}")
                    found += 1
        
        print(f"🏁 (100%) | اكتمل التحليل بنجاح. الإشارات: {found}")
    except Exception as e:
        print(f"⚠️ خطأ تقني: {e}")

send_msg("🤖 رادار Railway المطور (نسخة CCXT) بدأ العمل الآن")
last_pulse = -1

while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)
