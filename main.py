import streamlit as st
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(page_title="NR Breakout Scanner", layout="wide")

st.title("📈 NR4 / NR5 / NR6 / NR7 Breakout Scanner")

# ---------------------------------
# Load ALL NSE Stocks Automatically
# ---------------------------------

@st.cache_data
def load_symbols():

    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

    df = pd.read_csv(url)

    symbols = [s + ".NS" for s in df["SYMBOL"].tolist()]

    return symbols


symbols = load_symbols()

st.write("Total Stocks Loaded:", len(symbols))

# -----------------------
# NR Pattern Logic
# -----------------------

def get_nr_pattern(df):

    ranges = (df["High"] - df["Low"]).values.tolist()

    if len(ranges) < 7:
        return None

    last_range = ranges[-1]

    for i in range(4, 8):

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

        three_day_high = float(df["High"].iloc[-4:-1].max())

        if last_close > three_day_high:

            return {
                "Stock": symbol,
                "Pattern": pattern,
                "Breakout Above": round(three_day_high,2),
                "Current Price": round(last_close,2),
                "Signal": "BUY 🚨"
            }

    except:
        return None


# -----------------------
# Scanner Function
# -----------------------

def run_scan(symbols):

    results = []

    progress = st.progress(0)
    status = st.empty()

    total = len(symbols)

    with ThreadPoolExecutor(max_workers=20) as executor:

        futures = {executor.submit(check_breakout, s): s for s in symbols}

        for i, future in enumerate(as_completed(futures)):

            res = future.result()

            if res:
                results.append(res)

            progress.progress((i+1)/total)

            status.text(f"Scanned {i+1}/{total} stocks")

    return results


# -----------------------
# UI Button
# -----------------------

if st.button("🚀 Run Full Market Scan"):

    results = run_scan(symbols)

    st.success("Scan Complete ✅")

    if results:

        st.success(f"{len(results)} Breakouts Found")

        st.dataframe(pd.DataFrame(results), use_container_width=True)

    else:

        st.warning("No breakout found today")
