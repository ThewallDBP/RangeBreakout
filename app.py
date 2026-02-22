import yfinance as yf
import pandas as pd
import pandas_ta as ta
import time

# --- कॉन्फ़िगरेशन ---
STOCKS = ["RELIANCE.NS", "TCS.NS", "SBIN.NS", "HDFCBANK.NS", "INFY.NS"]

def scan():
    print(f"--- Scan Started: {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    for symbol in STOCKS:
        try:
            # 1. डेटा डाउनलोड (15 min for ORB and 1 Day for Pivot)
            # auto_adjust=True ताकि डेटा क्लीन मिले
            df = yf.download(symbol, period="5d", interval="15m", auto_adjust=True)
            daily = yf.download(symbol, period="5d", interval="1d", auto_adjust=True)

            if df.empty or len(df) < 20:
                print(f"Skipping {symbol}: Not enough data.")
                continue

            # 2. इंडिकेटर्स
            df['RSI'] = ta.rsi(df['Close'], length=14)
            df['SMA20'] = ta.sma(df['Close'], length=20)

            # 3. आज का डेटा निकालें
            today_date = df.index[-1].date()
            today_df = df[df.index.date == today_date]

            if today_df.empty:
                print(f"Skipping {symbol}: Market data not available for today.")
                continue

            # 4. Opening Range (पहली 15 मिनट की कैंडल)
            or_high = today_df['High'].iloc[0]
            or_low = today_df['Low'].iloc[0]

            # 5. डेली लेवल्स (Previous Day)
            pdh = daily['High'].iloc[-2]
            pdl = daily['Low'].iloc[-2]
            pdc = daily['Close'].iloc[-2]
            pivot = (pdh + pdl + pdc) / 3

            # 6. करंट वैल्यूज (नवीनतम कैंडल)
            # यहाँ .item() का उपयोग किया है ताकि 'Series Ambiguous' एरर न आए
            curr_close = df['Close'].iloc[-1]
            curr_rsi = df['RSI'].iloc[-1]
            curr_sma = df['SMA20'].iloc[-1]

            # --- बुलिश लॉजिक (Breakout) ---
            rsi_bullish = (curr_rsi > 60) or (35 <= curr_rsi <= 45)
            near_pdl = (curr_close >= pdl) and (curr_close <= pdl * 1.01)
            
            is_bullish = (curr_close > or_high) and rsi_bullish and \
                         (curr_close > pdh or near_pdl) and \
                         (curr_close >= curr_sma * 0.998) and \
                         (curr_close > pivot)

            # --- बेयरिश लॉजिक (Breakdown) ---
            rsi_bearish = (curr_rsi < 40) or (55 <= curr_rsi <= 65)
            near_pdh = (curr_close <= pdh) and (curr_close >= pdh * 0.99)
            
            is_bearish = (curr_close < or_low) and rsi_bearish and \
                         (curr_close < pdl or near_pdh) and \
                         (curr_close <= curr_sma * 1.002) and \
                         (curr_close < pivot)

            # 7. रिजल्ट प्रिंट करें
            if is_bullish:
                print(f"🚀 BUY SIGNAL: {symbol} | Price: {round(curr_close, 2)} | RSI: {round(curr_rsi, 2)}")
            elif is_bearish:
                print(f"🔻 SELL SIGNAL: {symbol} | Price: {round(curr_close, 2)} | RSI: {round(curr_rsi, 2)}")
            else:
                print(f"Neutral: {symbol} (Price: {round(curr_close, 2)})")

        except Exception as e:
            print(f"Error scanning {symbol}: {e}")

if __name__ == "__main__":
    scan()
