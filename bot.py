import time, requests, pandas as pd, pandas_ta as ta, yfinance as yf
from datetime import datetime

# --- الإعدادات الأساسية ---
TOKEN = '7900130533:AAFP7ZYnrdUOEf-8E1rQIKWdgRfD8oJZSuw'
CHAT_ID = '6424409099'

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}, timeout=15)
    except: pass

def get_data(symbol):
    try:
        yf_symbol = symbol.replace('USDT', '-USD')
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period="5d", interval="30m")
        if not df.empty:
            # لم نعد نغير أسماء الأعمدة يدوياً لتوافق المكتبة الفنية
            return df
    except: pass
    return pd.DataFrame()

def get_full_market_list():
    return [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT', 'AVAXUSDT', 'DOTUSDT',
        'DOGEUSDT', 'LINKUSDT', 'SHIBUSDT', 'MATICUSDT', 'LTCUSDT', 'UNIUSDT', 'NEARUSDT', 'APTUSDT',
        'OPUSDT', 'ARBUSDT', 'SUIUSDT', 'FETUSDT', 'RNDRUSDT', 'PEPEUSDT', 'FLOKIUSDT', 'INJUSDT',
        'TIAUSDT', 'STXUSDT', 'FILUSDT', 'LDOUSDT', 'ORDIUSDT', 'ICPUSDT', 'TRXUSDT', 'ETCUSDT', 
        'BCHUSDT', 'AAVEUSDT', 'ALGOUSDT', 'EGLDUSDT', 'SANDUSDT', 'MANAUSDT', 'ATOMUSDT', 'VETUSDT'
    ]

def run_radar():
    print(f"🚀 [1/4] {datetime.now().strftime('%H:%M')} | بدء المسح")
    try:
        btc = get_data('BTCUSDT')
        if btc.empty or len(btc) < 50: 
            print("❌ نقص في بيانات البيتكوين.")
            return
        
        # حساب EMA 50 للبيتكوين
        ema50 = btc.ta.ema(length=50)
        current_btc = btc['Close'].iloc[-1]
        last_ema50 = ema50.iloc[-1]
        
        # شرط الزخم الصاعد (EMA 50)
        if current_btc > last_ema50:
            print(f"✅ زخم صاعد (BTC: {current_btc:.0f} > EMA: {last_ema50:.0f})")
        else:
            print(f"🛑 زخم هابط (BTC: {current_btc:.0f} < EMA: {last_ema50:.0f}).")
            return

        all_symbols = get_full_market_list()
        found = 0
        for s in all_symbols:
            df = get_data(s)
            if not df.empty and len(df) >= 50:
                df = df.dropna()
                # فلتر السيولة (200 ألف دولار)
                volume_usd = df['Volume'].iloc[-1] * df['Close'].iloc[-1]
                if volume_usd < 200000: continue
                
                try:
                    # التحليل الفني (بدون تغيير المنطق)
                    m = df.ta.macd()
                    ic = df.ta.ichimoku()[0]
                    cp = df['Close'].iloc[-1]
                    
                    # التقاطع الإيجابي + فوق السحابة
                    if m.iloc[-1][0] > m.iloc[-1][2] and cp > ic['ISA_9'].iloc[-1] and cp > ic['ISB_26'].iloc[-1]:
                        send_msg(f"🚀 **إشارة دخول: {s}**\n💰 السعر: {cp:.4f}\n📈 وضع السوق: صاعد (EMA 50)")
                        found += 1
                except: continue
            time.sleep(0.1)
        print(f"🏁 اكتمل. الإشارات: {found}")
    except Exception as e:
        print(f"⚠️ خطأ عام: {e}")

send_msg("📡 تحديث: تم تصحيح أخطاء البيانات وتفعيل فلتر EMA 50 للبيتكوين.")

last_pulse = -1
while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)
