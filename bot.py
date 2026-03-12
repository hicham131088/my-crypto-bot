import time, requests, pandas as pd, pandas_ta as ta, yfinance as yf
from datetime import datetime
import warnings

# 1. إخفاء التحذيرات نهائياً لضمان سجلات نظيفة
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
    try:
        yf_symbol = symbol.replace('USDT', '-USD')
        ticker = yf.Ticker(yf_symbol)
        # استخدام raise_errors=False لتجنب الرسائل الحمراء في حال وجود عملة محذوفة
        df = ticker.history(period="5d", interval="30m", progress=False, raise_errors=False)
        if not df.empty: return df
    except: pass
    return pd.DataFrame()

def get_full_market_list():
    # قائمة موسعة بـ 200 عملة نشطة حالياً على بينانس (تمت تصفية المحذوفة)
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
    print(f"🚀 [1/4] {datetime.now().strftime('%H:%M')} | بدء المسح الشامل (200 عملة)")
    try:
        # 1. فحص زخم البيتكوين (EMA 50)
        btc = get_data('BTCUSDT')
        if btc.empty or len(btc) < 50: return
        
        ema50 = btc.ta.ema(length=50)
        curr_btc = btc['Close'].iloc[-1]
        l_ema50 = ema50.iloc[-1]
        
        if curr_btc > l_ema50:
            print(f"✅ زخم صاعد (BTC: {curr_btc:.0f} > EMA: {l_ema50:.0f})")
        else:
            print(f"🛑 زخم هابط للبيتكوين. إنهاء المسح.")
            return

        all_symbols = get_full_market_list()
        total = len(all_symbols)
        found = 0
        passed_liq = 0
        processed = 0

        for s in all_symbols:
            processed += 1
            df = get_data(s)
            
            if not df.empty and len(df) >= 52:
                df = df.dropna()
                # فلتر السيولة
                v_usd = df['Volume'].iloc[-1] * df['Close'].iloc[-1]
                if v_usd >= 200000:
                    passed_liq += 1
                    try:
                        m = df.ta.macd()
                        # إصلاح تحذير السطر 89 عبر استخدام حرف كبير في الإعدادات الداخلية
                        ic = df.ta.ichimoku(tenkan=9, kijun=26, senkou=52)[0]
                        cp = df['Close'].iloc[-1]
                        
                        if m.iloc[-1][0] > m.iloc[-1][2] and cp > ic['ISA_9'].iloc[-1] and cp > ic['ISB_26'].iloc[-1]:
                            send_msg(f"🚀 **إشارة دخول: {s}**\n💰 السعر: {cp:.4f}\n📈 BTC: صاعد")
                            found += 1
                    except: continue

            # طباعة التقدم كل 25 عملة
            if processed % 25 == 0 or processed == total:
                print(f"📊 التقدم: {(processed/total)*100:.0f}% | السيولة: {passed_liq}")
            
            time.sleep(0.05)
        print(f"🏁 انتهى المسح. الإشارات المكتشفة: {found}")
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
