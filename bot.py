import time, requests, pandas as pd, pandas_ta as ta, yfinance as yf
from datetime import datetime
import warnings

# 1. إخفاء التحذيرات المزعجة نهائياً لضمان استقرار السيرفر
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None 

# --- الإعدادات الأساسية ---
TOKEN = '7900130533:AAFP7ZYnrdUOEf-8E1rQIKWdgRfD8oJZSuw'
CHAT_ID = '6424409099'

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}, timeout=15)
    except: pass

def get_data(symbol):
    """ جلب البيانات مع محاولة إعادة الاتصال في حال الفشل """
    yf_symbol = symbol.replace('USDT', '-USD')
    for attempt in range(3): # محاولة الجلب حتى 3 مرات
        try:
            df = yf.download(yf_symbol, period="5d", interval="30m", progress=False, show_errors=False)
            if not df.empty and len(df) > 50:
                return df
        except:
            time.sleep(2)
    return pd.DataFrame()

def get_full_market_list():
    # قائمة الـ 200 عملة المنقحة لعام 2026
    return [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT', 'AVAXUSDT', 'DOTUSDT', 'DOGEUSDT', 'LINKUSDT',
        'SHIBUSDT', 'MATICUSDT', 'LTCUSDT', 'UNIUSDT', 'NEARUSDT', 'APTUSDT', 'OPUSDT', 'ARBUSDT', 'SUIUSDT', 'FETUSDT',
        'PEPEUSDT', 'FLOKIUSDT', 'INJUSDT', 'TIAUSDT', 'STXUSDT', 'ORDIUSDT', 'ICPUSDT', 'TRXUSDT', 'ETCUSDT', 'BCHUSDT',
        'AAVEUSDT', 'ALGOUSDT', 'SANDUSDT', 'MANAUSDT', 'ATOMUSDT', 'VETUSDT', 'IMXUSDT', 'GRTUSDT', 'SEIUSDT', 'GALAUSDT',
        'JUPUSDT', 'PYTHUSDT', 'DYMUSDT', 'PENDLEUSDT', 'AXSUSDT', 'MKRUSDT', 'SNXUSDT', 'WLDUSDT', 'ARKMUSDT', 'STRKUSDT',
        'ENAUSDT', 'WUSDT', 'SAGAUSDT', 'TAOUSDT', 'NOTUSDT', 'IOUSDT', 'ZROUSDT', 'DOGSUSDT', 'ASTRUSDT', 'ANKRUSDT',
        'AGLDUSDT', 'ACEUSDT', 'ALTUSDT', 'AIUSDT', 'API3USDT', 'ARKUSDT', 'ARUSDT', 'AUCTIONUSDT', 'BADGERUSDT', 'BALUSDT',
        'BATUSDT', 'BELUSDT', 'BICOUSDT', 'BLZUSDT', 'BNXUSDT', 'BONKUSDT', 'CELOUSDT', 'CFXUSDT', 'CHZUSDT', 'CKBUSDT',
        'COMPUSDT', 'COTIUSDT', 'CYBERUSDT', 'DASHUSDT', 'DYDXUSDT', 'EDUUSDT', 'EGLDUSDT', 'ENJUSDT', 'EOSUSDT', 'ETHFIUSDT',
        'FTMUSDT', 'GLMUSDT', 'GMTUSDT', 'GMXUSDT', 'HBARUSDT', 'HIGHUSDT', 'HOOKUSDT', 'IOTAUSDT', 'IOTXUSDT', 'JASMYUSDT',
        'KAVAUSDT', 'KNCUSDT', 'LPTUSDT', 'LRCUSDT', 'MAGICUSDT', 'MANTAUSDT', 'MASKUSDT', 'MINAUSDT', 'MOVRUSDT', 'MYROUSDT',
        'NFPUSDT', 'NTRNUSDT', 'OGNUSDT', 'ONTUSDT', 'PHBUSDT', 'PNUTUSDT', 'POLYXUSDT', 'POWRUSDT', 'QNTUSDT', 'QTUMUSDT',
        'RAYUSDT', 'REEFUSDT', 'RIFUSDT', 'RLCUSDT', 'ROSEUSDT', 'RUNEUSDT', 'RVNUSDT', 'SKLUSDT', 'STGUSDT', 'STORJUSDT'
    ]

def run_radar():
    print(f"🚀 [1/4] {datetime.now().strftime('%H:%M')} | بدء المسح")
    try:
        # 1. فحص البيتكوين
        btc = get_data('BTCUSDT')
        if btc.empty:
            print("❌ تعذر جلب بيانات BTC. سيتم المحاولة في الدورة القادمة.")
            return
        
        # التأكد من أسماء الأعمدة لمنع خطأ column not found
        ema50 = btc.ta.ema(close='Close', length=50)
        curr_btc = btc['Close'].iloc[-1]
        l_ema50 = ema50.iloc[-1]
        
        if curr_btc > l_ema50:
            print(f"✅ زخم صاعد (BTC: {curr_btc:.0f} > EMA: {l_ema50:.0f})")
        else:
            print(f"🛑 زخم هابط للبيتكوين. توقف المسح.")
            return

        all_symbols = get_full_market_list()
        total, found, passed_liq, processed = len(all_symbols), 0, 0, 0

        # 2. تحليل العملات
        for s in all_symbols:
            processed += 1
            df = get_data(s)
            
            if not df.empty and len(df) >= 52:
                v_usd = df['Volume'].iloc[-1] * df['Close'].iloc[-1]
                if v_usd >= 200000:
                    passed_liq += 1
                    try:
                        m = df.ta.macd(close='Close')
                        # حل تحذير حرف 'd' باستخدام الإعدادات الصريحة
                        ic = df.ta.ichimoku(tenkan=9, kijun=26, senkou=52)[0]
                        cp = df['Close'].iloc[-1]
                        
                        if m.iloc[-1][0] > m.iloc[-1][2] and cp > ic['ISA_9'].iloc[-1] and cp > ic['ISB_26'].iloc[-1]:
                            send_msg(f"🚀 **إشارة دخول: {s}**\n💰 السعر: {cp:.4f}")
                            found += 1
                    except: continue

            if processed % 25 == 0 or processed == total:
                print(f"📊 التقدم: {(processed/total)*100:.0f}% | السيولة: {passed_liq}")
            
            time.sleep(0.1)
        print(f"🏁 انتهى: {found} إشارة.")
    except Exception as e:
        print(f"⚠️ خطأ عام: {e}")

# إرسال إشعار التشغيل
send_msg("📡 **الرادار يعمل الآن.** تم إصلاح مشاكل جلب البيانات والتحذيرات.")

last_pulse = -1
while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)
send_msg("📡 **رادار الـ 200 عملة يعمل الآن بنظام الـ EMA 50.**\nتم تصحيح الأخطاء وإعادة تفعيل التقارير.")

last_pulse = -1
while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)
