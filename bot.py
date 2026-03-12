import time, requests, pandas as pd, pandas_ta as ta, yfinance as yf
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
        df = ticker.history(period="3d", interval="30m")
        if not df.empty:
            df = df.rename(columns={'Open':'o', 'High':'h', 'Low':'l', 'Close':'c', 'Volume':'v'})
            return df
    except: pass
    return pd.DataFrame()

def get_full_market_list():
    """قائمة شاملة تضم أغلب عملات بينانس المتاحة على TradingView"""
    return [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT', 'AVAXUSDT', 'DOTUSDT',
        'DOGEUSDT', 'LINKUSDT', 'SHIBUSDT', 'MATICUSDT', 'LTCUSDT', 'UNIUSDT', 'NEARUSDT', 'APTUSDT',
        'OPUSDT', 'ARBUSDT', 'SUIUSDT', 'FETUSDT', 'RNDRUSDT', 'PEPEUSDT', 'FLOKIUSDT', 'INJUSDT',
        'TIAUSDT', 'STXUSDT', 'FILUSDT', 'LDOUSDT', 'ORDIUSDT', 'ICPUSDT', 'TRXUSDT', 'ETCUSDT', 
        'BCHUSDT', 'AAVEUSDT', 'ALGOUSDT', 'EGLDUSDT', 'SANDUSDT', 'MANAUSDT', 'ATOMUSDT', 'VETUSDT',
        'IMXUSDT', 'GRTUSDT', 'SEIUSDT', 'BEAMUSDT', 'GALAUSDT', 'JUPUSDT', 'PYTHUSDT', 'DYMUSDT',
        'PENDLEUSDT', 'AXSUSDT', 'MKRUSDT', 'SNXUSDT', 'ENSUSDT', 'CRVUSDT', 'WLDUSDT', 'ARKMUSDT',
        'IDUSDT', 'PIXELUSDT', 'STRKUSDT', 'PORTALUSDT', 'ENAUSDT', 'WUSDT', 'TNSRUSDT', 'SAGAUSDT',
        'TAOUSDT', 'BBUSDT', 'NOTUSDT', 'IOUSDT', 'ZROUSDT', 'LISTAUSDT', 'DOGSUSDT'
    ]

def run_radar():
    print(f"🚀 [1/4] {datetime.now().strftime('%H:%M')} | بدء المسح الشامل لجميع العملات")
    try:
        # 1. شرط البيتكوين (الأساسي لفلترة السوق)
        print(f"⏳ [2/4] (%25) ... جاري فحص اتجاه البيتكوين")
        btc = get_data('BTCUSDT')
        if btc.empty: return
            
        btc_change = ((btc['c'].iloc[-1] - btc['c'].iloc[-2]) / btc['c'].iloc[-2]) * 100
        # تعديل بسيط ليكون أكثر مرونة مع تذبذب البيتكوين
        if btc_change < -0.15:
            print(f"🛑 اتجاه البيتكوين سلبي ({btc_change:.2f}%). تم إيقاف المسح.")
            return

        # 2. جلب القائمة الضخمة
        all_symbols = get_full_market_list()
        print(f"⏳ [3/4] (%50) ... جاري فلترة {len(all_symbols)} عملة حسب السيولة")

        # 3. الفحص الفني والسيولة
        print(f"⏳ [4/4] (%75) ... تطبيق MACD و Ichimoku")
        found = 0
        for s in all_symbols:
            df = get_data(s)
            
            # التأكد من وجود بيانات كافية وتنظيفها من القيم الفارغة
            if not df.empty and len(df) >= 50:
                df = df.dropna()
                
                # فلتر السيولة: تداول آخر شمعة > 200,000$
                volume_usd = df['v'].iloc[-1] * df['c'].iloc[-1]
                if volume_usd < 200000: 
                    continue
                
                try:
                    # حساب المؤشرات الفنية
                    m = df.ta.macd(close='c')
                    # استخدام 'D' كبيرة لتجنب تحذيرات Pandas في السجلات
                    ic = df.ta.ichimoku(high='h', low='l', close='c')[0]
                    
                    if m is None or ic is None: continue
                    
                    cp = df['c'].iloc[-1]
                    
                    # شرط الدخول: تقاطع MACD + السعر فوق السحابة
                    if m.iloc[-1][0] > m.iloc[-1][2] and cp > ic['ISA_9'].iloc[-1] and cp > ic['ISB_26'].iloc[-1]:
                        send_msg(f"🚀 **إشارة دخول قوية: {s}**\n💰 السعر: {cp:.4f}\n📊 سيولة الشمعة: ${volume_usd:,.0f}\n📈 اتجاه BTC: {btc_change:.2f}%")
                        found += 1
                except:
                    # في حال حدوث خطأ في عملة واحدة، يكمل البوت فحص الباقي
                    continue
            
            time.sleep(0.1) 
            
        print(f"🏁 اكتمل المسح الشامل. تم العثور على {found} فرصة.")
    except Exception as e:
        print(f"⚠️ خطأ عام في الدورة: {e}")

# رسالة تأكيد البدء
send_msg("🤖 رادار المسح الشامل (النسخة المستقرة) بدأ العمل الآن.")

# --- نظام النبض (Pulse) ثابت لضمان عمل السيرفر ---
last_pulse = -1
while True:
    now = datetime.now()
    if now.minute % 5 == 0 and now.minute != last_pulse:
        print(f"🕒 نبض السيرفر: {now.strftime('%H:%M')}")
        last_pulse = now.minute
        
        # تنفيذ التحليل عند الدقيقة 00 و 30
        if now.minute in [0, 30]:
            run_radar()
            
    time.sleep(1)
