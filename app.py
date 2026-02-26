import streamlit as st
import yfinance as yf

# ૧. સ્ટોક સિમ્બોલ ઇનપુટ
symbol = st.text_input("Enter Symbol", "RELIANCE.NS")

# ૨. ડેટા ડાઉનલોડ (૧૫ મિનિટના ઇન્ટરવલ સાથે)
data = yf.download(symbol, period="1d", interval="15m")

# ચેક કરો કે ડેટા મળ્યો છે કે નહીં
if not data.empty and len(data) > 0:
    
    # ૩. વેરીએબલ અહીં ડિફાઇન (Define) કરો
    first_15min_high = data.iloc[0]['High']
    first_15min_low = data.iloc[0]['Low']
    ltp = data.iloc[-1]['Close'] # લેટેસ્ટ પ્રાઈસ

    # ૪. હવે આ લાઈન કામ કરશે કારણ કે ઉપર વેરીએબલ બની ગયા છે
    st.write(f"15 min High: {first_15min_high:.2f} | Low: {first_15min_low:.2f} | LTP: {ltp:.2f}")

    # ૫. ફિલ્ટર લોજિક
    filter_choice = st.radio("Filter", ["Above 15m Range", "Below 15m Range"])

    if filter_choice == "Above 15m Range":
        if ltp > first_15min_high:
            st.success("🎯 Breakout Above!")
        else:
            st.info("Still in range")
            
    elif filter_choice == "Below 15m Range":
        if ltp < first_15min_low:
            st.error("📉 Breakdown Below!")
        else:
            st.info("Still in range")
else:
    st.error("Data not found. Please check your internet or symbol.")
