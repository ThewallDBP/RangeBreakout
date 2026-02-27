import yfinance as yf
import math

def get_gann_levels(symbol):
    try:
        # લાઈવ ડેટા ફેચ કરવો
        data = yf.download(symbol, period="1d", interval="1m")
        if data.empty:
            print(f"ડેટા મળ્યો નથી: {symbol}")
            return

        current_price = data['Close'].iloc[-1]
        
        # વર્ગમૂળની ગણતરી
        sqrt_price = math.sqrt(current_price)
        
        # નિફ્ટી કયા નંબરના વર્ગની નજીક છે?
        nearest_base = round(sqrt_price)
        base_square = math.pow(nearest_base, 2)

        print(f"\n{'='*40}")
        print(f"સ્ટોક/નિફ્ટી: {symbol}")
        print(f"વર્તમાન ભાવ: {current_price:.2f}")
        print(f"નજીકનો સ્ક્વેર નંબર: {nearest_base} (વર્ગ: {base_square:.2f})")
        print(f"{'='*40}")

        # Gann Degrees (90° = +0.5, 180° = +1.0, 270° = +1.5)
        degrees = {
            "90° ": 0.5,
            "180°": 1.0,
            "270°": 1.5,
            "360°": 2.0
        }

        print(f"{'ડિગ્રી':<10} | {'સપોર્ટ':<10} | {'રેઝિસ્ટન્સ':<10}")
        print("-" * 40)

        for deg, factor in degrees.items():
            resistance = math.pow(sqrt_price + factor, 2)
            support = math.pow(sqrt_price - factor, 2)
            print(f"{deg:<10} | {support:<10.2f} | {resistance:<10.2f}")

    except Exception as e:
        print(f"ભૂલ આવી છે: {e}")

# રન કરવા માટે
if __name__ == "__main__":
    # નિફ્ટી માટે '^NSEI' અને સ્ટોક માટે 'RELIANCE.NS' વાપરો
    get_gann_levels("^NSEI") 
    get_gann_levels("RELIANCE.NS")
