# --- Logic for Stock Scanner ---

def scan_stocks(data_15m, data_daily):
    # 1. Define Opening Range (First 15-min candle)
    or_high = data_15m['high'].iloc[0]
    or_low = data_15m['low'].iloc[0]
    current_price = data_15m['close'].iloc[-1]
    
    # 2. Indicators
    rsi_15 = calculate_rsi(data_15m, period=14)
    sma_20 = calculate_sma(data_15m, period=20)
    pivot = (data_daily['high'] + data_daily['low'] + data_daily['close']) / 3
    
    # 3. Previous Day Levels
    pdh = data_daily['high'].iloc[-1]
    pdl = data_daily['low'].iloc[-1]
    pdl_upper_limit = pdl * 1.01  # 1% range above PDL
    
    # --- BULLISH CONDITION ---
    is_bullish = (
        current_price > or_high and
        (rsi_15 > 60 or (35 <= rsi_15 <= 45)) and
        (current_price > pdh or (pdl <= current_price <= pdl_upper_limit)) and
        current_price >= (sma_20 * 0.998) and # "Near" 20 SMA
        current_price > pivot
    )
    
    # --- BEARISH CONDITION ---
    is_bearish = (
        current_price < or_low and
        (rsi_15 < 40 or (55 <= rsi_15 <= 65)) and
        (current_price < pdl or (pdh >= current_price >= pdh * 0.99)) and
        current_price <= (sma_20 * 1.002) and
        current_price < pivot)
    
    return is_bullish, is_bearish
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime

# 1. स्टॉक लिस्ट (अपने पसंदीदा स्टॉक्स यहाँ डालें)
stocks = ["RELIANCE.NS", "TCS.NS", "SBIN.NS", "HDFCBANK.NS"]

def scan():
    for symbol in stocks:
        print(f"--- Scanning {symbol} ---")
        
        # डेटा डाउनलोड (5 दिन का 15 मिनट डेटा)
        df = yf.download(symbol, period="5d", interval="15m")
        daily = yf.download(symbol, period="5d", interval="1d")

        if len(df) < 20: 
            print(f"Skipping {symbol}: Not enough data.")
            continue

        # इंडिकेटर्स
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['SMA20'] = ta.sma(df['Close'], length=20)
        
        # आज का डेटा और Opening Range
        today = df.index[-1].date()
        today_df = df[df.index.date == today]
        
        if len(today_df) == 0:
            print("Market not open yet for today.")
            continue

        or_high = today_df['High'].iloc[0]
        or_low = today_df['Low'].iloc[0]
        
        # डेली पिवट (कल के डेटा से)
        pdh, pdl, pdc = daily['High'].iloc[-2], daily['Low'].iloc[-2], daily['Close'].iloc[-2]
        pivot = (pdh + pdl + pdc) / 3

        curr = df.iloc[-1] # लेटेस्ट कैंडल
        
        # --- BULLISH CHECK ---
        rsi_ok = (curr['RSI'] > 60) or (35 <= curr['RSI'] <= 45)
        price_above_or = curr['Close'] > or_high
        above_pivot = curr['Close'] > pivot
        near_sma = curr['Close'] >= (curr['SMA20'] * 0.998)

        if price_above_or and rsi_ok and above_pivot and near_sma:
            print(f"✅ BULLISH SIGNAL: {symbol} at {curr['Close']}")
        else:
            print(f"❌ No signal for {symbol}. (Price: {round(curr['Close'], 2)}, RSI: {round(curr['RSI'], 2)})")

if __name__ == "__main__":
    scan()
