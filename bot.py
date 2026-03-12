import time, requests, pandas as pd, pandas_ta as ta
from datetime import datetime
from tvdatafeed import TvDatafeed, Interval

# --- الإعدادات ---
TOKEN = '7900130533:AAFP7ZYnrdUOEf-8E1rQIKWdgRfD8oJZSuw'
CHAT_ID = '6424409099'

# الاتصال بمحرك TradingView (بدون تسجيل دخول لضمان الاستقرار)
try:
    tv = TvDatafeed()
    print("✅ تم تشغيل محرك TradingView بنجاح")
except Exception as e:
    print(f"❌ فشل تشغيل المحرك: {e}")

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}, timeout=15)
    except: pass

def get_data(symbol):
    try:
        # جلب البيانات من TradingView (حل مشكلة حظر IP بينا نص)
        df = tv.get_hist(symbol=symbol, exchange='BINANCE', interval=Interval.in_30_minute, n_bars=100)
        if df is not None and not df.empty:
            df = df.rename(columns={'open':'o', 'high':'h', 'low':'l', 'close':'c', 'volume':'v'})
            return df
    except: pass
    return pd.DataFrame()

def run_radar():
    print(f"🚀 [1/4] {datetime.now().strftime('%H:%M')} | بدء دورة التحليل عبر TradingView")
    try:
        # 1. فحص البيتكوين
        btc = get_data('BTCUSDT')
        if btc.empty:
            print("❌ لا توجد بيانات. ربما هناك مشكلة في اتصال السيرفر بـ TradingView.")
            return
            
        btc_change = ((btc['c'].iloc[-1] - btc['c'].iloc[-2]) / btc['c'].iloc[-2]) * 100
        print(f"📊 اتجاه البيتكوين: {btc_change:.2f}%")

        if btc_change < 0:
            print("🛑 السوق هابط. سأنتظر الدورة القادمة.")
            return

        # 2. قائمة العملات المختارة (أقوى العملات حالياً)
        symbols = ['ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'AVAXUSDT', 'NEARUSDT', 'FETUSDT', 'SUIUSDT', 'PEPEUSDT']
        
        # 3. الفحص الفني
        found = 0
        for s in symbols:
            df = get_data(s)
            if not df.empty and len(df) >= 50:
                m = df.ta.macd(close='c')
                ic = df.ta.ichimoku(high='h', low='l', close='c')[0]
                cp = df['c'].iloc[-1]
                
                # استراتيجية التقاطع (MACD + Ichimoku)
                if m.iloc[-1][0] > m.iloc[-1][2] and cp > ic['ISA_9'].iloc[-1] and cp > ic['ISB_26'].iloc[-1]:
                    send_msg(f"🚀 **إشارة TradingView: {s}**\n💰 السعر: {cp}\n📈 اتجاه BTC: {btc_change:.2f}%")
                    found += 1
            time.sleep(1) # لضمان عدم حظر الطلبات
        
        print(f"🏁 اكتمل التحليل. الإشارات: {found}")
    except Exception as e:
        print(f"⚠️ خطأ أثناء التشغيل: {e}")

# التنبيه ببدء التشغيل
send_msg("📡 البوت يعمل الآن باستخدام بيانات TradingView لتجاوز الحظر.")

last_pulse = -1
while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        last_pulse = now.minute
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)
