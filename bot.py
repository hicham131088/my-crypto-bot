import time
import requests
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import warnings
from datetime import datetime

# إخفاء التحذيرات الزائدة
warnings.filterwarnings('ignore')

# --- الإعدادات الأساسية ---
TOKEN = '7900130533:AAFP7ZYnrdUOEf-8E1rQIKWdgRfD8oJZSuw'
CHAT_ID = '6424409099'

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}, 
                      timeout=15)
    except Exception as e:
        print(f"⚠️ خطأ إرسال: {e}")

def get_data(symbol):
    try:
        yf_symbol = symbol.replace('USDT', '-USD')
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period="5d", interval="30m")
        if not df.empty:
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ خطأ جلب البيانات ({symbol}): {e}")
        return pd.DataFrame()

def get_full_market_list():
    return [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT', 'AVAXUSDT', 'DOTUSDT',
        'DOGEUSDT', 'LINKUSDT', 'SHIBUSDT', 'MATICUSDT', 'LTCUSDT', 'UNIUSDT', 'NEARUSDT', 'APTUSDT',
        'OPUSDT', 'ARBUSDT', 'SUIUSDT', 'FETUSDT', 'RNDRUSDT', 'PEPEUSDT', 'FLOKIUSDT', 'INJUSDT',
        'TIAUSDT', 'STXUSDT', 'FILUSDT', 'LDOUSDT', 'ORDIUSDT', 'ICPUSDT', 'TRXUSDT', 'ETCUSDT', 
        'BCHUSDT', 'AAVEUSDT', 'ALGOUSDT', 'EGLDUSDT', 'SANDUSDT', 'MANAUSDT', 'ATOMUSDT', 'VETUSDT'
    ]

def run_radar():
    print(f"🚀 [{datetime.now().strftime('%H:%M')}] بدء المسح الشامل")
    try:
        btc = get_data('BTCUSDT')
        if btc.empty or len(btc) < 50: 
            print("❌ بيانات البيتكوين غير كافية")
            return
        
        # حساب EMA 50 للبيتكوين
        ema50 = btc['Close'].ewm(span=50, adjust=False).mean()
        current_btc = btc['Close'].iloc[-1]
        last_ema50 = ema50.iloc[-1]
        
        # شرط الزخم الصاعد
        if current_btc > last_ema50:
            print(f"✅ زخم صاعد (BTC: ${current_btc:,.0f} > EMA: ${last_ema50:,.0f})")
        else:
            print(f"🛑 زخم هابط - لا مسح الآن")
            return

        all_symbols = get_full_market_list()
        found = 0
        errors = 0
        
        for s in all_symbols:
            try:
                df = get_data(s)
                if df.empty or len(df) < 50:
                    continue
                    
                df = df.dropna()
                if len(df) < 50:
                    continue
                
                # فلتر السيولة
                volume_usd = df['Volume'].iloc[-1] * df['Close'].iloc[-1]
                if volume_usd < 200000:
                    continue
                
                # التحليل الفني
                try:
                    # MACD - بدون تحذيرات
                    macd = df.ta.macd(signal_indicators=True)
                    if macd is None or macd.empty:
                        continue
                    
                    # Ichimoku - بدون تحذيرات deprecation
                    ichimoku = df.ta.ichimoku(tenkan=9, kijun=26, senkou_b=52, senkou_span=26, chikou=26)
                    
                    cp = df['Close'].iloc[-1]
                    
                    if ichimoku and len(ichimoku[0]) > 0:
                        isa = ichimoku[0]['ISA_9'].iloc[-1]
                        isb = ichimoku[0]['ISB_26'].iloc[-1]
                        
                        # تقاطع إيجابي + فوق السحابة
                        if (len(macd) > 0 and 
                            macd.iloc[-1, 0] > macd.iloc[-1, 1] and 
                            cp > isa and cp > isb):
                            
                            send_msg(f"🚀 **إشارة دخول: {s}**\n💰 السعر: ${cp:.4f}\n📊 الحجم: ${volume_usd:,.0f}\n✅ إشارة صاعدة قوية")
                            found += 1
                            print(f"   ✅ {s} - إشارة قوية!")
                
                except Exception as e:
                    errors += 1
                    continue
                
                time.sleep(0.2)
            
            except Exception as e:
                errors += 1
                continue
        
        print(f"✅ انتهى المسح | إشارات: {found} | أخطاء: {errors}")
        
    except Exception as e:
        print(f"❌ خطأ عام: {e}")

# البدء
print("="*50)
send_msg("📡 *البوت نشِط الآن*\n✅ النسخة المحسّنة")
print("="*50)

last_pulse = -1
while True:
    try:
        now = datetime.now()
        current_minute = now.minute
        
        # نبض كل دقيقة
        if current_minute != last_pulse:
            last_pulse = current_minute
            if current_minute % 5 == 0:
                print(f"🔔 [{now.strftime('%H:%M:%S')}] نبض النظام")
                if current_minute in [0, 30]:
                    run_radar()
        
        time.sleep(1)
    
    except KeyboardInterrupt:
        print("🛑 البوت تم إيقافه")
        break
    except Exception as e:
        print(f"⚠️ خطأ في الحلقة الرئيسية: {e}")
        time.sleep(5)
