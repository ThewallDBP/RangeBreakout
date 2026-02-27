import streamlit as st
import yfinance as yf
import pandas as pd
import math
import pandas_ta as ta
import requests

# Page Config
st.set_page_config(page_title="Pro Trader Dashboard", layout="wide")
st.title("🚀 Pro Multi-Stock Gann & ORB Scanner")

# --- 1. Sidebar Settings ---
st.sidebar.header("Configuration")
watchlist = st.sidebar.multiselect(
    "Select Stocks to Scan:", 
    ["^NSEI", "^NSEBANK", "RELIANCE.NS", "TCS.NS", "SBIN.NS", "HDFCBANK.NS", "ITC.NS", "TATAMOTORS.NS", "INFY.NS", "ICICIBANK.NS"],
    default=["^NSEI", "RELIANCE.NS", "ITC.NS"]
)

# Telegram Settings (Optional)
tg_token = st.sidebar.text_input("Telegram Bot Token", type="password")
tg_chat_id = st.sidebar.text_input("Telegram Chat ID")

def send_tg_msg(msg):
    if tg_token and tg_chat_id:
        url = f"https://api.telegram.org/bot{tg_token}/sendMessage?chat_id={tg_chat_id}&text={msg}"
        requests.get(url)

# --- 2. Gann & Target Logic ---
def get_gann_analysis(price):
    sqrt_p = math.sqrt(price)
    # Target 1 (90°), Target 2 (180°)
    t1 = math.pow(sqrt_p + 0.5, 2)
    t2 = math.pow(sqrt_p + 1.0, 2)
    # Stop Loss (90° Support or previous level)
    sl = math.pow(sqrt_p - 0.5, 2)
    return round(t1, 2), round(t2, 2), round(sl, 2)

# --- 3. Main Scanner Engine ---
results = []

if st.button("Start Global Scan 🔍"):
    for symbol in watchlist:
        try:
            df = yf.download(symbol, period="5d", interval="15m")
            if df.empty: continue

            # Current Data
            curr_price = float(df['Close'].iloc[-1].iloc[0]) if isinstance(df['Close'].iloc[-1], pd.Series) else float(df['Close'].iloc[-1])
            
            # Indicators
            df['RSI'] = ta.rsi(df['Close'], length=14)
            c_rsi = float(df['RSI'].iloc[-1].iloc[0]) if isinstance(df['RSI'].iloc[-1], pd.Series) else float(df['RSI'].iloc[-1])

            # Opening Range
            today_data = df[df.index.date == df.index[-1].date()]
            or_high = float(today_data['High'].iloc[0])
            or_low = float(today_data['Low'].iloc[0])

            # Gann Targets
            target1, target2, stoploss = get_gann_analysis(curr_price)

            # Signal Logic
            signal = "Neutral"
            if curr_price > or_high and (c_rsi > 60 or (35 <= c_rsi <= 45)):
                signal = "🚀 BULLISH"
                send_tg_msg(f"🔥 BULLISH BREAKOUT: {symbol} at {curr_price}. T1: {target1}, SL: {stoploss}")
            elif curr_price < or_low and (c_rsi < 40 or (55 <= c_rsi <= 65)):
                signal = "🔻 BEARISH"
                send_tg_msg(f"⚠️ BEARISH BREAKDOWN: {symbol} at {curr_price}. Target: {stoploss}")

            results.append({
                "Stock": symbol,
                "Price": round(curr_price, 2),
                "RSI": round(c_rsi, 2),
                "Signal": signal,
                "Target 1": target1,
                "Target 2": target2,
                "Stop Loss": stoploss
            )
        except Exception as e:
            st.error(f"Error in {symbol}: {e}")

    # Display Result Table
    if results:
        res_df = pd.DataFrame(results)
        st.table(res_df.style.applymap(lambda x: 'background-color: #d4edda' if x == '🚀 BULLISH' else ('background-color: #f8d7da' if x == '🔻 BEARISH' else ''), subset=['Signal']))
