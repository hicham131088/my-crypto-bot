# -*- coding: utf-8 -*-
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
    try:
        print("   جاري جلب العملات من بينانس...")
        response = requests.get('https://api.binance.com/api/v3/exchangeInfo', timeout=30)
        data = response.json()
        symbols = [s['symbol'] for s in data['symbols'] 
                   if s['status'] == 'TRADING' and s['quoteAsset'] == 'USDT']
        print(f"   تم: تحميل {len(symbols)} عملة")
        return sorted(symbols)
    except:
        return []

def run_radar(symbols):
    print("\n" + "="*70)
    print(f"بدء التحليل - {datetime.now().strftime('%H:%M:%S')}")
    print("="*70)
    
    print(f"\nالمرحلة 1: فحص زخم البيتكوين...")
    btc = get_data('BTCUSDT')
    if not btc:
        print(f"   خطأ: بيانات البيتكوين غير متوفرة")
        print(f"توقف\n")
        return
    
    ema50 = btc['Close'].ewm(span=50, adjust=False).mean()
    btc_price = btc['Close'].iloc[-1]
    btc_ema = ema50.iloc[-1]
    
    if btc_price <= btc_ema:
        print(f"   هبوط: السعر {btc_price:.0f} < متوسط متحرك 50 {btc_ema:.0f}")
        print(f"   السوق في حالة هبوط - سيتم إيقاف المسح")
        print(f"توقف\n")
        return
    
    print(f"   صعود: السعر {btc_price:.0f} > متوسط متحرك 50 {btc_ema:.0f}")
    print(f"   متابعة المسح...")
    
    print(f"\nالمرحلة 2: فلتر السيولة (الحد الأدنى 200 ألف دولار)...")
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
            pct = 100*idx//len(symbols)
            print(f"   التقدم: {idx}/{len(symbols)} ({pct}%)")
        time.sleep(0.02)
    
    print(f"   تم: تأهيل {len(qualified)} عملة")
    if not qualified:
        print(f"   لم يتم العثور على عملات مؤهلة")
        print(f"توقف\n")
        return
    
    print(f"\nالمرحلة 3: التحليل الفني (MACD + Ichimoku)...")
    found = 0
    for idx, s in enumerate(qualified, 1):
        try:
            df = get_data(s)
            if df is None:
                continue
            
            macd = df.ta.macd(signal_indicators=True)
            ichimoku = df.ta.ichimoku()
            
            if macd is None or macd.empty:
                continue
            if not ichimoku or len(ichimoku[0]) == 0:
                continue
            
            cp = df['Close'].iloc[-1]
            isa = ichimoku[0]['ISA_9'].iloc[-1]
            isb = ichimoku[0]['ISB_26'].iloc[-1]
            
            signal_macd = macd.iloc[-1, 0] > macd.iloc[-1, 1]
            signal_cloud = (cp > isa) and (cp > isb)
            
            if signal_macd and signal_cloud:
                vol_usd = df['Volume'].iloc[-1] * cp
                print(f"   ✅ إشارة: {s} | السعر: ${cp:.4f} | الحجم: ${vol_usd:,.0f}")
                send_msg(f"🚀 **إشارة دخول: {s}**\n💰 السعر: ${cp:.4f}\n📊 الحجم: ${vol_usd:,.0f}\n✅ إشارة قوية صاعدة")
                found += 1
        except:
            pass
        
        if idx % 20 == 0:
            pct = 100*idx//len(qualified)
            print(f"   ⏳ التقدم: {idx}/{len(qualified)} ({pct}%) | الإشارات: {found}")
        time.sleep(0.05)
    
    print(f"\n{'='*70}")
    print(f"✅ انتهى التحليل")
    print(f"{'='*70}")
    print(f"📌 ملخص النتائج:")
    print(f"   • إجمالي العملات: {len(symbols)}")
    print(f"   • العملات المفحوصة: {len(qualified)}")
    print(f"   • الإشارات المكتشفة: {found}")
    if found > 0:
        pct = 100*found//len(qualified)
        print(f"   • نسبة النجاح: {pct}%")
    else:
        print(f"   ⚠️ لم يتم العثور على إشارات في هذا المسح")
    print(f"{'='*70}\n")

# --- بدء التشغيل ---
print("\n" + "="*70)
print("🤖 بوت الكريبتو - كاشف الإشارات التلقائي")
print("="*70)

symbols = get_all_symbols()
if not symbols:
    print("❌ خطأ: فشل في تحميل العملات!")
    exit()

send_msg(f"🤖 *البوت نشِط الآن* ✅\n📊 عدد العملات: {len(symbols)}\n⏰ المسح في الدقائق 00 و 30")
print(f"\n✅ البوت جاهز للعمل")
print(f"   • عدد العملات المحملة: {len(symbols)}")
print(f"   • جدول المسح: الدقيقة 00 و 30 من كل ساعة")
print(f"   • الحالة: 🟢 جاهز للعمل")
print("="*70)

last_pulse = -1
while True:
    try:
        now = datetime.now()
        minute = now.minute
        
        if minute % 5 == 0 and minute != last_pulse:
            last_pulse = minute
            print(f"\n🔔 نبض النظام: {now.strftime('%H:%M:%S')} - البوت يعمل بشكل طبيعي")
            
            if minute in [0, 30]:
                run_radar(symbols)
        
        time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("🛑 تم إيقاف البوت")
        print("="*70)
        break
    except Exception as e:
        print(f"⚠️ خطأ: {e}")
        time.sleep(5)
