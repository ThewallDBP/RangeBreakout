import streamlit as st
import yfinance as yf
import pandas as pd
import math
import pandas_ta as ta

# Page Configuration
st.set_page_config(page_title="Nifty Gann & ORB Scanner", layout="wide")
st.title("📊 Nifty Gann Levels & Stock Scanner")

# Sidebar for Ticker Input
symbol = st.sidebar.text_input("Enter Ticker (NSE)", value="ITC.NS")

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
    # 7 દિવસનો ડેટા લેવો જેથી રજાના દિવસે પણ છેલ્લો ડેટા મળે
    df = yf.download(symbol, period="7d", interval="15m")
    
    if not df.empty:
        # .item() અથવા .iloc[-1] નો ઉપયોગ કરીને ખાતરી કરવી કે તે સિંગલ વેલ્યુ જ છે
        curr_price = float(df['Close'].iloc[-1])
        
        # 1. Gann Analysis વિભાગ
        st.subheader(f"📐 Gann Analysis for {symbol}")
        gann_df, sqrt_val = get_gann_levels(curr_price)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Current Price", f"{curr_price:.2f}")
            st.write(f"Price is near square of: **{round(sqrt_val)}**")
        with col2:
            st.table(gann_df)

        st.divider()
        st.subheader("🚀 Opening Range & Indicators Status")

        # Indicators ગણતરી
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # છેલ્લી વેલ્યુ લેતી વખતે .iloc[-1] નો જ ઉપયોગ કરવો
        c_rsi_series = df['RSI'].iloc[-1]
        # જો હજુ પણ Series હોય તો તેને Float માં ફેરવવી
        c_rsi = float(c_rsi_series.iloc[0]) if isinstance(c_rsi_series, pd.Series) else float(c_rsi_series)

        # Opening Range શોધવી
        latest_day = df.index[-1].date()
        day_data = df[df.index.date == latest_day]
        or_high = float(day_data['High'].iloc[0])
        or_low = float(day_data['Low'].iloc[0])

        # Metrics ડિસ્પ્લે
        m1, m2, m3 = st.columns(3)
        m1.metric("15m RSI", f"{c_rsi:.2f}")
        m2.metric("OR High", f"{or_high:.2f}")
        m3.metric("OR Low", f"{or_low:.2f}")

        # બ્રેકઆઉટ સિગ્નલ લોજિક
        if curr_price > or_high and (c_rsi > 60 or (35 <= c_rsi <= 45)):
            st.success(f"🔥 BULLISH BREAKOUT! Price is above {or_high:.2f}")
        elif curr_price < or_low and (c_rsi < 40 or (55 <= c_rsi <= 65)):
            st.error(f"⚠️ BEARISH BREAKDOWN! Price is below {or_low:.2f}")
        else:
            st.info("Market is currently within range or neutral.")

    else:
        st.warning("No data found. Please check ticker symbol.")

except Exception as e:
    st.error(f"Something went wrong: {e}")
