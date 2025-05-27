from .analyst_ratings import AnalystRatings
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def calculate_composite_score(ticker: str) -> float:
    """
    تحويل التقييم المجمع إلى نسبة مئوية من 100.
    """
    try:
        ratings = AnalystRatings.aggregate_ratings(ticker)
        if ratings['final_rating']:
            return ratings['final_rating'] * 20  # مقياس من 0 إلى 100
        else:
            return None
    except Exception as e:
        logger.error(f"خطأ في حساب composite score للسهم {ticker}: {e}")
        return None

def calculate_roe(income_stmt, balance_sheet) -> float:
    """
    حساب العائد على حقوق المساهمين (ROE).
    """
    try:
        net_income = income_stmt.loc['Net Income'].iloc[0]
        equity = balance_sheet.loc['Stockholders Equity'].iloc[0]
        return round((net_income / equity) * 100, 2)
    except Exception as e:
        logger.error(f"خطأ في حساب ROE: {e}")
        return None

def calculate_de_ratio(balance_sheet) -> float:
    """
    حساب نسبة الدين إلى حقوق الملكية (Debt-to-Equity).
    """
    try:
        total_liabilities = balance_sheet.loc['Total Liab'].iloc[0]
        equity = balance_sheet.loc['Stockholders Equity'].iloc[0]
        return round(total_liabilities / equity, 2)
    except Exception as e:
        logger.error(f"خطأ في حساب D/E Ratio: {e}")
        return None
