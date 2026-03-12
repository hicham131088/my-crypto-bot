import time, requests, pandas as pd, pandas_ta as ta
from datetime import datetime
from tvDatafeed import TvDatafeed, Interval

# --- الإعدادات الأساسية ---
TOKEN = '7900130533:AAFP7ZYnrdUOEf-8E1rQIKWdgRfD8oJZSuw'
CHAT_ID = '6424409099'

# الاتصال بمحرك TradingView
tv = TvDatafeed()

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}, timeout=15)
    except: pass

def get_data(symbol):
    try:
        # جلب البيانات من TradingView لتجاوز حظر Binance
        df = tv.get_hist(symbol=symbol, exchange='BINANCE', interval=Interval.in_30_minute, n_bars=100)
        if df is not None and not df.empty:
            # إعادة تسمية الأعمدة لتتوافق مع الكود
            df = df.rename(columns={'open':'o', 'high':'h', 'low':'l', 'close':'c', 'volume':'v'})
            return df
    except Exception as e:
        print(f"❌ خطأ في جلب {symbol}: {e}")
    return pd.DataFrame()

def run_radar():
    print(f"🚀 [1/4] {datetime.now().strftime('%H:%M')} | بدء دورة التحليل (Stable TV Mode)")
    try:
        # 1. تحليل البيتكوين
        print("⏳ [2/4] (25%) | فحص البيتكوين...")
        btc = get_data('BTCUSDT')
        if btc.empty:
            print("❌ لا تزال هناك مشكلة في جلب بيانات TradingView.")
            return
            
        btc_change = ((btc['c'].iloc[-1] - btc['c'].iloc[-2]) / btc['c'].iloc[-2]) * 100
        status = "🟢 صاعد" if btc_change >= 0 else "🔴 هابط"
        print(f"📊 نتيجة البيتكوين: {status} ({btc_change:.2f}%)")

        if btc_change < 0:
            print(f"🛑 الاتجاه سلبي. تم إيقاف الدورة.")
            return

        # 2. قائمة العملات (أقوى 15 عملة سيولة)
        print("⏳ [3/4] (50%) | فحص قائمة العملات القوية...")
        top_symbols = [
            'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 
            'AVAXUSDT', 'DOTUSDT', 'LINKUSDT', 'NEARUSDT', 'LTCUSDT',
            'FETUSDT', 'PEPEUSDT', 'DOGEUSDT', 'SUIUSDT', 'APTUSDT'
        ]
        
        # 3. التحليل الفني
        print(f"⏳ [4/4] (75%) | فحص المؤشرات لـ {len(top_symbols)} عملة...")
        found = 0
        for s in top_symbols:
            df = get_data(s)
            if not df.empty and len(df) >= 50:
                # حساب MACD
                m = df.ta.macd(close='c')
                # حساب Ichimoku
                ic = df.ta.ichimoku(high='h', low='l', close='c')[0]
                cp = df['c'].iloc[-1]
                
                # استراتيجية التقاطع فوق السحابة
                if m.iloc[-1][0] > m.iloc[-1][2] and cp > ic['ISA_9'].iloc[-1] and cp > ic['ISB_26'].iloc[-1]:
                    send_msg(f"🚀 **إشارة دخول (TV): {s}**\n💰 السعر الحالي: {cp}\n📊 اتجاه BTC: {btc_change:.2f}%")
                    print(f"📡 إشارة مؤكدة لعملة: {s}")
                    found += 1
            time.sleep(1.5) # مهلة بسيطة لضمان جلب البيانات دون خطأ
        
        print(f"🏁 (100%) | اكتمل التحليل بنجاح. الإشارات المرسلة: {found}")

    except Exception as e:
        print(f"⚠️ خطأ عام: {e}")

send_msg("🤖 رادار Railway (النسخة المستقرة - TradingView) بدأ العمل")
last_pulse = -1

while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)
