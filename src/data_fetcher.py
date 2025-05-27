import yfinance as yf
import pandas as pd

def fetch_stock_data(ticker: str, period="1y", interval="1d") -> pd.DataFrame:
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval=interval)
        return data
    except Exception as e:
        print(f"Error fetching stock data for {ticker}: {e}")
        return pd.DataFrame()
