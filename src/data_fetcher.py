import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def fetch_stock_data(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    جلب بيانات السهم التاريخية باستخدام مكتبة yfinance.
    
    المعلمات:
    - ticker: رمز السهم (مثل "AAPL").
    - period: الفترة الزمنية (مثل "1y" للسنة الماضية).
    - interval: الفاصل الزمني بين البيانات (مثل "1d" ليوميًا).
    
    العودة:
    - DataFrame يحتوي على بيانات السهم.
    """
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if data.empty:
            logger.warning(f"لم يتم العثور على بيانات للسهم: {ticker}")
            return pd.DataFrame()
        data.dropna(inplace=True)
        return data
    except Exception as e:
        logger.error(f"خطأ أثناء جلب بيانات السهم {ticker}: {e}")
        return pd.DataFrame()
