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
        print(f"   ⚠️ خطأ إرسال Telegram: {e}")

def get_data(symbol):
    try:
        yf_symbol = symbol.replace('USDT', '-USD')
        ticker = yf.Ticker(yf_symbol)
        df = ticker.history(period="5d", interval="30m")
        if not df.empty:
            return df
        return pd.DataFrame()
    except Exception as e:
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
    print("\n" + "="*70)
    print(f"📊 بدء التحليل - {datetime.now().strftime('%H:%M:%S')}")
    print("="*70)
    
    try:
        # ═══════════════════════════════════════
        # 🔍 مرحلة 1: فحص البيتكوين
        # ═══════════════════════════════════════
        print(f"\n📈 [مرحلة 1] فحص البيتكوين (شرط أساسي)...")
        btc = get_data('BTCUSDT')
        
        if btc.empty or len(btc) < 50:
            print(f"   ❌ السبب: بيانات البيتكوين غير كافية (عدد الشمعات: {len(btc)})")
            print(f"✋ انهاء التحليل\n")
            return
        
        # حساب EMA 50 للبيتكوين
        ema50 = btc['Close'].ewm(span=50, adjust=False).mean()
        current_btc = btc['Close'].iloc[-1]
        last_ema50 = ema50.iloc[-1]
        
        # شرط الزخم الصاعد
        if current_btc > last_ema50:
            print(f"   ✅ السعر: ${current_btc:,.2f} > EMA50: ${last_ema50:,.2f}")
            print(f"   ✅ النتيجة: الزخم صاعد ✓")
        else:
            print(f"   ❌ السعر: ${current_btc:,.2f} < EMA50: ${last_ema50:,.2f}")
            print(f"   ❌ السبب: السوق الآن في حالة هبوطية")
            print(f"✋ انهاء التحليل\n")
            return

        # ═══════════════════════════════════════
        # 🔄 مرحلة 2: تحليل السيولة
        # ═══════════════════════════════════════
        print(f"\n💧 [مرحلة 2] تحليل السيولة (تصفية العملات الضعيفة)...")
        all_symbols = get_full_market_list()
        qualified_symbols = []
        
        for idx, s in enumerate(all_symbols, 1):
            try:
                df = get_data(s)
                if df.empty or len(df) < 50:
                    continue
                
                # فلتر السيولة
                volume_usd = df['Volume'].iloc[-1] * df['Close'].iloc[-1]
                if volume_usd >= 200000:
                    qualified_symbols.append(s)
                
            except:
                continue
            
            # طباعة نسبة التقدم كل 5 عملات
            if idx % 5 == 0:
                progress = (idx / len(all_symbols)) * 100
                print(f"   📊 التقدم: {idx}/{len(all_symbols)} ({progress:.1f}%)")
            
            time.sleep(0.1)
        
        # نتيجة تحليل السيولة
        progress = 100
        print(f"   📊 التقدم: {len(all_symbols)}/{len(all_symbols)} (100%)")
        print(f"\n   ✅ العملات المؤهلة: {len(qualified_symbols)} من {len(all_symbols)}")
        
        if len(qualified_symbols) == 0:
            print(f"   ⚠️ لم نجد أي عملات تحقق معايير السيولة")
            print(f"✋ انهاء التحليل\n")
            return
        else:
            print(f"   📌 العملات المؤهلة: {', '.join(qualified_symbols[:5])}..." if len(qualified_symbols) > 5 else f"   📌 العملات المؤهلة: {', '.join(qualified_symbols)}")

        # ═══════════════════════════════════════
        # 📊 مرحلة 3: التحليل الفني
        # ═══════════════════════════════════════
        print(f"\n🔬 [مرحلة 3] التحليل الفني (MACD + Ichimoku)...")
        found = 0
        errors = 0
        
        for idx, s in enumerate(qualified_symbols, 1):
            try:
                df = get_data(s)
                if df.empty or len(df) < 50:
                    continue
                
                df = df.dropna()
                if len(df) < 50:
                    continue
                
                # التحليل الفني
                try:
                    # MACD
                    macd = df.ta.macd(signal_indicators=True)
                    if macd is None or macd.empty:
                        continue
                    
                    # Ichimoku
                    ichimoku = df.ta.ichimoku(tenkan=9, kijun=26, senkou_b=52, senkou_span=26, chikou=26)
                    
                    cp = df['Close'].iloc[-1]
                    
                    if ichimoku and len(ichimoku[0]) > 0:
                        isa = ichimoku[0]['ISA_9'].iloc[-1]
                        isb = ichimoku[0]['ISB_26'].iloc[-1]
                        
                        # تقاطع إيجابي + فوق السحابة
                        if (len(macd) > 0 and 
                            macd.iloc[-1, 0] > macd.iloc[-1, 1] and 
                            cp > isa and cp > isb):
                            
                            volume_usd = df['Volume'].iloc[-1] * df['Close'].iloc[-1]
                            print(f"   ✅ {s} | السعر: ${cp:.4f} | الحجم: ${volume_usd:,.0f}")
                            
                            send_msg(f"🚀 **إشارة دخول: {s}**\n💰 السعر: ${cp:.4f}\n📊 الحجم: ${volume_usd:,.0f}\n✅ إشارة صاعدة قوية")
                            found += 1
                
                except Exception as e:
                    errors += 1
                    continue
            
            except Exception as e:
                errors += 1
                continue
            
            # نسبة التقدم
            progress = (idx / len(qualified_symbols)) * 100
            print(f"   ⏳ التقدم: {idx}/{len(qualified_symbols)} ({progress:.1f}%) | الإشارات: {found}")
            
            time.sleep(0.2)
        
        # ═══════════════════════════════════════
        # 📋 النتيجة النهائية
        # ═══════════════════════════════════════
        print(f"\n{'='*70}")
        print(f"✅ انتهى التحليل")
        print(f"{'='*70}")
        print(f"📌 ملخص النتائج:")
        print(f"   • العملات المفحوصة: {len(qualified_symbols)}")
        print(f"   • الإشارات المكتشفة: {found}")
        if found > 0:
            print(f"   • النسبة: {(found/len(qualified_symbols)*100):.1f}%")
        else:
            print(f"   ⚠️ لم يتم العثور على إشارات في هذا المسح")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"❌ خطأ عام في التحليل: {e}")
        print(f"✋ انهاء التحليل\n")

# البدء
print("\n" + "="*70)
send_msg("📡 *البوت نشِط الآن* ✅\n*النسخة المحسّنة مع Logging متقدم*")
print("📡 البوت جاهز للعمل")
print(f"⏰ المسح سيبدأ عند الدقائق: 00 و 30 من كل ساعة")
print("="*70)

last_pulse = -1
while True:
    try:
        now = datetime.now()
        current_minute = now.minute
        
        # نبض كل 5 دقائق
        if current_minute % 5 == 0 and current_minute != last_pulse:
            last_pulse = current_minute
            print(f"\n🔔 نبض النظام: {now.strftime('%H:%M:%S')} - النظام يعمل بشكل طبيعي")
            
            # مسح فني عند الدقائق 0 و 30
            if current_minute in [0, 30]:
                run_radar()
        
        time.sleep(1)
    
    except KeyboardInterrupt:
        print(f"\n{'='*70}")
        print("🛑 تم إيقاف البوت من قبل المستخدم")
        print("="*70)
        break
    except Exception as e:
        print(f"⚠️ خطأ في الحلقة الرئيسية: {e}")
        time.sleep(5)                
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
