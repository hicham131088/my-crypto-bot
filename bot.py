# -*- coding: utf-8 -*-
import time
import requests
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# --- الإعدادات ---
TOKEN = '7900130533:AAFP7ZYnrdUOEf-8E1rQIKWdgRfD8oJZSuw'
CHAT_ID = '6424409099'

# قائمة أشهر 400 عملة رقمية مقابل USDT
SYMBOLS_LIST = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT', 'DOGEUSDT', 'MATICUSDT', 'LTCUSDT',
    'SHIBUSDT', 'TRXUSDT', 'AVAXUSDT', 'UNIUSDT', 'LINKUSDT', 'ATOMUSDT', 'ETCUSDT', 'XLMUSDT', 'BCHUSDT', 'ALGOUSDT',
    'VETUSDT', 'MANAUSDT', 'SANDUSDT', 'HBARUSDT', 'ICPUSDT', 'FILUSDT', 'EGLDUSDT', 'NEARUSDT', 'APEUSDT', 'QNTUSDT',
    'LUNCUSDT', 'FTMUSDT', 'GRTUSDT', 'THETAUSDT', 'AXSUSDT', 'EOSUSDT', 'FLOWUSDT', 'AAVEUSDT', 'CHZUSDT', 'KCSUSDT',
    'MKRUSDT', 'ZECUSDT', 'XMRUSDT', 'IOTAUSDT', 'NEOUSDT', 'CRVUSDT', 'RUNEUSDT', 'DASHUSDT', 'KAVAUSDT', 'ENJUSDT',
    'LRCUSDT', 'BATUSDT', 'CELOUSDT', 'ZILUSDT', 'GALAUSDT', 'MINAUSDT', 'STXUSDT', 'COMPUSDT', 'GMTUSDT', 'ANKRUSDT',
    'HOTUSDT', 'QTUMUSDT', 'KSMUSDT', '1INCHUSDT', 'OMGUSDT', 'ZRXUSDT', 'RVNUSDT', 'IOTXUSDT', 'GLMRUSDT', 'WAVESUSDT',
    'ONEUSDT', 'ROSEUSDT', 'KNCUSDT', 'AUDIOUSDT', 'KDAUSDT', 'SKLUSDT', 'MASKUSDT', 'SXPUSDT', 'YFIUSDT', 'BANDUSDT',
    'ICXUSDT', 'SUSHIUSDT', 'JASMYUSDT', 'WOOUSDT', 'CHRUSDT', 'SCRTUSDT', 'WAXPUSDT', 'DYDXUSDT', 'ONTUSDT', 'FLOKIUSDT',
    'PEPEUSDT', 'ARBUSDT', 'OPUSDT', 'APTUSDT', 'SUIUSDT', 'LDOUSDT', 'ORDIUSDT', 'TIAUSDT', 'SEIUSDT', 'INJUSDT',
    'IMXUSDT', 'RNDRUSDT', 'FETUSDT', 'AGIXUSDT', 'OCEANUSDT', 'CFXUSDT', 'STGUSDT', 'HOOKUSDT', 'MAGICUSDT', 'GNSUSDT',
    'JOEUSDT', 'IDUSDT', 'LQTYUSDT', 'GMXUSDT', 'PENDLEUSDT', 'RDNTUSDT', 'FLRUSDT', 'COREUSDT', 'KASUSDT', 'BEAMUSDT',
    'PYTHUSDT', 'JTOUSDT', 'BONKUSDT', 'MEMEUSDT', 'WLDUSDT', 'ARKMUSDT', 'MAVIAUSDT', 'STRKUSDT', 'AXLUSDT',
    'PORTALUSDT', 'METISUSDT', 'AEVOUSDT', 'ETHFIUSDT', 'BOMEUSDT', 'ENAUSDT', 'WUSDT', 'SAGAUSDT', 'TNSRUSDT', 'TAOUSDT',
    'OMNIUSDT', 'REZUSDT', 'BBUSDT', 'NOTUSDT', 'IOUSDT', 'LISTAUSDT', 'ZKUSDT', 'RENDERUSDT', 'BANANAUSDT', 'DOGSUSDT',
    'TURBOUSDT', 'POPCATUSDT', 'MEWUSDT', 'BRETTUSDT', 'MOGUSDT', 'NEIROUSDT', 'BABYDOGEUSDT', 'HMSTRUSDT', 'CATIUSDT',
    'EIGENUSDT', 'SCRUSDT', 'GOATUSDT', 'MOODENGUSDT', 'GRASSUSDT', 'DRIFTUSDT', 'PENGUUSDT', 'TRUMPUSDT', 'VINEUSDT',
    'SUNUSDT', 'RAREUSDT', 'ALPACAUSDT', 'TLMUSDT', 'VOXELUSDT', 'REIUSDT', 'PROMSUSDT', 'OXTUSDT', 'VIDTUSDT', 'DOCKUSDT',
    'KEYUSDT', 'DEGOUSDT', 'HARDUSDT', 'RIFUSDT', 'FORTHUSDT', 'BURGERUSDT', 'SLPUSDT', 'BAKEUSDT', 'SYSUSDT', 'CKBUSDT',
    'DENTUSDT', 'TKOUSDT', 'LINAUSDT', 'PERPUSDT', 'STRAXUSDT', 'ALPHAUSDT', 'CTSIUSDT', 'OGNUSDT', 'BELUSDT', 'ARPAUSDT',
    'MTLUSDT', 'DGBUSDT', 'DUSKUSDT', 'COSUSDT', 'NKNUSDT', 'TFUELUSDT', 'SCUSDT', 'LSKUSDT', 'RENUSDT', 'RLCUSDT',
    'LTOUSDT', 'MFTUSDT', 'ATAUSDT', 'MLNUSDT', 'QUICKUSDT', 'POLSUSDT', 'FARMUSDT', 'REQUSDT', 'GTCUSDT',
    'CLVUSDT', 'MBOXUSDT', 'ORNUSDT', 'UTKUSDT', 'STMXUSDT', 'DEXEUSDT', 'FRONTUSDT', 'TRUUSDT', 'PONDFUSDT', 'TWTUSDT',
    'SUPERUSDT', 'BADGERUSDT', 'FISUSDT', 'MDXUSDT', 'PROSUSDT', 'VTHOUSDT', 'PUNDIXUSDT', 'LPTUSDT', 'FORUSDT', 'AKROUSDT',
    'POLUSDT', 'ELFUSDT', 'CELRUSDT', 'GTOUSDT', 'VIBUSDT', 'AMBUSDT', 'ARKUSDT', 'LOOMUSDT', 'GFTUSDT', 'PHBUSDT',
    'AGLDUSDT', 'RADUSDT', 'HIGHUSDT', 'GLMUSDT', 'LAZIOUSDT', 'PORTOUSDT', 'SANTOSUSDT', 'DARUSDT', 'BNXUSDT',
    'MOVRUSDT', 'CITYUSDT', 'ASRUSDT', 'JUVUSDT', 'ACMUSDT', 'ATMUSDT', 'OGUSDT', 'BICOUSDT', 'FLUXUSDT',
    'PYRUSDT', 'KP3RUSDT', 'QIUSDT', 'BIFIUSDT', 'OOKIUSDT', 'SPELLUSDT', 'USTCUSDT', 'ANCUSDT', 'LEVERUSDT', 'VGXUSDT',
    'STEEMUSDT', 'STORJUSDT', 'ADXUSDT', 'CVXUSDT', 'PNTUSDT', 'REPUSDT', 'PROMUSDT', 'DREPUSDT', 'TUSDT', 'ASTRUSDT',
    'ACAUSDT', 'RONINUSDT', 'XNOUSDT', 'BSWUSDT', 'EPXUSDT', 'MOBUSDT', 'NEXOUSDT', 'MDTUSDT', 'DATAUSDT', 'VICUSDT',
    'STPTUSDT', 'NULSUSDT', 'MBLUSDT', 'QKCUSDT', 'RSRUSDT', 'PSGUSDT', 'BARUSDT', 'ALPINEUSDT'
]

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}
        response = requests.post(url, data=payload, timeout=15)
        return response.status_code == 200
    except:
        return False

