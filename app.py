import streamlit as st
import yfinance as yf
import pandas as pd
import math
import pandas_ta as ta

# Page Title
st.set_page_config(page_title="Nifty Gann & ORB Scanner", layout="wide")
st.title("📊 Nifty Gann Levels & Stock Scanner")

# --- Function for Gann Levels ---
def get_gann_levels(price):
    sqrt_price = math.sqrt(price)
    levels = {"90°": 0.5, "180°": 1.0, "270°": 1.5, "360°": 2.0}
    data = []
    for deg, factor in levels.items():
        res = math.pow(sqrt_price + factor, 2)
        sup = math.pow(sqrt_price - factor, 2)
        data.append({"Degree": deg, "Support": round(sup, 2), "Resistance": round(res, 2)})
    return pd.DataFrame(data), round(sqrt_price, 2)

# --- Sidebar Inputs ---
st.sidebar.header("Settings")
symbol = st.sidebar.text_input("Enter Ticker (NSE)", value="^NSEI")
st.sidebar.info("Use .NS for stocks (e.g., RELIANCE.NS)")

# --- Main App Logic ---
try:
    # Fetch Data
    df = yf.download(symbol, period="2d", interval="15m")
    daily = yf.download(symbol, period="5d", interval="1d")
    
    if not df.empty:
        curr_price = df['Close'].iloc[-1]
        
        # 1. Gann Analysis Section
        st.subheader(f"📐 Gann Analysis for {symbol}")
        col1, col2 = st.columns(2)
        
        gann_df, sqrt_val = get_gann_levels(curr_price)
        nearest_sq = round(sqrt_val)
        
        with col1:
            st.metric("Current Price", round(curr_price, 2))
            st.write(f"Nifty is near square of: **{nearest_sq}** (Square: {nearest_sq**2})")
        
        with col2:
            st.table(gann_df)

        # 2. ORB Scanner Section
        st.divider()
        st.subheader("🚀 Opening Range & Indicators Status")
        
        # Indicators
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['SMA20'] = ta.sma(df['Close'], length=20)
        
        # Today's ORB
        today_df = df[df.index.date == df.index[-1].date()]
        or_high = today_df['High'].iloc[0]
        or_low = today_df['Low'].iloc[0]
        
        # Current Stats
        c_rsi = df['RSI'].iloc[-1]
        c_sma = df['SMA20'].iloc[-1]
        
        col3, col4, col5 = st.columns(3)
        col3.metric("15m RSI", round(c_rsi, 2))
        col4.metric("OR High", round(or_high, 2))
        col5.metric("20 SMA", round(c_sma, 2))

        # Signal Logic
        if curr_price > or_high and (c_rsi > 60 or (35 <= c_rsi <= 45)):
            st.success(f"🔥 BULLISH BREAKOUT Detected on {symbol}!")
        elif curr_price < or_low and (c_rsi < 40 or (55 <= c_rsi <= 65)):
            st.error(f"⚠️ BEARISH BREAKDOWN Detected on {symbol}!")
        else:
            st.info("Searching for breakout conditions...")

    else:
        st.warning("No data found. Please check the ticker symbol.")

except Exception as e:
    st.error(f"Error: {e}")
