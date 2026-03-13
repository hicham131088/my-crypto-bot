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

# قائمة أشهر 400 عملة رقمية مقابل USDT (يدوية لضمان الاستقرار)
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
    'PYTHUSDT', 'JTOUSDT', 'BONKUSDT', 'MEMEUSDT', 'ORDIUSDT', 'WLDUSDT', 'ARKMUSDT', 'MAVIAUSDT', 'STRKUSDT', 'AXLUSDT',
    'PORTALUSDT', 'METISUSDT', 'AEVOUSDT', 'ETHFIUSDT', 'BOMEUSDT', 'ENAUSDT', 'WUSDT', 'SAGAUSDT', 'TNSRUSDT', 'TAOUSDT',
    'OMNIUSDT', 'REZUSDT', 'BBUSDT', 'NOTUSDT', 'IOUSDT', 'LISTAUSDT', 'ZKUSDT', 'RENDERUSDT', 'BANANAUSDT', 'DOGSUSDT',
    'TURBOUSDT', 'POPCATUSDT', 'MEWUSDT', 'BRETTUSDT', 'MOGUSDT', 'NEIROUSDT', 'BABYDOGEUSDT', 'HMSTRUSDT', 'CATIUSDT',
    'EIGENUSDT', 'SCRUSDT', 'GOATUSDT', 'MOODENGUSDT', 'GRASSUSDT', 'DRIFTUSDT', 'PENGUUSDT', 'TRUMPUSDT', 'VINEUSDT',
    'SUNUSDT', 'RAREUSDT', 'ALPACAUSDT', 'TLMUSDT', 'VOXELUSDT', 'REIUSDT', 'PROMSUSDT', 'OXTUSDT', 'VIDTUSDT', 'DOCKUSDT',
    'KEYUSDT', 'DEGOUSDT', 'HARDUSDT', 'RIFUSDT', 'FORTHUSDT', 'BURGERUSDT', 'SLPUSDT', 'BAKEUSDT', 'SYSUSDT', 'CKBUSDT',
    'DENTUSDT', 'TKOUSDT', 'LINAUSDT', 'PERPUSDT', 'STRAXUSDT', 'ALPHAUSDT', 'CTSIUSDT', 'OGNUSDT', 'BELUSDT', 'ARPAUSDT',
    'MTLUSDT', 'DGBUSDT', 'DUSKUSDT', 'COSUSDT', 'NKNUSDT', 'TFUELUSDT', 'SCUSDT', 'LSKUSDT', 'RENUSDT', 'RLCUSDT',
    'LTOUSDT', 'MFTUSDT', 'ATAUSDT', 'MLNUSDT', 'QUICKUSDT', 'POLSUSDT', 'FARMUSDT', 'REQUSDT', 'GTCUSDT', 'MLNUSDT',
    'CLVUSDT', 'MBOXUSDT', 'ORNUSDT', 'UTKUSDT', 'STMXUSDT', 'DEXEUSDT', 'FRONTUSDT', 'TRUUSDT', 'PONDFUSDT', 'TWTUSDT',
    'SUPERUSDT', 'BADGERUSDT', 'FISUSDT', 'MDXUSDT', 'PROSUSDT', 'VTHOUSDT', 'PUNDIXUSDT', 'LPTUSDT', 'FORUSDT', 'AKROUSDT',
    'POLUSDT', 'ELFUSDT', 'CELRUSDT', 'GTOUSDT', 'VIBUSDT', 'AMBUSDT', 'ARKUSDT', 'LOOMUSDT', 'GFTUSDT', 'PHBUSDT',
    'AGLDUSDT', 'RADUSDT', 'HIGHUSDT', 'GLMUSDT', 'LAZIOUSDT', 'PORTOUSDT', 'SANTOSUSDT', 'VOXELUSDT', 'DARUSDT', 'BNXUSDT',
    'MOVRUSDT', 'CITYUSDT', 'ASRUSDT', 'JUVUSDT', 'ACMUSDT', 'ATMUSDT', 'OGUSDT', 'BICOUSDT', 'FLUXUSDT', 'VOXELUSDT',
    'PYRUSDT', 'KP3RUSDT', 'QIUSDT', 'MCUSDT', 'BIFIUSDT', 'OOKIUSDT', 'SPELLUSDT', 'USTCUSDT', 'ANCUSDT', 'LUNCUSDT',
    'GALUSDT', 'OPUSDT', 'LEVERUSDT', 'LDOUSDT', 'VGXUSDT', 'STEEMUSDT', 'MTLUSDT', 'STORJUSDT', 'ADXUSDT', 'CVXUSDT',
    'PNTUSDT', 'REPUSDT', 'PROMUSDT', 'DREPUSDT', 'INJUSDT', 'TUSDT', 'ASTRUSDT', 'KDAUSDT', 'GLMRUSDT', 'ACAUSDT',
    'RONINUSDT', 'XNOUSDT', 'REIUSDT', 'BSWUSDT', 'EPXUSDT', 'MOBUSDT', 'NEXOUSDT', 'GALUSDT', 'LDOUSDT', 'ENJUSDT',
    'MDTUSDT', 'DOCKUSDT', 'DATAUSDT', 'UTKUSDT', 'VICUSDT', 'STPTUSDT', 'RAREUSDT', 'PROSUSDT', 'VIBUSDT', 'STMXUSDT',
    'NULSUSDT', 'ZVPUSDT', 'MBLUSDT', 'WNMUSDT', 'QKCUSDT', 'LOOMUSDT', 'RSRUSDT', 'OGUSDT', 'PSGUSDT', 'BARUSDT',
    'JUVUSDT', 'CITYUSDT', 'ATMUSDT', 'ASRUSDT', 'ACMUSDT', 'SANTOSUSDT', 'PORTOUSDT', 'LAZIOUSDT', 'ALPINEUSDT', 'SUNUSDT'
]

