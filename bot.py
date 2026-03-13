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
        print("   jari jib el amlat min Binance...")
        response = requests.get('https://api.binance.com/api/v3/exchangeInfo', timeout=30)
        data = response.json()
        symbols = [s['symbol'] for s in data['symbols'] 
                   if s['status'] == 'TRADING' and s['quoteAsset'] == 'USDT']
        print(f"   OK: {len(symbols)} amlat loaded")
        return sorted(symbols)
    except:
        return []

def run_radar(symbols):
    print("\n" + "="*70)
    print(f"ANALYSIS START - {datetime.now().strftime('%H:%M:%S')}")
    print("="*70)
    
    print(f"\nPhase 1: Bitcoin momentum...")
    btc = get_data('BTCUSDT')
    if not btc:
        print(f"   ERROR: BTC data not available")
        print(f"STOP\n")
        return
    
    ema50 = btc['Close'].ewm(span=50, adjust=False).mean()
    btc_price = btc['Close'].iloc[-1]
    btc_ema = ema50.iloc[-1]
    
    if btc_price <= btc_ema:
        print(f"   DOWN: Price {btc_price:.0f} < EMA {btc_ema:.0f}")
        print(f"   Market is DOWN - stopping")
        print(f"STOP\n")
        return
    
    print(f"   UP: Price {btc_price:.0f} > EMA {btc_ema:.0f}")
    print(f"   Continue scanning...")
    
    print(f"\nPhase 2: Liquidity filter (min 200k USD)...")
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
            print(f"   Progress: {idx}/{len(symbols)} ({pct}%)")
        time.sleep(0.02)
    
    print(f"   OK: {len(qualified)} coins qualified")
    if not qualified:
        print(f"   No coins found")
        print(f"STOP\n")
        return
    
    print(f"\nPhase 3: Technical Analysis (MACD + Ichimoku)...")
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
                print(f"   SIGNAL: {s} | Price: ${cp:.4f} | Vol: ${vol_usd:,.0f}")
                send_msg(f"SIGNAL: {s}\nPrice: ${cp:.4f}\nVolume: ${vol_usd:,.0f}")
                found += 1
        except:
            pass
        
        if idx % 20 == 0:
            pct = 100*idx//len(qualified)
            print(f"   Progress: {idx}/{len(qualified)} ({pct}%) | Signals: {found}")
        time.sleep(0.05)
    
    print(f"\n{'='*70}")
    print(f"ANALYSIS COMPLETE")
    print(f"{'='*70}")
    print(f"Summary:")
    print(f"  Total symbols: {len(symbols)}")
    print(f"  Qualified: {len(qualified)}")
    print(f"  Signals: {found}")
    if found > 0:
        pct = 100*found//len(qualified)
        print(f"  Success rate: {pct}%")
    print(f"{'='*70}\n")

print("\n" + "="*70)
print("CRYPTO BOT - AUTOMATIC SIGNAL DETECTOR")
print("="*70)

symbols = get_all_symbols()
if not symbols:
    print("ERROR: Failed to load symbols!")
    exit()

send_msg(f"BOT ACTIVE\nSymbols: {len(symbols)}")
print(f"BOT READY")
print(f"  Symbols: {len(symbols)}")
print(f"  Scan at: minutes 00 and 30")
print("="*70)

last_pulse = -1
while True:
    try:
        now = datetime.now()
        minute = now.minute
        
        if minute % 5 == 0 and minute != last_pulse:
            last_pulse = minute
            print(f"\nPulse: {now.strftime('%H:%M:%S')} - Bot running")
            
            if minute in [0, 30]:
                run_radar(symbols)
        
        time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nBOT STOPPED")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
