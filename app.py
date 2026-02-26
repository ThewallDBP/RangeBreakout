import streamlit as st
import yfinance as yf
import pandas as pd

# ૧. સ્ટોક સિલેક્શન (ઉદાહરણ તરીકે)
symbol = st.text_input("Enter Stock Symbol (e.g. RELIANCE.NS)", "SBIN.NS")

# ૨. ડેટા ફેચ કરવો (આના વગર 'df' એરર આવશે)
data = yf.download(symbol, period="1d", interval="15m")

if not data.empty:
    # Multi-index ડેટાને સાફ કરવો
    df = data.copy()
    
    # પ્રથમ ૧૫ મિનિટની કેન્ડલનો High અને Low
    first_15min_high = df.iloc[0]['High']
    first_15min_low = df.iloc[0]['Low']
    
    # કરન્ટ પ્રાઈસ (LTP)
    ltp = df.iloc[-1]['Close']

    st.write(f"15 min High: {first_15min_high:.2f} | Low: {first_15min_low:.2f} | LTP: {ltp:.2f}")

    # ૩. ફિલ્ટર સિલેક્શન
    filter_choice = st.radio(
        "Select Filter:",
        ["All Stocks", "Stock Above 1st 15 min Candle", "Stock Below 1st 15 min Candle"]
    )

    # ૪. ફિલ્ટરિંગ લોજિક (અહીં 'df' મળી જશે)
    if filter_choice == "Stock Above 1st 15 min Candle":
        if ltp > first_15min_high:
            st.success(f"🚀 {symbol} is Above 15 min range!")
        else:
            st.warning("Not in range")
            
    elif filter_choice == "Stock Below 15 min Candle":
        if ltp < first_15min_low:
            st.error(f"📉 {symbol} is Below 15 min range!")
        else:
            st.warning("Not in range")
    else:
        st.dataframe(df)
else:
    st.error("Data not found. Please check the symbol.")
