import streamlit as st
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Mega Swing-Scanner", page_icon="🔍", layout="wide")

st.title("🔍 Ultimativer Mega-Swing-Scanner")
st.markdown("Dieser High-Speed-Scanner prüft das gesamte Universum aus **S&P 500, Nasdaq 100** und den **Top-Werten des Russell 2000** – sortiert nach den besten Setups.")

# --- DIE KOMPLETTE LISTE (ÜBER 650 AKTIEN DIREKT IM CODE) ---
TICKER_LISTE = [
    # --- NASDAQ 100 ---
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "PEP",
    "COST", "CSCO", "TMUS", "CMCSA", "AMD", "NFLX", "ADBE", "AMGN", "ISRG", "HON",
    "QCOM", "INTC", "INTU", "MDLZ", "BKNG", "AMAT", "ADI", "TXN", "PANW", "MU",
    "REGN", "VRTX", "LRCX", "ADP", "MELI", "KLAC", "SNPS", "CDNS", "ASML", "CSX",
    "MAR", "CTAS", "ORLY", "MNST", "WDAY", "ROP", "PCAR", "NXPI", "ADSK", "PAYX",
    "ROST", "KDP", "AEP", "ODFL", "CEG", "MCHP", "AZN", "DDOG", "IDXX", "CPRT",
    "FAST", "EA", "GEHC", "CTSH", "VRSK", "EXC", "CSGP", "BKR", "TEAM", "XEL",
    "ANSS", "MNDY", "PDD", "FTNT", "ALGN", "ILMN", "WBD", "LULU", "SIRI", "MCHP",
    "CTVA", "GILD", "KHC", "DXCM", "GE", "WBA", "ON", "SBUX", "MRVL", "COR",

    # --- S&P 500 (ALLE 500 UNTERNEHMEN) ---
    "A", "AAL", "AAP", "ABBV", "ABC", "ABMD", "ABT", "ACN", "ADBE", "ADI", "ADM", 
    "ADsk", "AEE", "AEP", "AES", "AFL", "AIG", "AIZ", "AJG", "AKAM", "ALB", "ALGN", 
    "ALK", "ALL", "ALLE", "ALXN", "AMAT", "AMCR", "AMD", "AME", "AMGN", "AMP", "AMT", 
    "AMZN", "ANET", "ANSS", "ANTM", "AON", "AOS", "APA", "APD", "APH", "APTV", "ARE", 
    "ATO", "ATVI", "AVB", "AVGO", "AVY", "AWK", "AXP", "AZO", "BA", "BAC", "BAX", 
    "BBY", "BDX", "BEN", "BF-B", "BIIB", "BIO", "BK", "BKNG", "BKR", "BLK", "BLL", 
    "BMY", "BR", "BRK-B", "BSX", "BWA", "BXP", "C", "CAG", "CAH", "CARR", "CAT", 
    "CB", "CBRE", "CCI", "CCK", "CCL", "CDNS", "CDW", "CE", "CERN", "CF", "CFG", 
    "CHD", "CHRW", "CHTR", "CI", "Cinf", "CL", "CLX", "CMA", "CMCSA", "CME", "CMG", 
    "CMI", "CMS", "CNC", "CNP", "COF", "COG", "COO", "COP", "COST", "CPB", "CPRT", 
    "CRL", "CRM", "CSCO", "CSX", "CTAS", "CTLT", "CTSH", "CTVA", "CTXS", "CVS", 
    "CVX", "CZR", "D", "DAL", "DD", "DE", "DFS", "DG", "DGX", "DHI", "DHR", "DIS", 
    "DISCA", "DISCK", "DISH", "DLR", "DLTR", "DOV", "DOW", "DPZ", "DRE", "DRI", "DTE", 
    "DUK", "DVA", "DVN", "DXC", "DXCM", "EA", "EBAY", "ECL", "ED", "EFX", "EIX", 
    "EL", "EMN", "EMR", "ENPH", "EOG", "EQIX", "EQR", "ES", "ESS", "ETN", "ETR", 
    "ETSY", "EVRG", "EW", "EXC", "EXPD", "EXPE", "EXR", "F", "FANG", "FAST", "FB", 
    "FBHS", "FCX", "FDS", "FDX", "FE", "FFIV", "FIS", "FISV", "FITB", "FLT", "FMC", 
    "FOX", "FOXA", "FRC", "FRT", "FTNT", "FTV", "GD", "GE", "GILD", "GIS", "GL", 
    "GLW", "GM", "GOOG", "GOOGL", "GPC", "GPN", "GPS", "GRMN", "GS", "GWW", "HAL", 
    "HAS", "HBAN", "HCA", "HD", "HES", "HIG", "HII", "HLT", "HOLX", "HON", "HPE", 
    "HPQ", "HRL", "HSIC", "HST", "HSY", "HUM", "HWM", "IBM", "ICE", "IDXX", "IEX", 
    "IFF", "ILMN", "INCY", "INFO", "INTC", "INTU", "IP", "IPG", "IPGP", "IQV", "IR", 
    "IRM", "ISRG", "IT", "ITW", "IVZ", "J", "JBHT", "JCI", "JKHY", "JNJ", "JNPR", 
    "JPM", "K", "KEY", "KEYS", "KHC", "KIM", "KLAC", "KMB", "KMI", "KMX", "KO", 
    "KR", "KSu", "L", "LDOS", "LEG", "LEN", "LH", "LHX", "LIN", "LKQ", "LLY", "LMT", 
    "LNC", "LNT", "LOW", "LRCX", "LUMN", "LUV", "LVS", "LW", "LYB", "LYV", "MA", 
    "MAA", "MAR", "MAS", "MCD", "MCHP", "MCK", "MCO", "MDLZ", "MDT", "MET", "METV", 
    "MGM", "MHK", "MKC", "MKTX", "MLM", "MMC", "MMM", "MNST", "MO", "MOS", "MPC", 
    "MPWR", "MRK", "MRNA", "MRO", "MS", "MSCI", "MSFT", "MSI", "MTB", "MTD", "MU", 
    "MXIM", "MYL", "NCLH", "NDAQ", "NEE", "NEM", "NFLX", "NI", "NKE", "NLOK", "NLSN", 
    "NOC", "NOV", "NOW", "NRG", "NSC", "NTAP", "NTRS", "NUE", "NVDA", "NVR", "NWL", 
    "NWS", "NWSA", "O", "ODFL", "OGN", "OKE", "OMC", "ORLY", "ORCL", "OTIS", "OXY", 
    "PAYX", "PAYC", "PBCT", "PCAR", "PEAK", "PEG", "PEP", "PFE", "PFG", "PG", "PGR", 
    "PH", "PHM", "PKG", "PKI", "PLD", "PRU", "PRGO", "PSA", "PSX", "PTC", "PVH", 
    "PWR", "PXD", "QCOM", "QRVO", "RCL", "RE", "REG", "REGN", "RF", "RHI", "RJF", 
    "RL", "RMD", "ROK", "ROL", "ROP", "ROST", "RSG", "RTX", "SBAC", "SBUX", "SCCO", 
    "SCHW", "SEE", "SHW", "SIVB", "SJK", "SLB", "SLG", "SNA", "SNPS", "SO", "SPG", 
    "SPGI", "SRE", "STE", "STT", "STX", "STZ", "SWK", "SWKS", "SYF", "SYK", "SYY", 
    "T", "TAP", "TDG", "TDY", "TEL", "TER", "TFC", "TFX", "TGT", "TJX", "TMO", 
    "TMUS", "TPR", "TRV", "TRMB", "TROW", "TT", "TTWO", "TWTR", "TXN", "TXT", "TYL", 
    "UA", "UAA", "UAL", "UDR", "UHS", "ULTA", "UNH", "UNP", "UPS", "URI", "USB", 
    "V", "VFC", "VIAC", "VLO", "VMC", "VNO", "VRSN", "VRSK", "VRTX", "VTR", "VTRS", 
    "VZ", "WAB", "WAT", "WBA", "WBD", "WDC", "WEC", "WELL", "WFC", "WHR", "WLTW", 
    "WM", "WMB", "WMT", "WRB", "WRK", "WST", "WU", "WY", "WYNN", "XEL", "XLNX", 
    "XOM", "XRAY", "XYL", "YUM", "ZBH", "ZBRA", "ZION", "ZTS",

    # --- TOP 100 RUSSELL 2000 (HÖCHSTE MARKTKAPITALISIERUNG / LIQUIDITÄT) ---
    "PLTR", "SOFI", "HOOD", "AFRM", "UPST", "AI", "DKNG", "MARA", "RIOT", "COIN",
    "RIVN", "LCID", "NIO", "XPEV", "LI", "BABA", "PDD", "SNAP", "PINS", "UBER",
    "LYFT", "OPEN", "RUN", "SPWR", "NKLA", "CHPT", "BLNK", "BE", "PLUG", "FCEL",
    "QS", "SPCE", "VIR", "GME", "AMC", "BB", "TLRY", "CGC", "CRSR", "CLOV", 
    "MVIS", "NVAX", "OCGN", "INO", "BNGO", "KOSS", "EXPR", "WKHS", "GOEV", "CLSK",
    "HIVE", "BITF", "HUT", "ANY", "ATER", "PROG", "CEI", "MMAT", "SRNE", "XELA",
    "SENS", "ZOM", "CTRM", "AEI", "PHUN", "MARK", "BBIG", "GNUS", "TRCH", "VKG",
    "OLLI", "SAIA", "SFM", "WMS", "SSD", "SKYW", "ENSG", "COHR", "AAON", "MEDP",
    "LANC", "AMKR", "KNSL", "FIX", "AIT", "VNOM", "EPR", "CUBI", "MTH", "SLVM"
]

