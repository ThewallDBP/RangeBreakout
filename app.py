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
import pandas as pd
import streamlit as st

def calculate_max_pain(df):
    strikes = df['Strike Price'].values
    total_loss_list = []

    for settlement_price in strikes:
        # Loss for Call Writers
        call_loss = df[df['Strike Price'] < settlement_price]
        c_loss = ((settlement_price - call_loss['Strike Price']) * call_loss['Call_OI']).sum()
        
        # Loss for Put Writers
        put_loss = df[df['Strike Price'] > settlement_price]
        p_loss = ((put_loss['Strike Price'] - settlement_price) * put_loss['Put_OI']).sum()
        
        total_loss_list.append(c_loss + p_loss)

    # Find the strike with minimum total loss
    min_loss_index = total_loss_list.index(min(total_loss_list))
    return strikes[min_loss_index]

# In your Streamlit UI:
# max_pain_level = calculate_max_pain(option_chain_data)
# st.metric("Predicted Expiry Level (Max Pain)", max_pain_level)
import streamlit as st
import datetime

def get_current_hora():
    # હોરાનો ક્રમ (સૂર્યથી શરૂ કરીને ઉલટો ક્રમ: સૂર્ય, શુક્ર, બુધ, ચંદ્ર, શનિ, ગુરુ, મંગળ)
    hora_order = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
    
    # અઠવાડિયાના દિવસ મુજબ પ્રથમ હોરાનો સ્વામી
    day_first_hora = {
        0: 0, # Monday -> Moon (ક્રમ મુજબ સેટ થશે)
        1: 6, # Tuesday -> Mars
        2: 2, # Wednesday -> Mercury
        3: 5, # Thursday -> Jupiter
        4: 1, # Friday -> Venus
        5: 4, # Saturday -> Saturn
        6: 0  # Sunday -> Sun
    }
    
    # સોમવાર માટે ખાસ વ્યવસ્થા કારણ કે તે લિસ્ટમાં 3જા નંબરે છે
    day_to_start_index = {0: 3, 1: 6, 2: 2, 3: 5, 4: 1, 5: 4, 6: 0}

    now = datetime.datetime.now()
    day_of_week = now.weekday() # 0=Monday, 6=Sunday
    
    # સૂર્યોદય આશરે 6:45 AM ગણીએ (તમે આને dynamic પણ કરી શકો)
    sunrise = now.replace(hour=6, minute=45, second=0, microsecond=0)
    
    if now < sunrise:
        # જો સૂર્યોદય પહેલાનો સમય હોય તો આગળના દિવસની હોરા ગણાય
        day_of_week = (day_of_week - 1) % 7
        hours_since_sunrise = (now + datetime.timedelta(days=1) - sunrise).seconds // 3600
    else:
        hours_since_sunrise = (now - sunrise).seconds // 3600

    start_idx = day_to_start_index[day_of_week]
    current_hora_idx = (start_idx + hours_since_sunrise) % 7
    return hora_order[current_hora_idx]

# --- Streamlit UI ---
st.title("Dhaval's Astro-Stock Strategy 📊")

current_hora = get_current_hora()

st.subheader(f"અત્યારની હોરા: **{current_hora}**")

# તમારા (પૂર્વાષાઢા) અને પત્ની (પૂર્વાભાદ્રપદ) માટેનું લોજિક
if current_hora in ["Venus", "Jupiter"]:
    st.success(f"🌟 આ સમય રોકાણ માટે અત્યંત શુભ છે! ({current_hora} હોરા)")
elif current_hora == "Mercury":
    st.info("📈 આ સમય એનાલિસિસ અને ગણતરી (Gann/Fibonacci) માટે શ્રેષ્ઠ છે.")
elif current_hora == "Saturn":
    st.warning("⚠️ શનિની હોરા છે, ઉતાવળમાં સોદા ન કરવા. ધીરજ રાખો.")
else:
    st.write(f"⚖️ અત્યારે {current_hora} ની હોરા ચાલે છે. સામાન્ય વહેવાર રાખવો.")

st.divider()
st.write("નોંધ: આ ગણતરી સરેરાશ સૂર્યોદય 6:45 AM મુજબ છે.")
