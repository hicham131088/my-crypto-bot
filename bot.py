import time
import requests
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

TOKEN = '7900130533:AAFP7ZYnrdUOEf-8E1rQIKWdgRfD8oJZSuw'
CHAT_ID = '6424409099'

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}, 
                      timeout=15)
    except:
        pass

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

def get_all_symbols():
    """جلب جميع العملات من Binance"""
    try:
        print("   ⏳ جاري جلب العملات من Binance...")
        response = requests.get('https://api.binance.com/api/v3/exchangeInfo', timeout=30)
        data = response.json()
        symbols = [s['symbol'] for s in data['symbols'] 
                   if s['status'] == 'TRADING' and s['quoteAsset'] == 'USDT']
        print(f"   ✅ تم جلب {len(symbols)} عملة")
        return sorted(symbols)
    except Exception as e:
        print(f"   ❌ خطأ: {e}")
        return []

def run_radar(symbols):
    print("\n" + "="*70)
    print(f"📊 بدء التحليل - {datetime.now().strftime('%H:%M:%S')}")
    print("="*70)
    
    # مرحلة 1: البيتكوين
    print(f"\n📈 [مرحلة 1] فحص البيتكوين...")
    btc = get_data('BTCUSDT')
    if not btc:
        print(f"   ❌ بيانات BTC غير متاحة")
        print(f"✋ انهاء التحليل\n")
        return
    
    ema50 = btc['Close'].ewm(span=50, adjust=False).mean()
    if btc['Close'].iloc[-1] <= ema50.iloc[-1]:
        print(f"   ❌ السوق هابط - لا مسح الآن")
        print(f"✋ انهاء التحليل\n")
        return
    
    print(f"   ✅ الزخم صاعد - متابعة المسح")
    
    # مرحلة 2: السيولة
    print(f"\n💧 [مرحلة 2] فلترة السيولة...")
    qualified = []
    for idx, s in enumerate(symbols, 1):
        try:
            df = get_data(s)
            if df is not None:
                vol = df['Volume'].iloc[-1] * df['Close'].iloc[-1]
                if vol >= 200000:
                    qualified.append(s)
        except:
            pass
        if idx % 50 == 0:
            print(f"   📊 {idx}/{len(symbols)} ({100*idx//len(symbols)}%)")
        time.sleep(0.02)
    
    print(f"   ✅ عملات مؤهلة: {len(qualified)}")
    if not qualified:
        print(f"✋ انهاء التحليل\n")
        return
    
    # مرحلة 3: التحليل الفني
    print(f"\n🔬 [مرحلة 3] التحليل الفني...")
    found = 0
    for idx, s in enumerate(qualified, 1):
        try:
            df = get_data(s)
            if df is None:
                continue
            
            macd = df.ta.macd(signal_indicators=True)
            ichimoku = df.ta.ichimoku()
            
            if macd is None or macd.empty or not ichimoku or len(ichimoku[0]) == 0:
                continue
            
            cp = df['Close'].iloc[-1]
            isa = ichimoku[0]['ISA_9'].iloc[-1]
            isb = ichimoku[0]['ISB_26'].iloc[-1]
            
            if (len(macd) > 0 and 
                macd.iloc[-1, 0] > macd.iloc[-1, 1] and 
                cp > isa and cp > isb):
                
                vol_usd = df['Volume'].iloc[-1] * cp
                print(f"   ✅ {s} | ${cp:.4f} | ${vol_usd:,.0f}")
                send_msg(f"🚀 **{s}**\n💰 ${cp:.4f}\n📊 ${vol_usd:,.0f}")
                found += 1
        except:
            pass
        
        if idx % 20 == 0:
            print(f"   ⏳ {idx}/{len(qualified)} ({100*idx//len(qualified)}%) | إشارات: {found}")
        time.sleep(0.05)
    
    print(f"\n{'='*70}")
    print(f"✅ انتهى التحليل")
    print(f"{'='*70}")
    print(f"📌 النتائج: {len(qualified)} عملة | {found} إشارة")
    print(f"{'='*70}\n")

# البدء
print("\n" + "="*70)
print("📡 البوت جاهز للعمل")
print("="*70)

symbols = get_all_symbols()
if not symbols:
    print("❌ فشل في جلب العملات!")
    exit()

send_msg(f"📡 *البوت نشِط* ✅\n*عملات: {len(symbols)}*")
print(f"⏰ المسح: دقائق 00 و 30")
print("="*70)

last_pulse = -1
while True:
    try:
        now = datetime.now()
        minute = now.minute
        
        if minute % 5 == 0 and minute != last_pulse:
            last_pulse = minute
            print(f"\n🔔 {now.strftime('%H:%M:%S')} - البوت يعمل")
            
            if minute in [0, 30]:
                run_radar(symbols)
        
        time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 توقف")
        break
    except Exception as e:
        print(f"⚠️ {e}")
        time.sleep(5)            if (len(macd) > 0 and 
                macd.iloc[-1, 0] > macd.iloc[-1, 1] and 
                cp > isa and cp > isb):
                
                vol_usd = df['Volume'].iloc[-1] * cp
                print(f"   ✅ {s} | ${cp:.4f} | ${vol_usd:,.0f}")
                send_msg(f"🚀 **{s}**\n💰 ${cp:.4f}\n📊 ${vol_usd:,.0f}")
                found += 1
        except:
            pass
        
        if idx % 20 == 0:
            print(f"   ⏳ {idx}/{len(qualified)} ({100*idx//len(qualified)}%) | إشارات: {found}")
        time.sleep(0.05)
    
    print(f"\n{'='*70}")
    print(f"✅ انتهى التحليل")
    print(f"{'='*70}")
    print(f"📌 النتائج: {len(qualified)} عملة | {found} إشارة")
    print(f"{'='*70}\n")

# البدء
print("\n" + "="*70)
print("📡 البوت جاهز للعمل")
print("="*70)

symbols = get_all_symbols()
if not symbols:
    print("❌ فشل في جلب العملات!")
    exit()

send_msg(f"📡 *البوت نشِط* ✅\n*عملات: {len(symbols)}*")
print(f"⏰ المسح: دقائق 00 و 30")
print("="*70)

last_pulse = -1
while True:
    try:
        now = datetime.now()
        minute = now.minute
        
        if minute % 5 == 0 and minute != last_pulse:
            last_pulse = minute
            print(f"\n🔔 {now.strftime('%H:%M:%S')} - البوت يعمل")
            
            if minute in [0, 30]:
                run_radar(symbols)
        
        time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 توقف")
        break
    except Exception as e:
        print(f"⚠️ {e}")
        time.sleep(5)
