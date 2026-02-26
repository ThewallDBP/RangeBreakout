import streamlit as st
import yfinance as ticker # અથવા જે લાઈબ્રેરી તમે વાપરતા હોવ

# ૧. પ્રથમ ૧૫ મિનિટની રેન્જ મેળવવા માટેનું ફંક્શન
def get_15min_range(df):
    # ખાતરી કરો કે ડેટા ૧૫ મિનિટના ટાઈમફ્રેમમાં છે
    first_candle = df.iloc[0] 
    return first_candle['High'], first_candle['Low']

# ૨. ફિલ્ટર એપ્લાય કરવા માટેનો કોડ
st.sidebar.title("Breakout Filters")
filter_choice = st.sidebar.selectbox(
    "Select Breakout Type:",
    ["All Stocks", "Stock Above 1st 15 min Candle", "Stock Below 1st 15 min Candle"]
)

# ૩. ફિલ્ટરિંગ લોજિક
if filter_choice == "Stock Above 1st 15 min Candle":
    # જો LTP > 15 min High હોય તો જ બતાવો
    filtered_df = df[df['LTP'] > df['15min_High']]
    
elif filter_choice == "Stock Below 15 min Candle":
    # જો LTP < 15 min Low હોય તો જ બતાવો
    filtered_df = df[df['LTP'] < df['15min_Low']]
else:
    filtered_df = df
