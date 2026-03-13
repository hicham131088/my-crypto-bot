# -*- coding: utf-8 -*-
import time
import requests
import pandas as pd
import pandas_ta as ta
import yfinance as yf
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# الإعدادات
TOKEN = '7900130533:AAFP7ZYnrdUOEf-8E1rQIKWdgRfD8oJZSuw'
CHAT_ID = '6424409099'

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}
        response = requests.post(url, data=payload, timeout=15)
        if response.status_code != 200:
            print(f"⚠️ فشل إرسال رسالة تلغرام: {response.text}")
    except Exception as e:
        print(f"⚠️ خطأ في اتصال تلغرام: {e}")

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
        print("🔍 جاري جلب قائمة العملات من Binance...")
        response = requests.get('https://api.binance.com/api/v3/exchangeInfo', timeout=30)
        data = response.json()
        symbols = [s['symbol'] for s in data['symbols'] if s['status'] == 'TRADING' and s['quoteAsset'] == 'USDT']
        print(f"✅ تم تحميل {len(symbols)} عملة بنجاح")
        return sorted(symbols)
    except Exception as e:
        print(f"❌ فشل جلب العملات: {e}")
        return []

def run_radar(symbols):
    print("\n" + "="*70)
    print(f"🚀 بدء عملية التحليل - {datetime.now().strftime('%H:%M:%S')}")
    print("="*70)
    
    print(f"\n1️⃣ فحص اتجاه البيتكوين (BTC)...")
    btc = get_data('BTCUSDT')
    if btc is None:
        print(f"❌ خطأ: تعذر الحصول على بيانات البيتكوين")
        return

    ema50 = btc['Close'].ewm(span=50, adjust=False).mean()
    btc_price = btc['Close'].iloc[-1]
    btc_ema = ema50.iloc[-1]

    if btc_price <= btc_ema:
        print(f"📉 هبوط: السعر الحالي ({btc_price:.0f}) تحت المتوسط ({btc_ema:.0f})")
        print(f"🛑 السوق غير مناسب حالياً - توقف المسح")
        return
    
    print(f"📈 صعود: السعر الحالي ({btc_price:.0f}) فوق المتوسط ({btc_ema:.0f})")
    print(f"🔄 متابعة المسح للعملات البديلة...")

    print(f"\n2️⃣ مرحلة فلتر السيولة (أكثر من 200 ألف دولار)...")
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
            print(f"⏳ التقدم: {idx}/{len(symbols)} ({pct}%)")
            time.sleep(0.02)

    print(f"✅ نجحت {len(qualified)} عملة في اجتياز فلتر السيولة")

    if not qualified:
        print(f"❌ لم يتم العثور على عملات مطابقة")
        return

    print(f"\n3️⃣ التحليل الفني (MACD + Ichimoku)...")
    found = 0
    for idx, s in enumerate(qualified, 1):
        try:
            df = get_data(s)
            if df is None: continue
            
            macd = df.ta.macd(signal_indicators=True)
            ichimoku = df.ta.ichimoku()
            
            if macd is None or macd.empty: continue
            if not ichimoku or len(ichimoku[0]) == 0: continue

            cp = df['Close'].iloc[-1]
            isa = ichimoku[0]['ISA_9'].iloc[-1]
            isb = ichimoku[0]['ISB_26'].iloc[-1]

            # إشارة شراء: MACD إيجابي والسعر فوق سحابة إيشيموكو
            signal_macd = macd.iloc[-1, 0] > macd.iloc[-1, 1]
            signal_cloud = (cp > isa) and (cp > isb)

            if signal_macd and signal_cloud:
                vol_usd = df['Volume'].iloc[-1] * cp
                msg = f"🔔 *إشارة شراء جديدة!* 🔔\n\n💰 العملة: #{s}\n💵 السعر: ${cp:.4f}\n📊 السيولة: ${vol_usd:,.0f}"
                print(f"✨ تم العثور على إشارة: {s}")
                send_msg(msg)
                found += 1
        except:
            pass
            
        if idx % 20 == 0:
            pct = 100*idx//len(qualified)
            print(f"⏳ التقدم: {idx}/{len(qualified)} ({pct}%) | الإشارات المكتشفة: {found}")
            time.sleep(0.05)

    print(f"\n{'='*70}")
    print(f"🏁 اكتمل التحليل بنجاح")
    print(f"{'='*70}")
    print(f"📊 الملخص:")
    print(f"🔹 إجمالي العملات: {len(symbols)}")
    print(f"🔹 العملات المؤهلة: {len(qualified)}")
    print(f"🔹 الإشارات المرسلة: {found}")
    print(f"{'='*70}\n")

# تشغيل البوت
print("\n" + "="*70)
print("🤖 بوت العملات المشفرة - كاشف الإشارات التلقائي")
print("="*70)

all_symbols = get_all_symbols()
if not all_symbols:
    print("❌ خطأ حرج: فشل تحميل قائمة العملات!")
    exit()

# إرسال رسالة تنبيه ببدء العمل
start_msg = f"🚀 *تم تفعيل البوت بنجاح!*\n📦 عدد العملات المراقبة: {len(all_symbols)}\n🕒 البوت سيبدأ المسح كل 30 دقيقة."
send_msg(start_msg)

print(f"✅ البوت جاهز للعمل")
print(f"📡 عدد العملات: {len(all_symbols)}")
print(f"⏱️ المواعيد: المسح سيبدأ عند الدقيقة 00 و 30 من كل ساعة")
print("="*70)

last_scan_minute = -1
while True:
    try:
        now = datetime.now()
        minute = now.minute
        
        # طباعة نبض كل 5 دقائق للتأكد أن البوت يعمل في الـ Logs
        if minute % 5 == 0 and minute != last_scan_minute:
            print(f"⏱️ نبض البوت: {now.strftime('%H:%M:%S')} - النظام يعمل بشكل طبيعي")
            last_scan_minute = minute

        # تنفيذ المسح عند رأس الساعة ومنتصفها
        if minute in [0, 30] and minute != last_scan_minute:
            run_radar(all_symbols)
            last_scan_minute = minute
            
        time.sleep(30) # فحص الوقت كل 30 ثانية
        
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف البوت يدوياً")
        break
    except Exception as e:
        print(f"⚠️ خطأ غير متوقع: {e}")
        time.sleep(10)
