# --- Logic for Stock Scanner ---

def scan_stocks(data_15m, data_daily):
    # 1. Define Opening Range (First 15-min candle)
    or_high = data_15m['high'].iloc[0]
    or_low = data_15m['low'].iloc[0]
    current_price = data_15m['close'].iloc[-1]
    
    # 2. Indicators
    rsi_15 = calculate_rsi(data_15m, period=14)
    sma_20 = calculate_sma(data_15m, period=20)
    pivot = (data_daily['high'] + data_daily['low'] + data_daily['close']) / 3
    
    # 3. Previous Day Levels
    pdh = data_daily['high'].iloc[-1]
    pdl = data_daily['low'].iloc[-1]
    pdl_upper_limit = pdl * 1.01  # 1% range above PDL
    
    # --- BULLISH CONDITION ---
    is_bullish = (
        current_price > or_high and
        (rsi_15 > 60 or (35 <= rsi_15 <= 45)) and
        (current_price > pdh or (pdl <= current_price <= pdl_upper_limit)) and
        current_price >= (sma_20 * 0.998) and # "Near" 20 SMA
        current_price > pivot
    )
    
    # --- BEARISH CONDITION ---
    is_bearish = (
        current_price < or_low and
        (rsi_15 < 40 or (55 <= rsi_15 <= 65)) and
        (current_price < pdl or (pdh >= current_price >= pdh * 0.99)) and
        current_price <= (sma_20 * 1.002) and
        current_price < pivot)
    
    return is_bullish, is_bearish
