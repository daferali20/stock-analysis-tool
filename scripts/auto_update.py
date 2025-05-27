from src.data_fetcher import fetch_stock_data
import pandas as pd

def update_data():
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    result = {}
    for ticker in tickers:
        df = fetch_stock_data(ticker)
        if not df.empty:
            result[ticker] = df.iloc[-1].to_dict()
    pd.DataFrame(result).T.to_csv('data/updated_stocks.csv')

if __name__ == "__main__":
    update_data()
