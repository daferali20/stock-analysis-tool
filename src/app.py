
import streamlit as st
from src.data_fetcher import fetch_stock_data
from src.financial_analysis import *
from src.analyst_ratings import AnalystRatings

def display_ratings(ticker):
    ratings = AnalystRatings.aggregate_ratings(ticker)
    st.metric("التقييم المركب", ratings['final_rating'])
    st.json(ratings['details'])  # لعرض التفاصيل
def main():
    st.title("Stock Analysis Dashboard")
    # ... (كود الواجهة)

if __name__ == "__main__":
    main()