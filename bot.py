import time, requests, pandas as pd, pandas_ta as ta, yfinance as yf
from datetime import datetime
import warnings

# إخفاء التحذيرات لضمان استقرار السجلات
warnings.simplefilter(action='ignore', category=FutureWarning)

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
        yf_symbol = symbol.replace('USDT', '-USD')
        df = yf.download(yf_symbol, period="5d", interval="30m", progress=False, show_errors=False)
        return df if not df.empty else pd.DataFrame()
    except: return pd.DataFrame()

def get_full_market_list():
    # قائمة 200 عملة (الأقوى + الميم + العملات الجديدة)
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
    now_str = datetime.now().strftime('%H:%M')
    print(f"🚀 [1/4] {now_str} | بدء المسح")
    try:
        btc = get_data('BTCUSDT')
        if btc.empty or len(btc) < 50:
            print("❌ فشل جلب BTC")
            return
        
        ema50 = btc.ta.ema(length=50)
        curr_btc = btc['Close'].iloc[-1]
        if curr_btc <= ema50.iloc[-1]:
            print(f"🛑 سوق هابط (BTC < EMA50)")
            return

        print(f"✅ سوق صاعد. جاري فحص 200 عملة...")
        all_syms = get_full_market_list()
        found = 0
        
        for i, s in enumerate(all_syms, 1):
            df = get_data(s)
            if not df.empty and len(df) >= 52:
                v_usd = df['Volume'].iloc[-1] * df['Close'].iloc[-1]
                if v_usd >= 200000:
                    try:
                        m = df.ta.macd()
                        # إعدادات ثابتة للإيشيموكو لمنع أي تحذير
                        ic = df.ta.ichimoku(tenkan=9, kijun=26, senkou=52)[0]
                        cp = df['Close'].iloc[-1]
                        if m.iloc[-1][0] > m.iloc[-1][2] and cp > ic['ISA_9'].iloc[-1] and cp > ic['ISB_26'].iloc[-1]:
                            send_msg(f"🚀 **دخول: {s}**\n💰 السعر: {cp:.4f}")
                            found += 1
                    except: pass
            
            if i % 40 == 0:
                print(f"📊 التقدم: {i}/200")
            time.sleep(0.05)
            
        print(f"🏁 انتهى. الإشارات: {found}")
    except Exception as e:
        print(f"⚠️ خطأ: {e}")

# البدء
send_msg("📡 البوت يعمل الآن بقائمة 200 عملة محدثة.")

last_min = -1
while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_min:
        last_min = now.minute
        print(f"🕒 نبض: {now.strftime('%H:%M')}")
        if now.minute in [0, 30]:
            run_radar()
    time.sleep(1)
