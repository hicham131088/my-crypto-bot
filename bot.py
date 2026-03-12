import time, requests, pandas as pd, pandas_ta as ta, yfinance as yf
from datetime import datetime

# --- الإعدادات ---
TOKEN = '7900130533:AAFP7ZYnrdUOEf-8E1rQIKWdgRfD8oJZSuw'
CHAT_ID = '6424409099'

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}, timeout=15)
    except: pass

def get_data(symbol):
    try:
        # تحويل اسم العملة ليتوافق مع Yahoo Finance (مثلاً BTC-USD)
        yf_symbol = symbol.replace('USDT', '-USD')
        # جلب البيانات (فريم 30 دقيقة)
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period="5d", interval="30m")
        
        if not df.empty:
            # إعادة تسمية الأعمدة لتناسب الكود السابق
            df = df.rename(columns={'Open':'o', 'High':'h', 'Low':'l', 'Close':'c', 'Volume':'v'})
            return df
    except Exception as e:
        print(f"⚠️ خطأ في جلب {symbol}: {e}")
    return pd.DataFrame()

def run_radar():
    print(f"🚀 [1/4] {datetime.now().strftime('%H:%M')} | بدء دورة التحليل (YFinance Mode)")
    try:
        # 1. تحليل البيتكوين
        btc = get_data('BTCUSDT')
        if btc.empty:
            print("❌ تعذر جلب بيانات السوق حالياً.")
            return
            
        btc_change = ((btc['c'].iloc[-1] - btc['c'].iloc[-2]) / btc['c'].iloc[-2]) * 100
        print(f"📊 اتجاه البيتكوين: {btc_change:.2f}%")

        if btc_change < 0:
            print("🛑 السوق هابط، تم إيقاف الفحص.")
            return

        # 2. قائمة العملات للمراقبة
        top_symbols = ['ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'AVAXUSDT', 'NEARUSDT', 'FETUSDT', 'SUIUSDT', 'PEPEUSDT']
        
        # 3. الفحص الفني
        found = 0
        for s in top_symbols:
            df = get_data(s)
            if not df.empty and len(df) >= 50:
                # حساب المؤشرات (MACD + Ichimoku)
                macd = df.ta.macd(close='c')
                ichi = df.ta.ichimoku(high='h', low='l', close='c')[0]
                cp = df['c'].iloc[-1]
                
                # شرط الدخول: السعر فوق السحابة + تقاطع MACD إيجابي
                if macd.iloc[-1][0] > macd.iloc[-1][2] and cp > ichi['ISA_9'].iloc[-1] and cp > ichi['ISB_26'].iloc[-1]:
                    send_msg(f"🚀 **إشارة دخول قوية: {s}**\n💰 السعر: {cp:.4f}\n📈 اتجاه BTC: {btc_change:.2f}%")
                    found += 1
            time.sleep(1) # لتجنب الضغط على السيرفر
        
        print(f"🏁 اكتمل التحليل. الإشارات المرسلة: {found}")
    except Exception as e:
        print(f"⚠️ خطأ عام: {e}")

# تنبيه البدء
send_msg("📡 البوت يعمل الآن بنظام YFinance المستقر 100%.")

last_pulse = -1
while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        last_pulse = now.minute
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)
