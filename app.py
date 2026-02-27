import streamlit as st
import yfinance as yf
import pandas as pd
import math
import pandas_ta as ta
import requests

# Page Config
st.set_page_config(page_title="Pro Trader Dashboard", layout="wide")
st.title("🚀 Pro Multi-Stock Gann & ORB Scanner")

# Sidebar Configuration
st.sidebar.header("Configuration")
watchlist = st.sidebar.multiselect(
    "Select Stocks to Scan:", 
    ["^NSEI", "^NSEBANK", "RELIANCE.NS", "TCS.NS", "SBIN.NS", "HDFCBANK.NS", "ITC.NS", "TATAMOTORS.NS", "INFY.NS", "ICICIBANK.NS"],
    default=["SBIN.NS", "RELIANCE.NS"]
)

st.sidebar.subheader("Telegram Alerts")
tg_token = st.sidebar.text_input("Bot Token", type="password")
tg_chat_id = st.sidebar.text_input("Chat ID")

def send_tg_msg(msg):
    if tg_token and tg_chat_id:
        try:
            url = f"https://api.telegram.org/bot{tg_token}/sendMessage?chat_id={tg_chat_id}&text={msg}"
            requests.get(url, timeout=5)
        except: pass

def get_gann_analysis(price):
    sqrt_p = math.sqrt(price)
    t1 = math.pow(sqrt_p + 0.5, 2)
    t2 = math.pow(sqrt_p + 1.0, 2)
    sl = math.pow(sqrt_p - 0.5, 2)
    return round(t1, 2), round(t2, 2), round(sl, 2)

results = []

if st.button("Start Global Scan 🔍"):
    progress_bar = st.progress(0)
    for index, symbol in enumerate(watchlist):
        try:
            # ડેટા ફેચિંગ (છેલ્લા 7 દિવસ)
            df = yf.download(symbol, period="7d", interval="15m", progress=False)
            if df.empty: continue

            # કિંમત મેળવતી વખતે સુરક્ષા (Safety checks)
            last_price = df['Close'].iloc[-1]
            curr_price = float(last_price.iloc[0]) if hasattr(last_price, 'iloc') else float(last_price)
            
            # RSI કેલ્ક્યુલેશન
            df['RSI'] = ta.rsi(df['Close'], length=14)
            rsi_val = df['RSI'].iloc[-1]
            c_rsi = float(rsi_val.iloc[0]) if hasattr(rsi_val, 'iloc') else (float(rsi_val) if not pd.isna(rsi_val) else 0.0)

            # Opening Range
            latest_day = df.index[-1].date()
            day_data = df[df.index.date == latest_day]
            o_high = float(day_data['High'].iloc[0]) if not day_data.empty else 0.0
            o_low = float(day_data['Low'].iloc[0]) if not day_data.empty else 0.0

            t1, t2, sl = get_gann_analysis(curr_price)
            signal = "Neutral"

            if o_high > 0 and curr_price > o_high and (c_rsi > 60 or (35 <= c_rsi <= 45)):
                signal = "🚀 BULLISH"
                send_tg_msg(f"🔥 {symbol} BUY at {curr_price:.2f}. T1: {t1}, SL: {sl}")
            elif o_low > 0 and curr_price < o_low and (c_rsi < 40 or (55 <= c_rsi <= 65)):
                signal = "🔻 BEARISH"
                send_tg_msg(f"⚠️ {symbol} SELL at {curr_price:.2f}. Target: {sl}")

            results.append({
                "Stock": symbol, "Price": round(curr_price, 2), "RSI": round(c_rsi, 2),
                "Signal": signal, "Target 1": t1, "Target 2": t2, "Stop Loss": sl
            })
            progress_bar.progress((index + 1) / len(watchlist))

        except Exception as e:
            st.error(f"Error in {symbol}: {e}")

    if results:
        res_df = pd.DataFrame(results)
        st.subheader("📋 Market Analysis Report")
        def color_signal(val):
            color = '#d4edda' if val == '🚀 BULLISH' else '#f8d7da' if val == '🔻 BEARISH' else 'white'
            return f'background-color: {color}'
        st.table(res_df.style.applymap(color_signal, subset=['Signal']))
    else:
        st.info("No data found or conditions not met.")
