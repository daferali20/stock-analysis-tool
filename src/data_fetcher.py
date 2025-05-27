import yfinance as yf
import pandas as pd

def fetch_stock_data(ticker):
    """جلب البيانات المالية للسهم"""
    stock = yf.Ticker(ticker)
    return {
        'income_stmt': stock.incomestmt,
        'balance_sheet': stock.balancesheet,
        'info': stock.info
    }