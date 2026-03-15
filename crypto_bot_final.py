# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║         🤖 بوت التداول التلقائي الذكي - Crypto Auto Trading Bot       ║
║                    نسخة محسّنة مع طباعات عربية مفصلة                   ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import time
import requests
import pandas as pd
import pandas_ta as ta
import json
import os
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException
import warnings

warnings.filterwarnings('ignore')

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                        ⚙️  المتغيرات القابلة للتعديل                    ║
# ╚════════════════════════════════════════════════════════════════════════════╝

# ━━━━━━━━━━━━━━━━━━━━━━━━ بيانات التوصيل ━━━━━━━━━━━━━━━━━━━━━━━━
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', 'YOUR_TOKEN')
CHAT_ID = os.getenv('CHAT_ID', 'YOUR_CHAT_ID')
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', 'YOUR_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', 'YOUR_SECRET')

# ━━━━━━━━━━━━━━━━━━━━━━━━ إعدادات الشمعات والتوقيت ━━━━━━━━━━━━━━━━━━━━━━━━
CANDLE_INTERVAL = '30m'              # فترة الشمعة (30 دقيقة)
SCAN_INTERVAL = 5                    # النبض كل 5 دقائق (التحليل والتداول عند إغلاق الشمعة)
NUM_CANDLES = 100                    # عدد الشمعات التاريخية المطلوبة للتحليل

# ━━━━━━━━━━━━━━━━━━━━━━━━ إعدادات التداول ━━━━━━━━━━━━━━━━━━━━━━━━
TRADING_AMOUNT = 10                  # المبلغ بالدولار لكل صفقة
MIN_WALLET_BALANCE = 5               # الحد الأدنى للعملة في المحفظة (دولار)
MIN_VOLUME_USD = 150000              # الحد الأدنى لحجم التداول (دولار)
VOLUME_MULTIPLIER = 1.2              # العملة يجب أن تكون حجمها أعلى من المتوسط بـ X مرة

# ━━━━━━━━━━━━━━━━━━━━━━━━ إعدادات الاستراتيجية ━━━━━━━━━━━━━━━━━━━━━━━━
SL_ATR_MULTIPLIER = 1.2              # Stop Loss = سعر الشراء - (1.2 * ATR)
TP_ATR_MULTIPLIER = 2.4              # Take Profit = سعر الشراء + (2.4 * ATR)
RSI_OVERBOUGHT = 70                  # مستوى التشبع الشرائي
ENABLE_TRAILING_STOP = True          # تفعيل ملاحقة الربح
TRAILING_TP_ATR = 2.4                # TP الجديد = آخر TP + (2.4 * ATR)

# ━━━━━━━━━━━━━━━━━━━━━━━━ العملات المحظورة ━━━━━━━━━━━━━━━━━━━━━━━━
BLACKLIST_SYMBOLS = [
    'BNBUSDT', 'BUSDUSDT', 'USDCUSDT', 'DAIUSDT', 'USDT', 'FDUSDUSDT',
]

# ━━━━━━━━━━━━━━━━━━━━━━━━ ملفات التتبع ━━━━━━━━━━━━━━━━━━━━━━━━
PORTFOLIO_FILE = 'portfolio.json'
HISTORY_FILE = 'trade_history.json'
LAST_SIGNAL_FILE = 'last_signals.json'

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                        🔌 تهيئة الاتصالات                               ║
# ╚════════════════════════════════════════════════════════════════════════════╝

try:
    binance_client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
    binance_client.get_account()
    print("✅ تم الاتصال ببينانص بنجاح!")
except Exception as e:
    print(f"❌ خطأ في الاتصال ببينانص: {e}")
    exit(1)

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                        📁 وظائف إدارة الملفات                            ║
# ╚════════════════════════════════════════════════════════════════════════════╝

