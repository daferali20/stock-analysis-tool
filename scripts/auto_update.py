import time
import src.data_fetcher as df

TICKERS = ['AAPL', 'TSLA', 'MSFT']  # قائمة الأسهم المتابعة

def update_data():
    for ticker in TICKERS:
        data = df.fetch_stock_data(ticker)
        # ... (كود الحفظ في CSV أو قاعدة بيانات)

if __name__ == "__main__":
    update_data()