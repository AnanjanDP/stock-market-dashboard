import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv



load_dotenv()
API_URL = os.getenv("API_URL")

st.set_page_config(page_title="Stock Analytics Dashboard", layout="wide")

st.title("Stock Analytics Dashboard")

# Sidebar

stock_options = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Tesla (TSLA)": "TSLA",
    "Amazon (AMZN)": "AMZN",
    "Google (GOOGL)": "GOOGL",
}

selected_stock = st.sidebar.selectbox(
    "Select Stock",
    list(stock_options.keys())
)

period = st.sidebar.selectbox(
    "Select Time Range",
    ["1mo", "6mo", "1y", "5y"]
)

show_rsi = st.sidebar.checkbox("Show RSI", True)
show_macd = st.sidebar.checkbox("Show MACD", True)

ticker = stock_options[selected_stock]

# Cached API Call


@st.cache_data
def fetch_stock(ticker, period):
    response = requests.get(f"{API_URL}/stock/{ticker}?period={period}")
    return response.json()

data = fetch_stock(ticker, period)

if "error" in data:
    st.error(data["error"])
    st.stop()

# Metric Cards


col1, col2, col3, col4 = st.columns(4)

col1.metric("Current Price", f"${data['latest_price']}")
col2.metric("Daily Change %", f"{data['daily_change']}%")
col3.metric("52W High", f"${data['high_52w']}")
col4.metric("52W Low", f"${data['low_52w']}")

# DataFrame

df = pd.DataFrame({
    "Date": data["dates"],
    "Close": data["close"],
    "SMA 50": data["sma_50"],
    "SMA 200": data["sma_200"],
    "RSI": data["rsi"],
    "MACD": data["macd"],
    "Signal": data["signal"],
})

df.set_index("Date", inplace=True)

# Charts


st.subheader("Price & Moving Averages")
st.line_chart(df[["Close", "SMA 50", "SMA 200"]])

if show_rsi:
    st.subheader("RSI Indicator")
    st.line_chart(df[["RSI"]])

if show_macd:
    st.subheader("MACD Indicator")
    st.line_chart(df[["MACD", "Signal"]])


st.download_button(
    label="Download Data as CSV",
    data=df.to_csv().encode("utf-8"),
    file_name=f"{ticker}_data.csv",
    mime="text/csv"
)

st.caption("Built with FastAPI + Streamlit")