# Bereinigung: Doppelte Einträge löschen (manche Nasdaq Titel sind auch im S&P 500)
TICKER_LISTE = sorted(list(set(TICKER_LISTE)))

# --- SWING-ANALYSATOR FUNKTION ---
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
        
        # 1. RSI (Max 20 Pkt.)
        if 40 <= current_rsi <= 55:
            score += 20
        elif 30 <= current_rsi < 40:
            score += 15
        elif 55 < current_rsi <= 68:
            score += 12
            
        # 2. Trend (Max 20 Pkt.)
        if last_close > last_ema20 and last_close > last_sma50:
            score += 20
        elif last_close > last_ema20:
            score += 10
            
        # 3. MACD (Max 20 Pkt.)
        if last_macd > last_sig:
            score += 20
            
        # 4. Volumen (Max 15 Pkt.)
        if last_volume > avg_volume:
            score += 15
        else:
            score += 7
            
        # 5. 24h Momentum/Katalysator (Max 25 Pkt.)
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

# --- APP-OBERFLÄCHE ---
st.info(f"Der Scanner ist geladen mit **{len(TICKER_LISTE)}** einzigartigen Top-Aktien aus S&P 500, Nasdaq 100 & Russell 2000.")

if st.button("🚀 Mega-Markt-Scan jetzt starten"):
    fortschritts_balken = st.progress(0)
    status_text = st.empty()
    ergebnisse = []
    
    status_text.write("Scanne komplettes Markt-Universum über Hochgeschwindigkeits-Threads...")
    
    # max_workers=30 sorgt für absolute Spitzengeschwindigkeit beim parallelen Laden
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(analyze_single_stock, t) for t in TICKER_LISTE]
        
        for i, future in enumerate(futures):
            res = future.result()
            if res:
                ergebnisse.append(res)
            fortschritts_balken.progress((i + 1) / len(TICKER_LISTE))
            
    status_text.write("✅ Scan komplett abgeschlossen! Filtere die Top 100...")
    
    if ergebnisse:
        df = pd.DataFrame(ergebnisse)
        
        # SORTIERUNG: Höchster Swing-Score zuerst
        df = df.sort_values(by="Swing-Score", ascending=False).reset_index(drop=True)
        
        # STRIKTER FILTER: Nur die 100 allerbesten Aktien anzeigen
        df = df.head(100)
        
        def color_signal(val):
            if val == "STARKER KAUF": return "background-color: #2ecc71; color: white; font-weight: bold;"
            elif val == "KAUFEN": return "background-color: #27ae60; color: white;"
            elif val == "BEOBACHTEN": return "background-color: #f39c12; color: white;"
            else: return "background-color: #e74c3c; color: white;"

        st.markdown("### 🏆 Die 100 besten Swing-Trading Setups am Markt")
        styled_df = df.style.map(color_signal, subset=["Signal"])
        st.dataframe(styled_df, use_container_width=True, height=600)
        st.balloons()
    else:
        st.error("Es konnten keine Daten geladen werden.")