def get_data(symbol):
    try:
        yf_symbol = symbol.replace('USDT', '-USD')
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period="5d", interval="30m")
        if not df.empty and len(df) >= 50:
            return df
    except:
        pass
    return None

def run_radar():
    print("\n" + "="*70)
    print(f"🚀 بدء المسح الشامل - {datetime.now().strftime('%H:%M:%S')}")
    print("="*70)
    
    btc = get_data('BTCUSDT')
    if btc is None:
        print(f"❌ تعذر جلب بيانات BTC.")
        return

    ema50 = btc['Close'].ewm(span=50, adjust=False).mean()
    if btc['Close'].iloc[-1] <= ema50.iloc[-1]:
        print(f"📉 البيتكوين تحت EMA50. توقف المسح.")
        return
    
    print(f"📈 البيتكوين صاعد. فحص العملات البديلة...")

    found = 0
    for idx, s in enumerate(SYMBOLS_LIST, 1):
        try:
            df = get_data(s)
            if df is None: continue
            
            # --- التعديل الأول: فلتر السيولة الذكي ---
            vol_usd_series = df['Volume'] * df['Close']
            current_vol = vol_usd_series.iloc[-1]
            avg_vol = vol_usd_series.rolling(window=20).mean().iloc[-1]
            
            # يتجاوز العملة إذا كانت السيولة أقل من 150 ألف دولار، أو أقل من 120% من متوسط السيولة
            if current_vol < 150000 or current_vol < (avg_vol * 1.2): 
                continue
            # ----------------------------------------
            
            macd = df.ta.macd()
            ichimoku = df.ta.ichimoku()
            rsi = df.ta.rsi(length=14)
            atr = df.ta.atr(length=14)
            
            if macd is None or ichimoku is None or rsi is None or atr is None: continue

            # تعريف البيانات للشمعة الحالية المقفلة (index -1) والشمعة التي قبلها (index -2)
            cp_now = df['Close'].iloc[-1]
            isa_now = ichimoku[0]['ISA_9'].iloc[-1]
            isb_now = ichimoku[0]['ISB_26'].iloc[-1]
            macd_val_now = macd.iloc[-1, 0]
            signal_val_now = macd.iloc[-1, 1]
            rsi_now = rsi.iloc[-1]
            atr_now = atr.iloc[-1]

            cp_prev = df['Close'].iloc[-2]
            isa_prev = ichimoku[0]['ISA_9'].iloc[-2]
            isb_prev = ichimoku[0]['ISB_26'].iloc[-2]
            macd_val_prev = macd.iloc[-2, 0]
            signal_val_prev = macd.iloc[-2, 1]

            # منطق الاستراتيجية للشمعة المقفلة الحالية (تمت إضافة شرط الـ RSI هنا)
            cond_now = (macd_val_now > signal_val_now) and (cp_now > isa_now) and (cp_now > isb_now) and (rsi_now < 70)
            
            # منطق الاستراتيجية للشمعة السابقة (يجب أن يكون خطأ لضمان أن الإشارة بدأت الآن)
            cond_prev = (macd_val_prev > signal_val_prev) and (cp_prev > isa_prev) and (cp_prev > isb_prev)

            # إشارة الشراء: تحقق الشرط الآن ولم يكن متحققاً في الشمعة السابقة
            if cond_now and not cond_prev:
                # --- التعديل الثاني والثالث: تعديل الـ ATR لوقف الخسارة وأخذ الربح ---
                sl_price = cp_now - (1.2 * atr_now)
                tp_price = cp_now + (2.4 * atr_now)
                sl_pct = ((1.2 * atr_now) / cp_now) * 100
                tp_pct = ((2.4 * atr_now) / cp_now) * 100
                # -----------------------------------------------------------------

                msg = f"✅ *إشارة شراء جديدة (انفجار سيولة)!*\n\n💎 العملة: #{s}\n💵 السعر: ${cp_now:.4f}\n🎯 أخذ الربح: ${tp_price:.4f} (+{tp_pct:.2f}%)\n🛑 وقف الخسارة: ${sl_price:.4f} (-{sl_pct:.2f}%)\n🕒 وقت الإغلاق: {datetime.now().strftime('%H:%M')}"
                send_msg(msg)
                print(f"✨ إشارة جديدة: {s}")
                found += 1
        except:
            pass
        
        if idx % 50 == 0:
            print(f"⏳ فحص {idx}/{len(SYMBOLS_LIST)}...")

    print(f"\n✅ اكتمل المسح. الإشارات الجديدة: {found}")
    print("="*70)

# التشغيل
print("\n" + "="*70)
print("🤖 بوت صيد العملات (فلتر التقاطع الصاعد)")
print("="*70)

start_txt = f"🚀 *تم تشغيل البوت بنجاح!*\n🔍 يراقب: 400 عملة\n⚙️ الاستراتيجية: إيشيموكو + ماكدي + انفجار سيولة."
send_msg(start_txt)

run_radar()

last_min = -1
while True:
    try:
        now = datetime.now()
        if now.minute in [0, 30] and now.minute != last_min:
            run_radar()
            last_min = now.minute
        if now.minute % 10 == 0 and now.second == 0:
            print(f"🕒 نبض النظام: {now.strftime('%H:%M')} - مراقبة مستمرة")
        time.sleep(1)
    except Exception as e:
        time.sleep(10)
            
