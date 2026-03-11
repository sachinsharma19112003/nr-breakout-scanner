import streamlit as st
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(page_title="NR Breakout Scanner", layout="wide")

st.title("📈 NR4 / NR5 / NR6 / NR7 Breakout Scanner")

# ----------------------------------
# Load NSE Stocks
# ----------------------------------

@st.cache_data
def load_symbols():

    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

    df = pd.read_csv(url)

    symbols = [s + ".NS" for s in df["SYMBOL"].tolist()]

    return symbols


symbols = load_symbols()

st.write("Total Stocks Loaded:", len(symbols))


# ----------------------------------
# NR Pattern Logic
# ----------------------------------

def get_nr_pattern(ranges):

    last_range = ranges[-1]

    for i in range(4,8):

        if last_range < min(ranges[-i:-1]):

            return f"NR{i}"

    return None


# ----------------------------------
# TODAY NR BREAKOUT
# ----------------------------------

def today_breakout(symbol):

    try:

        df = yf.download(symbol, period="10d", interval="1d", progress=False)

        if df.empty or len(df) < 7:
            return None

        ranges = (df["High"] - df["Low"]).tolist()

        pattern = get_nr_pattern(ranges)

        if not pattern:
            return None

        nr_high = float(df["High"].iloc[-1])

        price = float(df["Close"].iloc[-1])

        if price > nr_high:

            return {
                "Stock": symbol,
                "Pattern": pattern,
                "NR High": round(nr_high,2),
                "Price": round(price,2),
                "Signal": "Today Breakout 🚀"
            }

    except:
        return None


# ----------------------------------
# FIRST DAY BREAKOUT (Yesterday NR)
# ----------------------------------

def first_day_breakout(symbol):

    try:

        df = yf.download(symbol, period="10d", interval="1d", progress=False)

        if df.empty or len(df) < 7:
            return None

        ranges = (df["High"] - df["Low"]).tolist()

        nr_range = ranges[-2]

        pattern = None

        for i in range(4,8):

            if nr_range < min(ranges[-i-1:-2]):

                pattern = f"NR{i}"

        if not pattern:
            return None

        nr_high = float(df["High"].iloc[-2])

        price = float(df["Close"].iloc[-1])

        if price > nr_high:

            return {
                "Stock": symbol,
                "Pattern": pattern,
                "NR Day High": round(nr_high,2),
                "Price": round(price,2),
                "Signal": "First Day Breakout 🔥"
            }

    except:
        return None


# ----------------------------------
# SCANNER
# ----------------------------------

def run_scan(symbols, mode):

    results = []

    progress = st.progress(0)

    status = st.empty()

    total = len(symbols)

    with ThreadPoolExecutor(max_workers=40) as executor:

        if mode == "today":

            futures = {executor.submit(today_breakout, s): s for s in symbols}

        else:

            futures = {executor.submit(first_day_breakout, s): s for s in symbols}

        for i, future in enumerate(as_completed(futures)):

            res = future.result()

            if res:
                results.append(res)

            progress.progress((i+1)/total)

            status.text(f"Scanning {i+1}/{total} stocks")

    return results


# ----------------------------------
# BUTTONS
# ----------------------------------

col1, col2 = st.columns(2)

with col1:

    if st.button("🚀 Scan Today NR Breakout"):

        results = run_scan(symbols,"today")

        st.success("Scan Complete")

        if results:

            st.dataframe(pd.DataFrame(results), use_container_width=True)

        else:

            st.warning("No breakout found")


with col2:

    if st.button("🔥 Scan First Day Breakout"):

        results = run_scan(symbols,"first")

        st.success("Scan Complete")

        if results:

            st.dataframe(pd.DataFrame(results), use_container_width=True)

        else:

            st.warning("No first day breakout found")
