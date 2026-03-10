import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="NR Breakout Scanner", layout="wide")

st.title("📈 NR4 / NR7 Breakout Scanner")

# -----------------------
# Paste NSE symbols here
# -----------------------

raw_symbols = """
NSE:3IINFOTECH,NSE:3MINDIA,NSE:3RDROCK,NSE:5PAISA,NSE:63MOONS,NSE:AARTIDRUGS,
NSE:AARTIIND,NSE:AAVAS,NSE:ABB,NSE:ABCAPITAL,NSE:ABFRL,NSE:ACC,NSE:ACCELYA,
NSE:ACE,NSE:ADANIENT,NSE:ADANIGREEN,NSE:ADANIPORTS,NSE:ADANIPOWER,NSE:ADANITRANS,
NSE:ADFFOODS,NSE:ADORWELD,NSE:ADVANIHOTR,NSE:ADVENZYMES,NSE:AEGISCHEM,NSE:AFFLE,
NSE:AHLUCONT,NSE:AIAENG,NSE:AJANTPHARM,NSE:AJMERA,NSE:AKZOINDIA,NSE:ALANKIT,
NSE:ALBERTDAVD,NSE:ALEMBICLTD,NSE:ALKEM,NSE:ALKYLAMINE,NSE:ALLCARGO,NSE:ALOKINDS,
NSE:AMARAJABAT,NSE:AMBER,NSE:AMBUJACEM,NSE:ANANTRAJ,NSE:APARINDS,NSE:APLAPOLLO,
NSE:APOLLOHOSP,NSE:APOLLOTYRE,NSE:ASHOKLEY,NSE:ASIANPAINT,NSE:ASTRAL,NSE:ATUL,
NSE:AUBANK,NSE:AUROPHARMA,NSE:AXISBANK,NSE:BAJAJFINSV,NSE:BAJFINANCE,
NSE:BALKRISIND,NSE:BANDHANBNK,NSE:BANKBARODA,NSE:BEL,NSE:BERGEPAINT,
NSE:BHARATFORG,NSE:BHARTIARTL,NSE:BHEL,NSE:BIOCON,NSE:BLUEDART,
NSE:BPCL,NSE:BRITANNIA,NSE:BSE,NSE:BSOFT,NSE:CANBK,NSE:CDSL,NSE:CEATLTD,
NSE:CHOLAFIN,NSE:CIPLA,NSE:COALINDIA,NSE:COLPAL,NSE:CONCOR,NSE:CROMPTON,
NSE:CUMMINSIND,NSE:CYIENT,NSE:DABUR,NSE:DALBHARAT,NSE:DBL,NSE:DCBBANK,
NSE:DEEPAKNTR,NSE:DELTA CORP,NSE:DIVISLAB,NSE:DIXON,NSE:DLF,NSE:DMART,
NSE:DRREDDY,NSE:EICHERMOT,NSE:EMAMILTD,NSE:ENDURANCE,NSE:EQUITAS,
NSE:ERIS,NSE:ESCORTS,NSE:EXIDEIND,NSE:FEDERALBNK,NSE:FINEORG,
NSE:FORTIS,NSE:GAIL,NSE:GLENMARK,NSE:GMRINFRA,NSE:GODREJCP,
NSE:GODREJPROP,NSE:GRANULES,NSE:GRAPHITE,NSE:GRASIM
"""

# convert NSE format to yfinance format
symbols = [s.replace("NSE:", "").strip() + ".NS" for s in raw_symbols.split(",")]

# -----------------------
# NR Pattern Logic
# -----------------------

def get_nr_pattern(df):

    ranges = (df["High"] - df["Low"]).values.tolist()

    if len(ranges) < 7:
        return None

    last_range = ranges[-1]

    for i in range(4,8):

        if last_range < min(ranges[-i:-1]):
            return f"NR{i}"

    return None


# -----------------------
# Breakout Logic
# -----------------------

def check_breakout(symbol):

    try:

        df = yf.download(symbol, period="10d", interval="1d", progress=False)

        if df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        pattern = get_nr_pattern(df)

        if not pattern:
            return None

        last_close = float(df["Close"].iloc[-1])
        prev_high = float(df["High"].iloc[-4:-1].max())

        if last_close > prev_high:

            return {
                "Stock": symbol,
                "Pattern": pattern,
                "Breakout Above": round(prev_high,2),
                "Current Price": round(last_close,2),
                "Signal": "BUY 🚨"
            }

    except:
        return None


# -----------------------
# UI Button
# -----------------------

if st.button("🚀 Run Full Market Scan"):

    results = []

    progress = st.progress(0)

    status = st.empty()

    total = len(symbols)

    for i,symbol in enumerate(symbols):

        status.text(f"Scanning {symbol}")

        res = check_breakout(symbol)

        if res:
            results.append(res)

        progress.progress((i+1)/total)

        time.sleep(0.1)

    status.text("Scan Complete ✅")

    if results:

        st.success(f"{len(results)} Breakouts Found")

        st.dataframe(pd.DataFrame(results), use_container_width=True)

    else:

        st.warning("No breakout found today")