def load_portfolio():
    """تحميل بيانات المحفظة"""
    if os.path.exists(PORTFOLIO_FILE):
        try:
            with open(PORTFOLIO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_portfolio(portfolio):
    """حفظ بيانات المحفظة"""
    with open(PORTFOLIO_FILE, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=2)

def load_history():
    """تحميل سجل الصفقات"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    """حفظ سجل الصفقات"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def add_to_history(symbol, trade_type, quantity, price, profit_loss=None, tp=None, sl=None):
    """إضافة صفقة إلى السجل"""
    history = load_history()
    trade = {
        'التاريخ': datetime.now().isoformat(),
        'العملة': symbol,
        'النوع': trade_type,
        'الكمية': quantity,
        'السعر': price,
        'المبلغ_دولار': quantity * price,
        'الربح_الخسارة_نسبة': profit_loss,
        'TP': tp,
        'SL': sl
    }
    history.append(trade)
    save_history(history)
    return trade

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                        📡 وظائف التلغرام                                ║
# ╚════════════════════════════════════════════════════════════════════════════╝

def send_msg(text, symbol=None):
    """إرسال رسالة إلى التلغرام"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}
        
        if symbol:
            base_coin = symbol.replace('USDT', '')
            binance_url = f"https://www.binance.com/en/trade/{base_coin}_USDT"
            keyboard = {
                "inline_keyboard": [
                    [{"text": f"📈 افتح {symbol} في بينانس", "url": binance_url}]
                ]
            }
            payload['reply_markup'] = json.dumps(keyboard)
        
        response = requests.post(url, data=payload, timeout=15)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ خطأ في إرسال الرسالة: {e}")
        return False

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                        💰 وظائف إدارة المحفظة                            ║
# ╚════════════════════════════════════════════════════════════════════════════╝

def get_all_trading_symbols():
    """جلب قائمة جميع العملات من Binance"""
    try:
        print("📥 جاري جلب قائمة العملات من Binance...")
        exchange_info = binance_client.get_exchange_info()
        symbols = []
        
        for symbol in exchange_info['symbols']:
            if symbol['quoteAsset'] == 'USDT' and symbol['status'] == 'TRADING':
                symbols.append(symbol['symbol'])
        
        symbols = [s for s in symbols if s not in BLACKLIST_SYMBOLS]
        print(f"✅ تم جلب {len(symbols)} عملة من Binance")
        return symbols
    except Exception as e:
        print(f"❌ خطأ في جلب قائمة العملات: {e}")
        return []

def get_wallet_balance():
    """جلب رصيد المحفظة"""
    try:
        account = binance_client.get_account()
        balances = {}
        
        for balance in account['balances']:
            free = float(balance['free'])
            locked = float(balance['locked'])
            total = free + locked
            
            if total > 0:
                balances[balance['asset']] = {
                    'متاح': free,
                    'مقفل': locked,
                    'الإجمالي': total
                }
        
        return balances
    except Exception as e:
        print(f"❌ خطأ في جلب الرصيد: {e}")
        return {}

def get_usdt_balance():
    """جلب رصيد USDT المتاح"""
    try:
        account = binance_client.get_account()
        for balance in account['balances']:
            if balance['asset'] == 'USDT':
                return float(balance['free'])
        return 0
    except:
        return 0

def get_current_price(symbol):
    """جلب السعر الحالي"""
    try:
        ticker = binance_client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except:
        return None

def get_data_binance(symbol, interval=CANDLE_INTERVAL, limit=NUM_CANDLES):
    """جلب بيانات الشمعات من Binance"""
    try:
        klines = binance_client.get_historical_klines(symbol, interval, limit=limit)
        df = pd.DataFrame(klines, columns=[
            'time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['open'] = pd.to_numeric(df['open'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        df.index = pd.to_datetime(df['time'].astype(int), unit='ms')
        
        if len(df) >= 50:
            return df[['open', 'high', 'low', 'close', 'volume']]
        return None
    except:
        return None

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                        🤖 وظائف التداول الفعلي                          ║
# ╚════════════════════════════════════════════════════════════════════════════╝

def execute_buy(symbol, amount_usdt):
    """تنفيذ عملية شراء"""
    try:
        current_price = get_current_price(symbol)
        if not current_price:
            print(f"❌ لا يمكن جلب سعر {symbol}")
            return None
        
        quantity = amount_usdt / current_price
        
        order = binance_client.order_market_buy(symbol=symbol, quantity=quantity)
        avg_price = float(order['cummulativeQuoteAssetTransacted']) / float(order['executedQty'])
        
        print(f"✅ تم شراء {quantity:.4f} {symbol} بسعر ${avg_price:.4f}")
        return {
            'symbol': symbol,
            'quantity': float(order['executedQty']),
            'price': avg_price
        }
    except BinanceAPIException as e:
        print(f"❌ خطأ Binance: {e}")
        return None
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return None

def execute_sell(symbol, quantity):
    """تنفيذ عملية بيع"""
    try:
        order = binance_client.order_market_sell(symbol=symbol, quantity=quantity)
        avg_price = float(order['cummulativeQuoteAssetTransacted']) / float(order['executedQty'])
        
        print(f"✅ تم بيع {quantity:.4f} {symbol} بسعر ${avg_price:.4f}")
        return {
            'symbol': symbol,
            'quantity': float(order['executedQty']),
            'price': avg_price
        }
    except BinanceAPIException as e:
        print(f"❌ خطأ Binance: {e}")
        return None
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return None

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                        📊 وظائف التحليل الفني                            ║
# ╚════════════════════════════════════════════════════════════════════════════╝

def calculate_indicators(df):
    """حساب المؤشرات"""
    try:
        macd = df.ta.macd()
        ichimoku = df.ta.ichimoku()
        rsi = df.ta.rsi(length=14)
        atr = df.ta.atr(length=14)
        
        if macd is None or ichimoku is None or rsi is None or atr is None:
            return None
        
        return {
            'macd': macd,
            'ichimoku': ichimoku,
            'rsi': rsi,
            'atr': atr
        }
    except:
        return None

def check_buy_signal(df, indicators):
    """التحقق من شروط الشراء"""
    try:
        indicators_data = calculate_indicators(df)
        if not indicators_data:
            return False
        
        macd = indicators_data['macd']
        ichimoku = indicators_data['ichimoku']
        rsi = indicators_data['rsi']
        
        macd_now = macd.iloc[-1, 0]
        signal_now = macd.iloc[-1, 1]
        cp_now = df['close'].iloc[-1]
        isa_now = ichimoku[0]['ISA_9'].iloc[-1]
        isb_now = ichimoku[0]['ISB_26'].iloc[-1]
        rsi_now = rsi.iloc[-1]
        
        macd_prev = macd.iloc[-2, 0]
        signal_prev = macd.iloc[-2, 1]
        cp_prev = df['close'].iloc[-2]
        isa_prev = ichimoku[0]['ISA_9'].iloc[-2]
        isb_prev = ichimoku[0]['ISB_26'].iloc[-2]
        
        buy_signal = (macd_now > signal_now) and (cp_now > isa_now) and (cp_now > isb_now) and (rsi_now < RSI_OVERBOUGHT)
        not_buy_before = not ((macd_prev > signal_prev) and (cp_prev > isa_prev) and (cp_prev > isb_prev))
        
        return buy_signal and not_buy_before
    except:
        return False

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                        🎯 وظائف فحص المحفظة                             ║
# ╚════════════════════════════════════════════════════════════════════════════╝

def check_portfolio_positions():
    """فحص المحفظة والتحقق من البيع"""
    portfolio = load_portfolio()
    if not portfolio:
        return
    
    print("\n" + "="*80)
    print("🔍 فحص المحفظة الحالية")
    print("="*80)
    
    usdt_balance = get_usdt_balance()
    print(f"💵 رصيد USDT المتاح: ${usdt_balance:.2f}")
    
    for symbol, position in list(portfolio.items()):
        try:
            current_price = get_current_price(symbol)
            if not current_price:
                continue
            
            quantity = position['quantity']
            buy_price = position['buy_price']
            current_value = quantity * current_price
            
            profit_loss_usd = current_value - (quantity * buy_price)
            profit_loss_pct = (profit_loss_usd / (quantity * buy_price)) * 100
            
            sl = position.get('sl', position.get('initial_sl'))
            tp = position.get('tp', position.get('initial_tp'))
            
            print(f"\n📊 {symbol}:")
            print(f"   الكمية: {quantity:.4f}")
            print(f"   سعر الشراء: ${buy_price:.4f}")
            print(f"   السعر الحالي: ${current_price:.4f}")
            print(f"   الربح/الخسارة: ${profit_loss_usd:.2f} ({profit_loss_pct:+.2f}%)")
            print(f"   SL: ${sl:.4f} | TP: ${tp:.4f}")
            
            # فحص Stop Loss
            if current_price <= sl:
                print(f"   🛑 تحقق Stop Loss! البيع الآن...")
                
                sell_result = execute_sell(symbol, quantity)
                if sell_result:
                    final_price = sell_result['price']
                    final_profit = (final_price - buy_price) * quantity
                    final_pct = ((final_price - buy_price) / buy_price) * 100
                    
                    msg = f"🛑 *تحقق وقف الخسارة!*\n\n💎 العملة: #{symbol}\n📉 بيع: {quantity:.4f} بسعر ${final_price:.4f}\n💰 الخسارة: ${final_profit:.2f} ({final_pct:.2f}%)\n🕒 الوقت: {datetime.now().strftime('%H:%M')}"
                    send_msg(msg, symbol=symbol)
                    
                    add_to_history(symbol, 'بيع', quantity, final_price, final_pct, tp, sl)
                    del portfolio[symbol]
                    save_portfolio(portfolio)
            
            # فحص Take Profit
            elif current_price >= tp:
                if ENABLE_TRAILING_STOP:
                    df = get_data_binance(symbol)
                    if df is not None:
                        indicators_data = calculate_indicators(df)
                        if indicators_data:
                            atr = indicators_data['atr'].iloc[-1]
                            
                            last_tp = tp
                            new_sl = last_tp
                            new_tp = last_tp + (TRAILING_TP_ATR * atr)
                            
                            print(f"   ⬆️  ملاحقة الربح! نصعد النقاط:")
                            print(f"      SL القديم: ${sl:.4f} → SL الجديد: ${new_sl:.4f}")
                            print(f"      TP القديم: ${tp:.4f} → TP الجديد: ${new_tp:.4f}")
                            
                            portfolio[symbol]['sl'] = new_sl
                            portfolio[symbol]['tp'] = new_tp
                            portfolio[symbol]['last_tp_update'] = datetime.now().isoformat()
                            save_portfolio(portfolio)
                            
                            msg = f"⬆️ *ملاحقة الربح!*\n\n💎 العملة: #{symbol}\n📈 السعر الحالي: ${current_price:.4f}\n🎯 TP الجديد: ${new_tp:.4f}\n🛑 SL الجديد: ${new_sl:.4f}\n🕒 الوقت: {datetime.now().strftime('%H:%M')}"
                            send_msg(msg, symbol=symbol)
                else:
                    print(f"   ✅ تحقق Take Profit! البيع الآن...")
                    
                    sell_result = execute_sell(symbol, quantity)
                    if sell_result:
                        final_price = sell_result['price']
                        final_profit = (final_price - buy_price) * quantity
                        final_pct = ((final_price - buy_price) / buy_price) * 100
                        
                        msg = f"✅ *تحقق أخذ الربح!*\n\n💎 العملة: #{symbol}\n📈 بيع: {quantity:.4f} بسعر ${final_price:.4f}\n💰 الربح: ${final_profit:.2f} (+{final_pct:.2f}%)\n🕒 الوقت: {datetime.now().strftime('%H:%M')}"
                        send_msg(msg, symbol=symbol)
                        
                        add_to_history(symbol, 'بيع', quantity, final_price, final_pct, tp, sl)
                        del portfolio[symbol]
                        save_portfolio(portfolio)
        
        except Exception as e:
            print(f"❌ خطأ في فحص {symbol}: {e}")
            continue

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                        🔍 وظيفة المسح الرئيسية                            ║
# ╚════════════════════════════════════════════════════════════════════════════╝

def run_scan():
    """المسح الشامل والتداول"""
    print("\n" + "="*80)
    print(f"🚀 بدء المسح الشامل - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # الخطوة 1: فحص المحفظة
    check_portfolio_positions()
    
    # الخطوة 2: فحص اتجاه السوق
    print("\n" + "="*80)
    print("📈 فحص اتجاه السوق العام (البيتكوين)")
    print("="*80)
    
    btc_df = get_data_binance('BTCUSDT')
    if btc_df is None or btc_df.empty:
        print("❌ لا يمكن جلب بيانات البيتكوين. سيتم التوقف.")
        return
    
    btc_price = btc_df['close'].iloc[-1]
    ema50_btc = btc_df['close'].ewm(span=50, adjust=False).mean().iloc[-1]
    
    if btc_price <= ema50_btc:
        print(f"📉 البيتكوين تحت EMA50 (${btc_price:.2f} < ${ema50_btc:.2f}). توقف مسح العملات الجديدة.")
        return
    
    print(f"✅ البيتكوين صاعد (${btc_price:.2f} > ${ema50_btc:.2f}). مسح العملات الجديدة...")
    
    # الخطوة 3: جلب قائمة العملات
    symbols = get_all_trading_symbols()
    portfolio = load_portfolio()
    owned_symbols = set(portfolio.keys())
    available_symbols = [s for s in symbols if s not in owned_symbols]
    
    print(f"📊 عدد العملات المتاحة للمسح: {len(available_symbols)}")
    
    found_signals = 0
    usdt_balance = get_usdt_balance()
    
    print(f"💵 رصيد USDT: ${usdt_balance:.2f}")
    
    if usdt_balance < TRADING_AMOUNT:
        print(f"⚠️  لا يكفي الرصيد! مطلوب ${TRADING_AMOUNT:.2f} وديك ${usdt_balance:.2f} - لن يتم الشراء")
        return
    
    # الخطوة 4: مسح العملات
    print(f"\n📌 جاري مسح العملات بحثاً عن إشارات شراء...")
    
    for idx, symbol in enumerate(available_symbols, 1):
        try:
            df = get_data_binance(symbol)
            if df is None or df.empty:
                continue
            
            vol_usd = df['volume'] * df['close']
            current_vol = vol_usd.iloc[-1]
            avg_vol = vol_usd.rolling(window=20).mean().iloc[-1]
            
            if current_vol < MIN_VOLUME_USD or current_vol < (avg_vol * VOLUME_MULTIPLIER):
                continue
            
            indicators_data = calculate_indicators(df)
            if not indicators_data:
                continue
            
            if check_buy_signal(df, indicators_data):
                current_price = df['close'].iloc[-1]
                atr = indicators_data['atr'].iloc[-1]
                
                buy_price = current_price
                sl = buy_price - (SL_ATR_MULTIPLIER * atr)
                tp = buy_price + (TP_ATR_MULTIPLIER * atr)
                
                sl_pct = ((SL_ATR_MULTIPLIER * atr) / buy_price) * 100
                tp_pct = ((TP_ATR_MULTIPLIER * atr) / buy_price) * 100
                
                if usdt_balance >= TRADING_AMOUNT:
                    print(f"\n✨ إشارة شراء: {symbol}")
                    
                    buy_result = execute_buy(symbol, TRADING_AMOUNT)
                    
                    if buy_result:
                        quantity = buy_result['quantity']
                        actual_buy_price = buy_result['price']
                        
                        portfolio[symbol] = {
                            'quantity': quantity,
                            'buy_price': actual_buy_price,
                            'initial_sl': sl,
                            'initial_tp': tp,
                            'sl': sl,
                            'tp': tp,
                            'buy_time': datetime.now().isoformat(),
                            'amount_usdt': TRADING_AMOUNT
                        }
                        save_portfolio(portfolio)
                        
                        add_to_history(symbol, 'شراء', quantity, actual_buy_price, tp=tp, sl=sl)
                        
                        msg = f"✅ *إشارة شراء جديدة!*\n\n💎 العملة: #{symbol}\n💵 تم شراء: {quantity:.4f} بسعر ${actual_buy_price:.4f}\n🎯 أخذ الربح: ${tp:.4f} (+{tp_pct:.2f}%)\n🛑 وقف الخسارة: ${sl:.4f} (-{sl_pct:.2f}%)\n📊 RSI: {indicators_data['rsi'].iloc[-1]:.1f}\n🕒 الوقت: {datetime.now().strftime('%H:%M')}"
                        send_msg(msg, symbol=symbol)
                        
                        found_signals += 1
                        usdt_balance -= TRADING_AMOUNT
        
        except Exception as e:
            continue
        
        if idx % 100 == 0:
            print(f"⏳ تم فحص {idx}/{len(available_symbols)}...")
    
    print(f"\n✅ اكتمل المسح. إشارات جديدة: {found_signals}")
    print("="*80)

# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                        🎬 البرنامج الرئيسي                               ║
# ╚════════════════════════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🤖 بوت التداول التلقائي الذكي")
    print("="*80)
    print(f"""
⚙️ الإعدادات الحالية:
───────────────────────────────────────────────────────────────────────────────
  🕐 فترة الشمعة: {CANDLE_INTERVAL}
  📊 عدد الشمعات: {NUM_CANDLES}
  ⏰ النبض: كل {SCAN_INTERVAL} دقائق (التحليل عند إغلاق الشمعة)
  
💰 إعدادات التداول:
───────────────────────────────────────────────────────────────────────────────
  💵 المبلغ لكل صفقة: ${TRADING_AMOUNT}
  🔢 الحد الأدنى للعملة: ${MIN_WALLET_BALANCE}
  📈 الحد الأدنى للسيولة: ${MIN_VOLUME_USD}
  
🎯 إعدادات الاستراتيجية:
───────────────────────────────────────────────────────────────────────────────
  🛑 Stop Loss: {SL_ATR_MULTIPLIER} × ATR
  📈 Take Profit: {TP_ATR_MULTIPLIER} × ATR
  📊 RSI: {RSI_OVERBOUGHT}
  ⬆️  ملاحقة الربح: {'✅ مفعلة' if ENABLE_TRAILING_STOP else '❌ معطلة'}
───────────────────────────────────────────────────────────────────────────────
""")
    
    start_msg = f"""🚀 *تم تشغيل البوت بنجاح!*

⚙️ الإعدادات:
• الشمعة: {CANDLE_INTERVAL}
• النبض: كل {SCAN_INTERVAL} دقائق
• المبلغ: ${TRADING_AMOUNT} لكل صفقة
• ملاحقة الربح: {'✅' if ENABLE_TRAILING_STOP else '❌'}

🔍 البوت يبدأ المسح الآن...
📡 مصدر البيانات: Binance API
"""
    send_msg(start_msg)
    
    run_scan()
    
    print("\n" + "="*80)
    print("🔄 البوت يعمل بشكل مستمر...")
    print("="*80)
    
    last_scan_time = datetime.now()
    
    while True:
        try:
            current_time = datetime.now()
            time_since_last_scan = (current_time - last_scan_time).total_seconds() / 60
            
            if time_since_last_scan >= SCAN_INTERVAL:
                run_scan()
                last_scan_time = current_time
            
            if current_time.second == 0 and current_time.minute % 5 == 0:
                portfolio = load_portfolio()
                remaining = SCAN_INTERVAL - int(time_since_last_scan)
                print(f"\n🕐 {current_time.strftime('%H:%M:%S')} | عملات في المحفظة: {len(portfolio)} | المسح التالي بعد {remaining} دقائق")
            
            time.sleep(1)
        
        except Exception as e:
            print(f"\n❌ خطأ في الحلقة الرئيسية: {e}")
            time.sleep(10)
