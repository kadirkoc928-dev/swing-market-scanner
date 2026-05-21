import streamlit as st
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Profi Swing-Scanner", page_icon="🔍", layout="wide")

st.title("🔍 Automatischer Profi-Swing-Scanner")
st.markdown("Dieses Tool scannt den Markt vollautomatisch, berechnet die Swing-Scores und listet die besten Setups absteigend auf.")

# Liste der zu scannenden Aktien
TICKER_LISTE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "AMD", "NFLX", "COIN",
    "PLTR", "BABA", "NIO", "XPEV", "LI", "PYPL", "SQ", "DIS", "JPM", "BAC",
    "F", "GM", "XOM", "CVX", "PFE", "MRNA", "PINS", "SNAP", "UBER", "LYFT",
    "SAP.DE", "SIE.DE", "DTE.DE", "MBG.DE", "BMW.DE", "VOW3.DE", "ALV.DE", "BAS.DE",
    "INTC", "QCOM", "MU", "ASML", "TSM", "AVGO", "PANW", "CRWD", "NET", "SNOW",
    "RIVN", "LCID", "MARA", "RIOT", "HOOD", "AFRM", "SOFI", "UPST", "AI", "DKNG"
]

def analyze_single_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="3mo")
        if hist.empty or len(hist) < 20:
            return None
        
        current_price = round(hist['Close'].iloc[-1], 2)
        prev_close = hist['Close'].iloc[-2]
        perf_24h = ((current_price - prev_close) / prev_close) * 100
        
        hist['EMA20'] = hist['Close'].ewm(span=20, adjust=False).mean()
        hist['SMA50'] = hist['Close'].rolling(window=50).mean()
        last_close = hist['Close'].iloc[-1]
        last_ema20 = hist['EMA20'].iloc[-1]
        last_sma50 = hist['SMA50'].iloc[-1]
        
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist['RSI'] = 100 - (100 / (1 + rs))
        current_rsi = hist['RSI'].iloc[-1]
        
        exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
        exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
        hist['MACD'] = exp1 - exp2
        hist['Signal'] = hist['MACD'].ewm(span=9, adjust=False).mean()
        last_macd = hist['MACD'].iloc[-1]
        last_sig = hist['Signal'].iloc[-1]
        
        avg_volume = hist['Volume'].mean()
        last_volume = hist['Volume'].iloc[-1]
        
        score = 0
        
        if 40 <= current_rsi <= 55:
            score += 20
        elif 30 <= current_rsi < 40:
            score += 15
        elif 55 < current_rsi <= 68:
            score += 12
            
        if last_close > last_ema20 and last_close > last_sma50:
            score += 20
        elif last_close > last_ema20:
            score += 10
            
        if last_macd > last_sig:
            score += 20
            
        if last_volume > avg_volume:
            score += 15
        else:
            score += 7
            
        if perf_24h > 2.0:
            score += 25
        elif 0.0 <= perf_24h <= 2.0:
            score += 15
        elif -2.0 <= perf_24h < 0.0:
            score += 5
            
        stop_loss = round(current_price * 0.96, 2)
        take_profit = round(current_price * 1.12, 2)
        
        return {
            "Ticker": ticker,
            "Kurs": current_price,
            "RSI": round(current_rsi, 1),
            "Perf. 24h": f"{round(perf_24h, 2)}%",
            "Swing-Score": score,
            "Signal": "STARKER KAUF" if score >= 75 else ("KAUFEN" if score >= 60 else ("BEOBACHTEN" if score >= 40 else "MEIDEN")),
            "Stop-Loss (-4%)": stop_loss,
            "Take-Profit (+12%)": take_profit
        }
    except:
        return None

if st.button("🚀 Markt-Scan jetzt starten"):
    fortschritts_balken = st.progress(0)
    status_text = st.empty()
    ergebnisse = []
    
    status_text.write("Scanne Live-Marktdaten...")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(analyze_single_stock, t) for t in TICKER_LISTE]
        
        for i, future in enumerate(futures):
            res = future.result()
            if res:
                ergebnisse.append(res)
            fortschritts_balken.progress((i + 1) / len(TICKER_LISTE))
            
    status_text.write("✅ Scan abgeschlossen!")
    
    if ergebnisse:
        df = pd.DataFrame(ergebnisse)
        df = df.sort_values(by="Swing-Score", ascending=False).reset_index(drop=True)
        df = df.head(100)
        
        def color_signal(val):
            if val == "STARKER KAUF": return "background-color: #2ecc71; color: white; font-weight: bold;"
            elif val == "KAUFEN": return "background-color: #27ae60; color: white;"
            elif val == "BEOBACHTEN": return "background-color: #f39c12; color: white;"
            else: return "background-color: #e74c3c; color: white;"

        st.markdown("### 🏆 Die Swing-Trading Rangliste (Top Treffer oben)")
        # REPARIERTE ZEILE: .map statt .applymap
        styled_df = df.style.map(color_signal, subset=["Signal"])
        st.dataframe(styled_df, use_container_width=True, height=600)
        st.balloons()
    else:
        st.error("Es konnten keine Daten geladen werden.")
