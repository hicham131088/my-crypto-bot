import time, requests, pandas as pd, pandas_ta as ta, yfinance as yf
from datetime import datetime
import warnings

# إسكات التحذيرات لضمان نظافة السجلات وسرعة التنفيذ
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
        # جلب البيانات بالأسماء الأصلية لتجنب خطأ "column not found"
        df = ticker.history(period="5d", interval="30m", progress=False, raise_errors=False)
        return df
    except: return pd.DataFrame()

def get_full_market_list():
    # القائمة المنقحة التي طلبتها لـ 200 عملة
    return [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT', 'AVAXUSDT', 'DOTUSDT', 'DOGEUSDT', 'LINKUSDT',
        'SHIBUSDT', 'MATICUSDT', 'LTCUSDT', 'UNIUSDT', 'NEARUSDT', 'APTUSDT', 'OPUSDT', 'ARBUSDT', 'SUIUSDT', 'FETUSDT',
        'RNDRUSDT', 'PEPEUSDT', 'FLOKIUSDT', 'INJUSDT', 'TIAUSDT', 'STXUSDT', 'ORDIUSDT', 'ICPUSDT', 'TRXUSDT', 'ETCUSDT',
        'BCHUSDT', 'AAVEUSDT', 'ALGOUSDT', 'SANDUSDT', 'MANAUSDT', 'ATOMUSDT', 'VETUSDT', 'IMXUSDT', 'GRTUSDT', 'SEIUSDT',
        'GALAUSDT', 'JUPUSDT', 'PYTHUSDT', 'DYMUSDT', 'PENDLEUSDT', 'AXSUSDT', 'MKRUSDT', 'SNXUSDT', 'WLDUSDT', 'ARKMUSDT',
        'STRKUSDT', 'ENAUSDT', 'WUSDT', 'SAGAUSDT', 'TAOUSDT', 'NOTUSDT', 'IOUSDT', 'ZROUSDT', 'DOGSUSDT', 'ASTRUSDT',
        'ANKRUSDT', 'AGLDUSDT', 'ACEUSDT', 'ALTUSDT', 'AIUSDT', 'API3USDT', 'ARKUSDT', 'ARUSDT', 'AUCTIONUSDT', 'BADGERUSDT',
        'BALUSDT', 'BATUSDT', 'BELUSDT', 'BICOUSDT', 'BLZUSDT', 'BNXUSDT', 'BONKUSDT', 'CELOUSDT', 'CFXUSDT', 'CHZUSDT',
        'CKBUSDT', 'COMPUSDT', 'COTIUSDT', 'CYBERUSDT', 'DASHUSDT', 'DYDXUSDT', 'EDUUSDT', 'EGLDUSDT', 'ENJUSDT', 'EOSUSDT',
        'ETHFIUSDT', 'FTMUSDT', 'GLMUSDT', 'GMTUSDT', 'GMXUSDT', 'HBARUSDT', 'HIGHUSDT', 'HOOKUSDT', 'IOTAUSDT', 'IOTXUSDT',
        'JASMYUSDT', 'KAVAUSDT', 'KNCUSDT', 'LPTUSDT', 'LRCUSDT', 'MAGICUSDT', 'MANTAUSDT', 'MASKUSDT', 'MINAUSDT', 'MOVRUSDT',
        'MYROUSDT', 'NFPUSDT', 'NTRNUSDT', 'OGNUSDT', 'ONTUSDT', 'PHBUSDT', 'PNUTUSDT', 'POLYXUSDT', 'POWRUSDT', 'QNTUSDT',
        'QTUMUSDT', 'RAYUSDT', 'REEFUSDT', 'RIFUSDT', 'RLCUSDT', 'ROSEUSDT', 'RUNEUSDT', 'RVNUSDT', 'SKLUSDT', 'SXPUSDT',
        'THETAUSDT', 'TRBUSDT', 'UMAUSDT', 'VTHOUSDT', 'WAXPUSDT', 'WIFUSDT', 'WOOUSDT', 'XLMUSDT', 'XTZUSDT', 'YFIUSDT',
        'ZECUSDT', 'ZENUSDT', 'ZILUSDT', 'ZRXUSDT', '1INCHUSDT', 'AERGOUSDT', 'ALICEUSDT', 'ALPACAUSDT', 'ALPHAUSDT', 'AMBUSDT',
        'ANRWUSDT', 'APEUSDT', 'ARDRUSDT', 'ASRUSDT', 'ATMUSDT', 'AUDIOUSDT', 'AVAUSDT', 'BAKEUSDT', 'BARUSDT', 'BDPUSDT',
        'BETAUSDT', 'BIFIUSDT', 'BONDUSDT', 'BSWUSDT', 'BURGERUSDT', 'CITYUSDT', 'CLVUSDT', 'CTKUSDT', 'CTSIUSDT', 'CVXUSDT',
        'DENTUSDT', 'DOCKUSDT', 'DUSKUSDT', 'EPXUSDT', 'ERNUSDT', 'FARMUSDT', 'FIDAUSDT', 'FISUSDT', 'GNSUSDT', 'LINAUSDT'
    ]

def run_radar():
    print(f"🚀 [1/4] {datetime.now().strftime('%H:%M')} | بدء المسح الشامل")
    try:
        # 1. فحص زخم البيتكوين (EMA 50)
        btc = get_data('BTCUSDT')
        if btc.empty or len(btc) < 50: 
            print("❌ فشل جلب بيانات البيتكوين")
            return
        
        ema50 = btc.ta.ema(length=50)
        curr_btc = btc['Close'].iloc[-1]
        l_ema50 = ema50.iloc[-1]
        
        if curr_btc > l_ema50:
            print(f"✅ زخم صاعد (BTC: {curr_btc:.0f} > EMA: {l_ema50:.0f})")
        else:
            print(f"🛑 زخم هابط (BTC: {curr_btc:.0f} < EMA: {l_ema50:.0f}). إنهاء المسح.")
            return

        all_symbols = get_full_market_list()
        total = len(all_symbols)
        found = 0
        passed_liq = 0
        processed = 0

        # 2. تحليل العملات مع طباعة التقدم
        for s in all_symbols:
            processed += 1
            df = get_data(s)
            
            if not df.empty and len(df) >= 52:
                # فلتر السيولة
                v_usd = df['Volume'].iloc[-1] * df['Close'].iloc[-1]
                if v_usd >= 200000:
                    passed_liq += 1
                    try:
                        m = df.ta.macd()
                        # تصحيح تحذير حرف 'd' عبر الإدخال اليدوي
                        ic = df.ta.ichimoku(tenkan=9, kijun=26, senkou=52)[0]
                        cp = df['Close'].iloc[-1]
                        
                        # شروط الاستراتيجية الأصلية
                        if m.iloc[-1][0] > m.iloc[-1][2] and cp > ic['ISA_9'].iloc[-1] and cp > ic['ISB_26'].iloc[-1]:
                            send_msg(f"🚀 **إشارة دخول: {s}**\n💰 السعر: {cp:.4f}\n📈 BTC: صاعد")
                            found += 1
                    except: continue

            # إرجاع ميزة طباعة التقدم التي كانت موجودة
            if processed % 20 == 0 or processed == total:
                print(f"📊 التقدم: {(processed/total)*100:.0f}% ({processed}/{total}) | السيولة: {passed_liq} عملة")
            
            time.sleep(0.05)
        print(f"🏁 انتهى المسح. الإشارات: {found}")
    except Exception as e:
        print(f"⚠️ خطأ عام: {e}")

last_pulse = -1
while True:
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
