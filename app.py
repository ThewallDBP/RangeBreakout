import pandas as pd
import plotly.graph_objects as go

def calculate_heikin_ashi(df):
    ha_df = df.copy()
    
    # HA Close ની ગણતરી
    ha_df['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    
    # HA Open ની ગણતરી
    ha_df['HA_Open'] = 0.0
    ha_df.iloc[0, ha_df.columns.get_loc('HA_Open')] = (df.iloc[0]['Open'] + df.iloc[0]['Close']) / 2
    
    for i in range(1, len(df)):
        ha_df.iloc[i, ha_df.columns.get_loc('HA_Open')] = (ha_df.iloc[i-1]['HA_Open'] + ha_df.iloc[i-1]['HA_Close']) / 2
        
    # HA High અને HA Low ની ગણતરી
    ha_df['HA_High'] = ha_df[['High', 'HA_Open', 'HA_Close']].max(axis=1)
    ha_df['HA_Low'] = ha_df[['Low', 'HA_Open', 'HA_Close']].min(axis=1)
    
    return ha_df

# Streamlit માં ચાર્ટ બતાવવા માટે:
# ha_data = calculate_heikin_ashi(your_stock_dataframe)
# fig = go.Figure(data=[go.Candlestick(x=ha_data.index,
#                 open=ha_data['HA_Open'], high=ha_data['HA_High'],
#                 low=ha_data['HA_Low'], close=ha_data['HA_Close'])])
# st.plotly_chart(fig)
