import os, time, requests, pandas as pd, pandas_ta as ta
from datetime import datetime

# --- الإعدادات ---
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
    print(f"🚀 دورة التحليل بدأت: {datetime.now().strftime('%H:%M')}")
    try:
        # 1. فلتر البيتكوين (صاعد فقط)
        btc = get_data('BTCUSDT')
        if btc.empty: return
        btc_change = ((btc['c'].iloc[-1] - btc['c'].iloc[-2]) / btc['c'].iloc[-2]) * 100
        if btc_change < 0:
            print(f"⚠️ BTC هابط ({btc_change:.2f}%) - تم تخطي الفحص")
            return

        # 2. فلتر السيولة (> 20 مليون)
        r = requests.get("https://api2.binance.com/api/v3/ticker/24hr").json()
        valid = [i['symbol'] for i in r if i['symbol'].endswith('USDT') and float(i['quoteVolume']) > 20000000]
        
        for s in valid:
            df = get_data(s)
            if not df.empty and len(df) >= 50:
                # 3. فلتر MACD + Ichimoku
                m = df.ta.macd(close='c')
                ic = df.ta.ichimoku(high='h', low='l', close='c')[0]
                cp = df['c'].iloc[-1]
                if m.iloc[-1][0] > m.iloc[-1][2] and cp > ic['ISA_9'].iloc[-1] and cp > ic['ISB_26'].iloc[-1]:
                    send_msg(f"🚀 **إشارة دخول: {s}**\n💰 السعر: {cp}\n📊 BTC: {btc_change:.2f}%")
    except: pass

send_msg("🤖 رادار Railway يعمل الآن (النبض كل 5 دقائق)")

last_pulse = -1

while True:
    now = datetime.now()
    
    # تحديث النبض ليكون كل 5 دقائق (0, 5, 10, 15...)
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر (كل 5د): {now.strftime('%H:%M')}")
        last_pulse = now.minute
        
        # تنفيذ التحليل عند الدقيقة 00 و 30 فقط
        if now.minute in [0, 30]:
            run_radar()
            
    time.sleep(1)
    
