import streamlit as st
import yfinance as yf
import pandas as pd
import math
import pandas_ta as ta

# Page Setup
st.set_page_config(page_title="Nifty Gann & ORB Scanner", layout="wide")
st.title("📊 Nifty Gann Levels & Stock Scanner")

# Sidebar
st.sidebar.header("Settings")
symbol = st.sidebar.text_input("Enter Ticker (NSE)", value="^NSEI")

def get_gann_levels(price):
    sqrt_price = math.sqrt(price)
    levels = {"90°": 0.5, "180°": 1.0, "270°": 1.5, "360°": 2.0}
    data = []
    for deg, factor in levels.items():
        res = math.pow(sqrt_price + factor, 2)
        sup = math.pow(sqrt_price - factor, 2)
        data.append({"Degree": deg, "Support": round(sup, 4), "Resistance": round(res, 4)})
    return pd.DataFrame(data), sqrt_price

try:
    # Fetch Data - Increase period to ensure data availability on weekends
    df = yf.download(symbol, period="7d", interval="15m")
    
    if not df.empty:
        curr_price = float(df['Close'].iloc[-1])
        
        # 1. Gann Analysis
        st.subheader(f"📐 Gann Analysis for {symbol}")
        col1, col2 = st.columns([1, 2])
        
        gann_df, sqrt_val = get_gann_levels(curr_price)
        nearest_sq = round(sqrt_val)
        
        with col1:
            st.metric("Current Price", f"{curr_price:.2f}")
            st.write(f"Price is near square of: **{nearest_sq}** (Square: {nearest_sq**2})")
        
        with col2:
            st.table(gann_df)

        st.divider()
        st.subheader("🚀 Opening Range & Indicators Status")

        # Calculate Indicators safely
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['SMA20'] = ta.sma(df['Close'], length=20)
        
        # Get Latest Values
        c_rsi = df['RSI'].iloc[-1]
        c_sma = df['SMA20'].iloc[-1]
        
        # Get Opening Range for the latest available trading day
        latest_day = df.index[-1].date()
        today_df = df[df.index.date == latest_day]
        or_high = today_df['High'].iloc[0]
        or_low = today_df['Low'].iloc[0]

        # Display Metrics only if values are not None
        m1, m2, m3 = st.columns(3)
        
        if not pd.isna(c_rsi):
            m1.metric("15m RSI", f"{c_rsi:.2f}")
        else:
            m1.write("RSI: Calculating...")

        m2.metric("OR High", f"{or_high:.2f}")
        
        if not pd.isna(c_sma):
            m3.metric("20 SMA", f"{c_sma:.2f}")
        else:
            m3.write("SMA: Calculating...")

        # Final Signal Logic
        if not pd.isna(c_rsi):
            if curr_price > or_high and (c_rsi > 60 or (35 <= c_rsi <= 45)):
                st.success(f"🔥 BULLISH BREAKOUT Detected on {symbol}!")
            elif curr_price < or_low and (c_rsi < 40 or (55 <= c_rsi <= 65)):
                st.error(f"⚠️ BEARISH BREAKDOWN Detected on {symbol}!")
            else:
                st.info("Conditions for breakout/breakdown not met yet.")
        else:
            st.warning("Waiting for more market data to generate signals.")

    else:
        st.error("No data found. Check if the ticker is correct (e.g., RELIANCE.NS).")

except Exception as e:
    st.error(f"Something went wrong: {e}")
