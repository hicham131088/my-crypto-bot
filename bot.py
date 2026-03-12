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
    url = f"https://api2.binance.com/api/v3/klines?symbol={symbol}&interval=30m&limit=100"
    try:
        res = requests.get(url, timeout=10).json()
        if isinstance(res, list) and len(res) > 0:
            df = pd.DataFrame(res, columns=['t','o','h','l','c','v','ct','q','tr','tb','tq','i'])
            df[['h','l','c']] = df[['h','l','c']].astype(float)
            return df
    except: pass
    return pd.DataFrame()

def run_radar():
    print(f"🚀 [1/4] بدء دورة التحليل الشاملة: {datetime.now().strftime('%H:%M')}")
    try:
        # مرحلة 1: تحليل البيتكوين
        print("⏳ [2/4] جاري تحليل اتجاه البيتكوين... (25%)")
        btc = get_data('BTCUSDT')
        if btc.empty: 
            print("❌ فشل جلب بيانات البيتكوين.")
            return
            
        btc_change = ((btc['c'].iloc[-1] - btc['c'].iloc[-2]) / btc['c'].iloc[-2]) * 100
        status = "🟢 صاعد" if btc_change >= 0 else "🔴 هابط"
        print(f"📊 نتيجة البيتكوين: {status} ({btc_change:.2f}%)")

        if btc_change < 0:
            print(f"🛑 البيتكوين نازل بقوة. إنهاء التحليل فوراً للحماية.")
            return

        # مرحلة 2: تحليل السيولة
        print("⏳ [3/4] جاري فحص سيولة السوق... (50%)")
        r = requests.get("https://api2.binance.com/api/v3/ticker/24hr").json()
        valid = [i['symbol'] for i in r if i['symbol'].endswith('USDT') and float(i['quoteVolume']) > 20000000]
        print(f"✅ تم إيجاد {len(valid)} عملة تحقق شرط السيولة (>20M$)")

        # مرحلة 3: تحليل الإشارات الفنية
        print(f"⏳ [4/4] جاري فحص الإشارات الفنية لـ {len(valid)} عملة... (75%)")
        found_signals = 0
        for index, s in enumerate(valid):
            df = get_data(s)
            if not df.empty and len(df) >= 50:
                m = df.ta.macd(close='c')
                ic = df.ta.ichimoku(high='h', low='l', close='c')[0]
                cp = df['c'].iloc[-1]
                if m.iloc[-1][0] > m.iloc[-1][2] and cp > ic['ISA_9'].iloc[-1] and cp > ic['ISB_26'].iloc[-1]:
                    send_msg(f"🚀 **دخول: {s}**\n💰 السعر: {cp}\n📊 BTC: {btc_change:.2f}%")
                    print(f"📡 تم إرسال إشارة للعملة: {s}")
                    found_signals += 1
        
        print(f"🏁 تم الانتهاء من الفحص. العملات المكتشفة: {found_signals} (100%)")
        print("--------------------------------------------------")

    except Exception as e:
        print(f"⚠️ حدث خطأ أثناء التحليل: {e}")

send_msg("🤖 رادار Railway المطور بدأ العمل (نظام التقارير الحية)")
last_pulse = -1

while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        
        # لا يتم تحليل البيتكوين والسيولة إلا عند الدقيقة 00 و 30
        if now.minute in [0, 30]:
            run_radar()
            
    time.sleep(1)
