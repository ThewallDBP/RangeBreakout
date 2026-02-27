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
    ["^NSEI", "^NSEBANK", "RELIANCE.NS", "TCS.NS", "SBIN.NS", "HDFCBANK.NS", "ITC.NS", "TATAMOTORS.NS", "INFY.NS", "ICICIBANK.NS", "BAJFINANCE.NS", "AXISBANK.NS"],
    default=["^NSEI", "RELIANCE.NS", "ITC.NS"]
)

# Telegram Settings
st.sidebar.subheader("Telegram Alerts")
tg_token = st.sidebar.text_input("Bot Token", type="password", help="Get from @BotFather")
tg_chat_id = st.sidebar.text_input("Chat ID", help="Get from @userinfobot")

def send_tg_msg(msg):
    if tg_token and tg_chat_id:
        try:
            url = f"https://api.telegram.org/bot{tg_token}/sendMessage?chat_id={tg_chat_id}&text={msg}"
            requests.get(url, timeout=5)
        except:
            pass

# --- 2. Gann & Target Logic ---
def get_gann_analysis(price):
    sqrt_p = math.sqrt(price)
    # Targets & SL based on Gann degrees
    t1 = math.pow(sqrt_p + 0.5, 2)
    t2 = math.pow(sqrt_p + 1.0, 2)
    sl = math.pow(sqrt_p - 0.5, 2)
    return round(t1, 2), round(t2, 2), round(sl, 2)

# --- 3. Main Scanner Engine ---
results = []

if st.button("Start Global Scan 🔍"):
    progress_bar = st.progress(0)
    for index, symbol in enumerate(watchlist):
        try:
            df = yf.download(symbol, period="7d", interval="15m", progress=False)
            if df.empty: continue

            # Extract current price safely
            raw_close = df['Close'].iloc[-1]
            curr_price = float(raw_close.iloc[0]) if hasattr(raw_close, 'iloc') else float(raw_close)
            
            # Indicators
            df['RSI'] = ta.rsi(df['Close'], length=14)
            raw_rsi = df['RSI'].iloc[-1]
            c_rsi = float(raw_rsi.iloc[0]) if hasattr(raw_rsi, 'iloc') else float(raw_rsi)

            # Opening Range
            latest_day = df.index[-1].date()
            day_data = df[df.index.date == latest_day]
            
            raw_high = day_data['High'].iloc[0]
            raw_low = day_data['Low'].iloc[0]
            or_high = float(raw_high.iloc[0]) if hasattr(raw_high, 'iloc') else float(raw_high)
            or_low = float(raw_low.iloc[0]) if hasattr(raw_low, 'iloc') else float(raw_low)

            # Gann Targets
            target1, target2, stoploss = get_gann_analysis(curr_price)

            # Signal Logic
            signal = "Neutral"
            if curr_price > or_high and (c_rsi > 60 or (35 <= c_rsi <= 45)):
                signal = "🚀 BULLISH"
                send_tg_msg(f"🔥 {symbol} BUY at {curr_price:.2f}. RSI: {c_rsi:.2f}. T1: {target1}, SL: {stoploss}")
            elif curr_price < or_low and (c_rsi < 40 or (55 <= c_rsi <= 65)):
                signal = "🔻 BEARISH"
                send_tg_msg(f"⚠️ {symbol} SELL at {curr_price:.2f}. RSI: {c_rsi:.2f}. Target: {stoploss}")

            results.append({
                "Stock": symbol,
                "Price": round(curr_price, 2),
                "RSI": round(c_rsi, 2),
                "Signal": signal,
                "Target 1": target1,
                "Target 2": target2,
                "Stop Loss": stoploss
            }) # એરર અહીં સુધારી લીધી છે
            
            progress_bar.progress((index + 1) / len(watchlist))

        except Exception as e:
            st.error(f"Error in {symbol}: {e}")

    # Display Result Table
    if results:
        res_df = pd.DataFrame(results)
        st.subheader("📋 Market Analysis Report")
        
        # Color coding for signals
        def color_signal(val):
            color = '#d4edda' if val == '🚀 BULLISH' else '#f8d7da' if val == '🔻 BEARISH' else 'white'
            return f'background-color: {color}'
        
        st.table(res_df.style.applymap(color_signal, subset=['Signal']))
    else:
        st.info("No stocks matched the criteria. Try changing the watchlist.")