def send_msg(text):
    """إرسال رسالة لتلغرام مع التحقق من النجاح"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}
        response = requests.post(url, data=payload, timeout=15)
        if response.status_code == 200:
            return True
        else:
            print(f"⚠️ خطأ في تلغرام: {response.text}")
    except Exception as e:
        print(f"⚠️ تعذر الاتصال بتلغرام: {e}")
    return False

def get_data(symbol):
    """جلب بيانات العملة من Yahoo Finance"""
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
    """المحرك الرئيسي للتحليل"""
    print("\n" + "="*70)
    print(f"🚀 بدء المسح الشامل - {datetime.now().strftime('%H:%M:%S')}")
    print("="*70)
    
    # 1. فحص البيتكوين
    print(f"📡 فحص حالة البيتكوين (BTC)...")
    btc = get_data('BTCUSDT')
    if btc is None:
        print(f"❌ تعذر جلب بيانات BTC. سيتم تخطي الدورة.")
        return

    ema50 = btc['Close'].ewm(span=50, adjust=False).mean()
    btc_price = btc['Close'].iloc[-1]
    btc_ema = ema50.iloc[-1]

    if btc_price <= btc_ema:
        print(f"📉 البيتكوين في اتجاه هابط ({btc_price:.0f} < {btc_ema:.0f}). توقف المسح.")
        return
    
    print(f"📈 البيتكوين في اتجاه صاعد. جاري فحص 400 عملة بديلة...")

    # 2. فحص العملات الـ 400
    found = 0
    total = len(SYMBOLS_LIST)
    
    for idx, s in enumerate(SYMBOLS_LIST, 1):
        try:
            df = get_data(s)
            if df is None: continue
            
            # فلتر السيولة البسيط
            vol_usd = df['Volume'].iloc[-1] * df['Close'].iloc[-1]
            if vol_usd < 150000: continue # الحد الأدنى للسيولة
            
            # التحليل الفني
            macd = df.ta.macd(signal_indicators=True)
            ichimoku = df.ta.ichimoku()
            
            if macd is None or ichimoku is None: continue

            cp = df['Close'].iloc[-1]
            isa = ichimoku[0]['ISA_9'].iloc[-1]
            isb = ichimoku[0]['ISB_26'].iloc[-1]

            # شروط الاستراتيجية
            buy_signal = (macd.iloc[-1, 0] > macd.iloc[-1, 1]) and (cp > isa) and (cp > isb)

            if buy_signal:
                msg = f"✅ *إشارة شراء مؤكدة!*\n\n💎 العملة: #{s}\n💵 السعر: ${cp:.4f}\n📊 سيولة الشمعة: ${vol_usd:,.0f}\n🕒 الوقت: {datetime.now().strftime('%H:%M')}"
                send_msg(msg)
                print(f"✨ اكتشاف إشارة: {s}")
                found += 1
        except:
            pass
        
        if idx % 50 == 0:
            print(f"⏳ تم فحص {idx}/{total} عملة...")

    print(f"\n✅ اكتمل المسح. الإشارات المكتشفة: {found}")
    print("="*70)

# --- نقطة انطلاق البوت ---
print("\n" + "="*70)
print("🤖 بوت صيد العملات المشفرة (إصدار الـ 400 عملة)")
print("="*70)

# إرسال إشعار البدء فوراً وتكرار المحاولة إذا فشل
print("📡 جاري محاولة إرسال إشعار البدء لتلغرام...")
start_txt = f"🚀 *تم تشغيل البوت بنجاح!*\n🔍 يراقب الآن: 400 عملة\n⚙️ النظام: MACD + Ichimoku\n📈 الفاصل الزمني: 30 دقيقة"
if send_msg(start_txt):
    print("✅ تم إرسال إشعار البدء لتلغرام.")
else:
    print("⚠️ فشل إرسال الإشعار. تأكد من صحة TOKEN و CHAT_ID.")

print(f"⏱️ البوت سيعمل آلياً كل 30 دقيقة (عند الدقيقة 00 و 30).")

# تشغيل مسح أولي فور التشغيل دون انتظار الدقيقة 00
run_radar()

last_min = -1
while True:
    try:
        now = datetime.now()
        if now.minute in [0, 30] and now.minute != last_min:
            run_radar()
            last_min = now.minute
        
        # طباعة حالة بسيطة كل 10 دقائق لضمان أن السيرفر لم يتجمد
        if now.minute % 10 == 0 and now.second == 0:
            print(f"🕒 نبض النظام: {now.strftime('%H:%M')} - البوت مستمر في المراقبة")
            
        time.sleep(1)
    except Exception as e:
        print(f"❌ خطأ في الحلقة الرئيسية: {e}")
        time.sleep(10)
    
