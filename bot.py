import os, time, requests, pandas as pd, pandas_ta as ta
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# --- كود وهمي لإرضاء Render ومنع إغلاق البوت ---
def run_dummy_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is Running")
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), Handler)
    server.serve_forever()

# تشغيل السيرفر الوهمي في خلفية البوت
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- إعدادات البوت الأصلية ---
TOKEN = '7900130533:AAFP7ZYnrdUOEf-8E1rQIKWdgRfD8oJZSuw'
CHAT_ID = '6424409099'

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}, timeout=10)
    except: pass

def get_data(symbol):
    try:
        url = f"https://api1.binance.com/api/v3/klines?symbol={symbol}&interval=30m&limit=100"
        res = requests.get(url, timeout=15).json()
        df = pd.DataFrame(res, columns=['t','o','h','l','c','v','ct','q','tr','tb','tq','i'])
        for col in ['h','l','c']: df[col] = df[col].astype(float)
        return df
    except: return pd.DataFrame()

def run_radar():
    print(f"\n🚀 [بدء دورة التحليل: {datetime.now().strftime('%H:%M:%S')}]")
    try:
        r = requests.get("https://api1.binance.com/api/v3/ticker/24hr", timeout=15).json()
        valid_coins = [i['symbol'] for i in r if i['symbol'].endswith('USDT') and float(i['quoteVolume']) > 20000000]
        print(f"✅ وجدنا {len(valid_coins)} عملة قوية.")
        send_msg(f"🔎 بدأ فحص {len(valid_coins)} عملة...")

        signals = 0
        for i, sym in enumerate(valid_coins):
            df = get_data(sym)
            if not df.empty and len(df) >= 50:
                macd = df.ta.macd(close='c')
                ich = df.ta.ichimoku(high='h', low='l', close='c')[0]
                cp = df['c'].iloc[-1]
                
                if macd.iloc[-1][0] > macd.iloc[-1][2] and cp > ich['ISA_9'].iloc[-1] and cp > ich['ISB_26'].iloc[-1]:
                    send_msg(f"🚀 **فرصة صيد: {sym}**\n🔔 السعر: {cp}")
                    signals += 1
            
            # التقدم المئوي
            if (i+1) % max(1, len(valid_coins)//10) == 0:
                print(f"📊 تقدم التحليل: {((i+1)/len(valid_coins))*100:.0f}%")

        if signals == 0: send_msg("📭 لا فرص حالياً.")
    except Exception as e: print(f"❌ خطأ: {e}")

# النبض والتشغيل
send_msg("🤖 رادار Render المجاني بدأ العمل!")
while True:
    now = datetime.now()
    if now.second == 0:
        print(f"🕒 نبض البوت: {now.strftime('%H:%M')}")
    if now.minute in [0, 30] and now.second == 0:
        run_radar()
        time.sleep(1)
    time.sleep(0.8)
