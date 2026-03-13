Import time, requests, pandas as pd, pandas_ta as ta, yfinance as yf
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
        if not df.empty: return df
    except: pass
    return pd.DataFrame()

def get_full_market_list():
    return [
        'BTCUSDT','ETHUSDT','BNBUSDT','SOLUSDT','XRPUSDT','ADAUSDT','AVAXUSDT','DOTUSDT','DOGEUSDT','LINKUSDT',
        'MATICUSDT','LTCUSDT','UNIUSDT','ATOMUSDT','TRXUSDT','BCHUSDT','ETCUSDT','XLMUSDT','ICPUSDT','FILUSDT',
        'APTUSDT','ARBUSDT','OPUSDT','SUIUSDT','SEIUSDT','TIAUSDT','NEARUSDT','INJUSDT','RNDRUSDT','STXUSDT',
        'TAOUSDT','IMXUSDT','GRTUSDT','FETUSDT','RUNEUSDT','AAVEUSDT','MKRUSDT','SNXUSDT','CRVUSDT','LDOUSDT',
        'DYDXUSDT','GMXUSDT','PYTHUSDT','JUPUSDT','PENDLEUSDT','ENAUSDT','STRKUSDT','ZROUSDT','WLDUSDT','ARKMUSDT',
        'ORDIUSDT','KASUSDT','KAVAUSDT','HBARUSDT','ALGOUSDT','EGLDUSDT','FLOWUSDT','ROSEUSDT','CELOUSDT','CFXUSDT',
        'MINAUSDT','FTMUSDT','SANDUSDT','MANAUSDT','AXSUSDT','GALAUSDT','CHZUSDT','ENJUSDT','APEUSDT','BLURUSDT',
        'MAGICUSDT','SUPERUSDT','HIGHUSDT','YGGUSDT','SKLUSDT','STORJUSDT','ARUSDT','QNTUSDT','QTUMUSDT','IOTAUSDT',
        'DASHUSDT','ZECUSDT','COMPUSDT','BALUSDT','KNCUSDT','1INCHUSDT','BANDUSDT','API3USDT','ANKRUSDT','LRCUSDT',
        'OCEANUSDT','AGIXUSDT','NMRUSDT','GLMUSDT','MOVRUSDT','METISUSDT','RLCUSDT','RSRUSDT','REEFUSDT','RVNUSDT',
        'CKBUSDT','ONTUSDT','OMGUSDT','SXPUSDT','DGBUSDT','SCUSDT','ZENUSDT','ICXUSDT','ZILUSDT','WAVESUSDT',
        'PEPEUSDT','SHIBUSDT','FLOKIUSDT','BONKUSDT','WIFUSDT','MEMEUSDT','BOMEUSDT','MYROUSDT','DOGSUSDT','BABYDOGEUSDT',
        'NOTUSDT','TURBOUSDT','BRETTUSDT','MOGUSDT','PNUTUSDT','POPCATUSDT','NEIROUSDT','GMEUSDT','WOJAKUSDT','LADYSUSDT',
        'SATSUSDT','ORDSUSDT','RATSUSDT','TOSHIUSDT','HARAMBEUSDT','CATUSDT','HIPPOUSDT','PONKEUSDT','FUDUSDT','SMOGUSDT',
        'PIXELUSDT','PORTALUSDT','ALTUSDT','AIUSDT','ACEUSDT','DYMUSDT','SAGAUSDT','LISTAUSDT','IOSTUSDT','IDUSDT',
        'HOOKUSDT','EDUUSDT','NFPUSDT','CYBERUSDT','AEVOUSDT','OMNIUSDT','ETHFIUSDT','REZUSDT','BBUSDT','TNSRUSDT',
        'MANTAUSDT','ASTRUSDT','JOEUSDT','RAYUSDT','SFPUSDT','HFTUSDT','ARKUSDT','C98USDT','ATAUSDT','DARUSDT',
        'RADUSDT','FORTHUSDT','OGNUSDT','PERPUSDT','PHBUSDT','LPTUSDT','LQTYUSDT','MTLUSDT','NKNUSDT','POWRUSDT',
        'PROMUSDT','RAREUSDT','REQUSDT','RIFUSDT','SCRUSDT','SLPUSDT','SPELLUSDT','STEEMUSDT','STGUSDT','SUNUSDT'
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
            print(f"🛑 زخم هابط (BTC: {curr_btc:.0f} < EMA: {l_ema50:.0f}). إنهاء المسح.")
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
                        ic = df.ta.ichimoku()[0] # استخدام التلقائي لتجنب التحذير
                        cp = df['Close'].iloc[-1]
                        
                        # شرط الاستراتيجية
                        if m.iloc[-1][0] > m.iloc[-1][2] and cp > ic['ISA_9'].iloc[-1] and cp > ic['ISB_26'].iloc[-1]:
                            send_msg(f"🚀 **إشارة دخول: {s}**\n💰 السعر: {cp:.4f}\n📈 BTC: صاعد")
                            found_signals += 1
                    except: continue

            # طباعة نسبة التقدم كل 20 عملة لتجنب ازدحام السجلات
            if processed_count % 20 == 0 or processed_count == total_symbols:
                percentage = (processed_count / total_symbols) * 100
                print(f"📊 التقدم: {percentage:.0f}% ({processed_count}/{total_symbols}) | السيولة: {passed_liquidity} عملة")
            
            time.sleep(0.05) # تسريع الفحص قليلاً

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
