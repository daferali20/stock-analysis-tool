import streamlit as st
from data_fetcher import fetch_stock_data
from src.financial_analysis import *
from src.analyst_ratings import AnalystRatings
from src.alerts import check_alerts
import streamlit as st

def display_alerts(analysis_result):
    alerts = check_alerts(analysis_result)
    for alert in alerts:
        st.error(alert)  # يمكنك استبداله بـ st.toast أو st.markdown بتنسيق خاص

def display_ratings(ticker):
    try:
        ratings = AnalystRatings.aggregate_ratings(ticker)
        if ratings:
            st.metric("التقييم المركب", ratings.get('final_rating', 'غير متوفر'))
            st.subheader("تفاصيل التحليل")
            st.json(ratings.get('details', {}))
        else:
            st.warning("لم يتم العثور على تقييمات للمحللين.")
    except Exception as e:
        st.error(f"حدث خطأ أثناء جلب التقييمات: {e}")

def main():
    st.title("لوحة تحليل الأسهم")
    ticker = st.text_input("أدخل رمز السهم (مثل AAPL):").upper().strip()

    if st.button("عرض التحليل"):
        if not ticker:
            st.warning("يرجى إدخال رمز السهم.")
            return
        
        try:
            st.subheader("بيانات السهم")
            data = fetch_stock_data(ticker)
            st.write(data.head())  # مثال: عرض أول البيانات

            st.subheader("تحليل المحللين")
            display_ratings(ticker)
        except Exception as e:
            st.error(f"حدث خطأ أثناء تحليل السهم: {e}")

if __name__ == "__main__":
    main()
