
import os, time, requests, pandas as pd, pandas_ta as ta
from datetime import datetime

TOKEN = '7900130533:AAFP7ZYnrdUOEf-8E1rQIKWdgRfD8oJZSuw'
CHAT_ID = '6424409099'

def send_msg(text):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}, timeout=10)
        except: pass

        def get_data(symbol):
            url = f"https://api1.binance.com/api/v3/klines?symbol={symbol}&interval=30m&limit=100"
                try:
                        res = requests.get(url, timeout=10).json()
                                if isinstance(res, list) and len(res) > 0: # هذا هو صمام الأمان
                                            df = pd.DataFrame(res, columns=['t','o','h','l','c','v','ct','q','tr','tb','tq','i'])
                                                        df[['h','l','c']] = df[['h','l','c']].astype(float)
                                                                    return df
                                                                        except: pass
                                                                            return pd.DataFrame()

                                                                            def run_radar():
                                                                                print(f"\n🚀 بدء دورة التحليل: {datetime.now().strftime('%H:%M:%S')}")
                                                                                    try:
                                                                                            r = requests.get("https://api1.binance.com/api/v3/ticker/24hr").json()
                                                                                                    valid_coins = [i['symbol'] for i in r if i['symbol'].endswith('USDT') and float(i['quoteVolume']) > 20000000]
                                                                                                            for sym in valid_coins:
                                                                                                                        df = get_data(sym)
                                                                                                                                    if not df.empty and len(df) >= 50:
                                                                                                                                                    macd = df.ta.macd(close='c')
                                                                                                                                                                    ich = df.ta.ichimoku(high='h', low='l', close='c')[0]
                                                                                                                                                                                    cp = df['c'].iloc[-1]
                                                                                                                                                                                                    if macd.iloc[-1][0] > macd.iloc[-1][2] and cp > ich['ISA_9'].iloc[-1] and cp > ich['ISB_26'].iloc[-1]:
                                                                                                                                                                                                                        send_msg(f"🚀 **إشارة دخول: {sym}**\n💰 السعر: {cp}")
                                                                                                                                                                                                                                print("✅ اكتمل الفحص بنجاح")
                                                                                                                                                                                                                                    except Exception as e: print(f"❌ خطأ: {e}")

                                                                                                                                                                                                                                    send_msg("🤖 رادار Railway المحدث بدأ العمل!")
                                                                                                                                                                                                                                    while True:
                                                                                                                                                                                                                                        now = datetime.now()
                                                                                                                                                                                                                                            if now.second == 0: print(f"🕒 نبض البوت: {now.strftime('%H:%M')}")
                                                                                                                                                                                                                                                if now.minute in [0, 30] and now.second == 0:
                                                                                                                                                                                                                                                        run_radar()
                                                                                                                                                                                                                                                                time.sleep(1)
                                                                                                                                                                                                                                                                    time.sleep(0.8)
