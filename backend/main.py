from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App Setup

app = FastAPI(title="Stock Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes

@app.get("/")
def root():
    return {"message": "Stock Analytics API Running 🚀"}


@app.get("/stock/{ticker}")
def get_stock_data(
    ticker: str,
    period: str = Query("1y", description="Time period: 1mo, 6mo, 1y, 5y")
):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)

        if df.empty:
            return {"error": "No data found"}


        # Moving Averages

        df["SMA_50"] = df["Close"].rolling(50).mean()
        df["SMA_200"] = df["Close"].rolling(200).mean()

        # RSI

        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))


        # MACD

        df["EMA_12"] = df["Close"].ewm(span=12, adjust=False).mean()
        df["EMA_26"] = df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD"] = df["EMA_12"] - df["EMA_26"]
        df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

        latest_price = float(df["Close"].iloc[-1])
        daily_change = (
            (df["Close"].iloc[-1] - df["Close"].iloc[-2])
            / df["Close"].iloc[-2]
        ) * 100

        high_52w = float(df["High"].max())
        low_52w = float(df["Low"].min())

        return {
            "ticker": ticker.upper(),
            "latest_price": round(latest_price, 2),
            "daily_change": round(daily_change, 2),
            "high_52w": round(high_52w, 2),
            "low_52w": round(low_52w, 2),
            "dates": df.index.strftime("%Y-%m-%d").tolist(),
            "close": df["Close"].fillna(0).tolist(),
            "sma_50": df["SMA_50"].fillna(0).tolist(),
            "sma_200": df["SMA_200"].fillna(0).tolist(),
            "rsi": df["RSI"].fillna(0).tolist(),
            "macd": df["MACD"].fillna(0).tolist(),
            "signal": df["Signal"].fillna(0).tolist(),
        }

    except Exception as e:
        logger.error(str(e))
        return {"error": str(e)}
