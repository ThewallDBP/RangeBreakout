import streamlit as st
import yfinance as yf
import pandas as pd
import math
import pandas_ta as ta

# Page Configuration
st.set_page_config(page_title="Nifty Gann & ORB Scanner", layout="wide")
st.title("📊 Nifty Gann Levels & Stock Scanner")

# Sidebar Input
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
    # છેલ્લી રજાઓ ધ્યાનમાં રાખીને 7 દિવસનો ડેટા લેવો
    df = yf.download(symbol, period="7d", interval="15m")
    
    if not df.empty:
        # કિંમતને સુરક્ષિત રીતે ફ્લોટ નંબરમાં ફેરવવી
        raw_price = df['Close'].iloc[-1]
        curr_price = float(raw_price.iloc[0]) if hasattr(raw_price, 'iloc') else float(raw_price)
        
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

        # RSI ની ગણતરી અને સુરક્ષિત રીતે વેલ્યુ મેળવવી
        df['RSI'] = ta.rsi(df['Close'], length=14)
        raw_rsi = df['RSI'].iloc[-1]
        
        # જો RSI હજુ ગણાઈ રહ્યો હોય (NaN હોય) તો તેની તપાસ
        if pd.isna(raw_rsi):
            c_rsi = 0.0
            st.warning("RSI is still calculating...")
        else:
            c_rsi = float(raw_rsi.iloc[0]) if hasattr(raw_rsi, 'iloc') else float(raw_rsi)

        # Opening Range શોધવી (છેલ્લા ટ્રેડિંગ દિવસની પહેલી 15 મિનિટ)
        latest_day = df.index[-1].date()
        day_data = df[df.index.date == latest_day]
        
        raw_high = day_data['High'].iloc[0]
        raw_low = day_data['Low'].iloc[0]
        
        or_high = float(raw_high.iloc[0]) if hasattr(raw_high, 'iloc') else float(raw_high)
        or_low = float(raw_low.iloc[0]) if hasattr(raw_low, 'iloc') else float(raw_low)

        # Metrics ડિસ્પ્લે
        m1, m2, m3 = st.columns(3)
        m1.metric("15m RSI", f"{c_rsi:.2f}")
        m2.metric("OR High", f"{or_high:.2f}")
        m3.metric("OR Low", f"{or_low:.2f}")

        # બ્રેકઆઉટ સિગ્નલ લોજિક
        if curr_price > or_high and (c_rsi > 60 or (35 <= c_rsi <= 45)):
            st.success(f"🔥 BULLISH BREAKOUT! Price is holding above {or_high:.2f}")
        elif curr_price < or_low and (c_rsi < 40 or (55 <= c_rsi <= 65)):
            st.error(f"⚠️ BEARISH BREAKDOWN! Price is dropping below {or_low:.2f}")
        else:
            st.info("Market is currently in range or indicators are neutral.")

    else:
        st.warning("No data found. Please check ticker symbol.")

except Exception as e:
    st.error(f"Something went wrong: {e}")
