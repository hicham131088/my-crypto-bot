import time, requests, pandas as pd, pandas_ta as ta, yfinance as yf
from datetime import datetime
import warnings

# إسكات التحذيرات لضمان نظافة السجلات
warnings.simplefilter(action='ignore', category=FutureWarning)

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
        if not df.empty: return df
    except: pass
    return pd.DataFrame()

def get_full_market_list():
    # قائمة 200 عملة تضم الأقوى، الميم، والعملات الجديدة النشطة
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
        'RAYUSDT', 'REEFUSDT', 'RIFUSDT', 'RLCUSDT', 'ROSEUSDT', 'RUNEUSDT', 'RVNUSDT', 'SKLUSDT', 'SXPUSDT', 'THETAUSDT',
        'TRBUSDT', 'UMAUSDT', 'VTHOUSDT', 'WAXPUSDT', 'WIFUSDT', 'WOOUSDT', 'XLMUSDT', 'XTZUSDT', 'YFIUSDT', 'ZECUSDT',
        'ZENUSDT', 'ZILUSDT', 'ZRXUSDT', '1INCHUSDT', 'AERGOUSDT', 'ALICEUSDT', 'ALPACAUSDT', 'ALPHAUSDT', 'AMBUSDT', 'APEUSDT',
        'ARDRUSDT', 'ASRUSDT', 'ATMUSDT', 'AUDIOUSDT', 'AVAUSDT', 'BAKEUSDT', 'BARUSDT', 'BDPUSDT', 'BETAUSDT', 'BIFIUSDT',
        'BONDUSDT', 'BSWUSDT', 'BURGERUSDT', 'C98USDT', 'CITYUSDT', 'CLVUSDT', 'CTKUSDT', 'CTSIUSDT', 'CVXUSDT', 'DENTUSDT',
        'DOCKUSDT', 'DUSKUSDT', 'EPXUSDT', 'ERNUSDT', 'FARMUSDT', 'FIDAUSDT', 'FISUSDT', 'GNSUSDT', 'LINAUSDT', 'LQTYUSDT',
        'MBOXUSDT', 'METISUSDT', 'MTLUSDT', 'NKNUSDT', 'NMRUSDT', 'OGUSDT', 'OMGUSDT', 'ONGUSDT', 'OXTUSDT', 'PDAUSDT',
        'PERPUSDT', 'POLSUSDT', 'PONDUSDT', 'PSGUSDT', 'PUNDIXUSDT', 'PYRUSDT', 'QIUSDT', 'RADUSDT', 'REIUSDT', 'REQUSDT'
    ]

def run_radar():
    print(f"🚀 [1/4] {datetime.now().strftime('%H:%M')} | بدء المسح الشامل")
    try:
        # 1. فحص زخم البيتكوين (EMA 50)
        btc = get_data('BTCUSDT')
        if btc.empty or len(btc) < 50: 
            print("❌ بيانات البيتكوين غير مكتملة.")
            return
        
        ema50 = btc.ta.ema(length=50)
        curr_btc = btc['Close'].iloc[-1]
        l_ema50 = ema50.iloc[-1]
        
        if curr_btc > l_ema50:
            print(f"✅ زخم صاعد (BTC: {curr_btc:.0f} > EMA: {l_ema50:.0f})")
        else:
            print(f"🛑 زخم هابط للبيتكوين. إنهاء المسح.")
            return

        # 2. تحليل العملات مع عداد التقدم
        all_symbols = get_full_market_list()
        total_symbols = len(all_symbols)
        found_signals = 0
        passed_liquidity = 0
        processed_count = 0

        print(f"⏳ [3/4] جاري تحليل {total_symbols} عملة...")

        for s in all_symbols:
            processed_count += 1
            df = get_data(s)
            
            if not df.empty and len(df) >= 50:
                df = df.dropna()
                
                # فحص السيولة (200 ألف دولار)
                v_usd = df['Volume'].iloc[-1] * df['Close'].iloc[-1]
                if v_usd >= 200000:
                    passed_liquidity += 1
                    try:
                        m = df.ta.macd()
                        ic = df.ta.ichimoku()[0]
                        cp = df['Close'].iloc[-1]
                        
                        # شرط الاستراتيجية
                        if m.iloc[-1][0] > m.iloc[-1][2] and cp > ic['ISA_9'].iloc[-1] and cp > ic['ISB_26'].iloc[-1]:
                            send_msg(f"🚀 **إشارة دخول: {s}**\n💰 السعر: {cp:.4f}\n📈 BTC: صاعد")
                            found_signals += 1
                    except: continue

            # طباعة نسبة التقدم كل 20 عملة
            if processed_count % 20 == 0 or processed_count == total_symbols:
                percentage = (processed_count / total_symbols) * 100
                print(f"📊 التقدم: {percentage:.0f}% ({processed_count}/{total_symbols}) | السيولة: {passed_liquidity} عملة")
            
            time.sleep(0.05)

        print(f"🏁 اكتمل المسح: {found_signals} إشارة.")
    except Exception as e:
        print(f"⚠️ خطأ عام: {e}")

# رسالة البدء - ستصلك فوراً عند تشغيل البوت
send_msg("📡 رادار الـ 200 عملة يعمل الآن بنظام الـ EMA 50.")

last_pulse = -1
while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)

# رسالة البدء
send_msg("📡 رادار الـ 200 عملة يعمل الآن بنظام الـ EMA 50.")

last_pulse = -1
while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)

last_pulse = -1
while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)


last_pulse = -1
while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)
                percentage = (processed_count / total_symbols) * 100
                print(f"📊 التقدم: {percentage:.0f}% ({processed_count}/{total_symbols}) | السيولة: {passed_liquidity} عملة")
            
            time.sleep(0.05) 

        print(f"🏁 اكتمل المسح: {found_signals} إشارة | {passed_liquidity} عملة اجتازت السيولة.")
    except Exception as e:
        print(f"⚠️ خطأ عام: {e}")

# رسالة البدء
send_msg("📡 رادار الـ 200 عملة يعمل الآن بنظام الـ EMA 50.")

last_pulse = -1
while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)
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
