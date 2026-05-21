
import streamlit as st
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Mega Swing-Scanner", page_icon="🔍", layout="wide")

st.title("🔍 Automatischer Mega-Swing-Scanner")
st.markdown("Dieses Tool zieht sich **live** die Komponenten des **S&P 500**, **Nasdaq 100** sowie die aktivsten **Russell 2000** Werte und filtert die besten Swing-Trading-Setups heraus.")

# --- LIVE-ABRUF DER INDIZES-TICKER ---
@st.cache_data(ttl=86400)  # Speichert die Listen für 24 Std. im Cache für maximale Performance
def get_mega_ticker_list():
    ticker_set = set()
    
    # 1. S&P 500 von Wikipedia laden
    try:
        sp500_table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        sp500_tickers = sp500_table['Symbol'].tolist()
        # Punkte durch Bindestriche ersetzen für Yahoo Finance (z.B. BRK.B -> BRK-B)
        sp500_tickers = [t.replace('.', '-') for t in sp500_tickers]
        ticker_set.update(sp500_tickers)
    except Exception as e:
        st.warning(f"Fehler beim Laden des S&P 500: {e}. Nutze Fallback.")
        ticker_set.update(["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "BRK-B", "JPM", "UNH"])

    # 2. Nasdaq 100 von Wikipedia laden
    try:
        nasdaq_table = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')[2]
        # Spaltenname flexibel abfangen
        col_name = 'Ticker' if 'Ticker' in nasdaq_table.columns else 'Symbol'
        nasdaq_tickers = nasdaq_table[col_name].tolist()
        nasdaq_tickers = [t.replace('.', '-') for t in nasdaq_tickers]
        ticker_set.update(nasdaq_tickers)
    except Exception as e:
        st.warning(f"Fehler beim Laden des Nasdaq 100: {e}.")

    # 3. Russell 2000 (Die volatilsten Top 150 Liquiditäts-Treffer für Swing-Trading)
    # Da ein voller 2000er-Scan den Server sprengt, nutzen wir die bewährtesten Russell-Swing-Titel
    russell_swing_picks = [
        "PLTR", "SOFI", "HOOD", "AFRM", "UPST", "AI", "DKNG", "MARA", "RIOT", "COIN",
        "RIVN", "LCID", "NIO", "XPEV", "LI", "BABA", "PDD", "SNAP", "PINS", "UBER",
        "LYFT", "OPEN", "RUN", "SPWR", "FSR", "NKLA", "CHPT", "BLNK", "BE", "PLUG",
        "FCEL", "QS", "SPCE", "VIR", "GME", "AMC", "BB", "TLRY", "CGC", "SNDL",
        "ACB", "CRSR", "HEAR", "SKLZ", "UWMC", "GHIV", "CLOV", "WISH", "SDC", "ROOT",
        "MILE", "METX", "SENS", "ZOM", "CTRM", "AEI", "PHUN", "MARK", "BBIG", "ANY",
        "ATER", "PROG", "GNUS", "XELA", "TRCH", "MMAT", "CEI", "VKG", "NVAX", "OCGN",
        "INO", "SRNE", "BNGO", "MVIS", "KOSS", "EXPR", "HCMC", "EEENF", "AABB", "OZSC",
        "SOLO", "AYRO", "FUV", "WKHS", "RIDE", "HYLN", "XL", "GOEV", "PTRA", "ARVL",
        "LEV", "GP", "RMO", "NGA", "STPK", "ACTC", "CLSK", "HIVE", "BITF", "HUT"
    ]
    ticker_set.update(russell_swing_picks)
    
    return sorted(list(ticker_set))

# --- EINZEL-ANALYSE FUNKTION ---
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
        
        # RSI (Max 20)
        if 40 <= current_rsi <= 55:
            score += 20
        elif 30 <= current_rsi < 40:
            score += 15
        elif 55 < current_rsi <= 68:
            score += 12
            
        # Trend (Max 20)
        if last_close > last_ema20 and last_close > last_sma50:
            score += 20
        elif last_close > last_ema20:
            score += 10
            
        # MACD (Max 20)
        if last_macd > last_sig:
            score += 20
            
        # Volumen (Max 15)
        if last_volume > avg_volume:
            score += 15
        else:
            score += 7
            
        # 24h Performance (Max 25)
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

# --- OBERFLÄCHE ---
TICKER_LISTE = get_mega_ticker_list()
st.info(f"Gesamtanzahl der geladenen Aktien im Scanner: **{len(TICKER_LISTE)}** Aktien.")

if st.button("🚀 Mega-Markt-Scan jetzt starten"):
    fortschritts_balken = st.progress(0)
    status_text = st.empty()
    ergebnisse = []
    
    status_text.write(f"Scanne {len(TICKER_LISTE)} Aktien gleichzeitig im Hochgeschwindigkeitsmodus...")
    
    # max_workers=25 sorgt für extrem schnelles paralleles Laden der 750+ Aktien
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(analyze_single_stock, t) for t in TICKER_LISTE]
        
        for i, future in enumerate(futures):
            res = future.result()
            if res:
                ergebnisse.append(res)
            fortschritts_balken.progress((i + 1) / len(TICKER_LISTE))
            
    status_text.write("✅ Scan komplett abgeschlossen!")
    
    if ergebnisse:
        df = pd.DataFrame(ergebnisse)
        df = df.sort_values(by="Swing-Score", ascending=False).reset_index(drop=True)
        
        # Begrenzung auf die Top 100 besten Treffer im gesamten Markt
        df = df.head(100)
        
        def color_signal(val):
            if val == "STARKER KAUF": return "background-color: #2ecc71; color: white; font-weight: bold;"
            elif val == "KAUFEN": return "background-color: #27ae60; color: white;"
            elif val == "BEOBACHTEN": return "background-color: #f39c12; color: white;"
            else: return "background-color: #e74c3c; color: white;"

        st.markdown("### 🏆 Die Top 100 Swing-Trading Rangliste (Beste Setups oben)")
        styled_df = df.style.map(color_signal, subset=["Signal"])
        st.dataframe(styled_df, use_container_width=True, height=600)
        st.balloons()
    else:
        st.error("Es konnten keine Daten geladen werden.")
