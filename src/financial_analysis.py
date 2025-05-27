from analyst_ratings import AnalystRatings

def calculate_composite_score(ticker):
    ratings = AnalystRatings.aggregate_ratings(ticker)
    return ratings['final_rating'] * 20  # لتحويله إلى نسبة مئوية
def calculate_roe(income_stmt, balance_sheet):
    net_income = income_stmt.loc['Net Income'].iloc[0]
    equity = balance_sheet.loc['Stockholders Equity'].iloc[0]
    return (net_income / equity) * 100

def calculate_de_ratio(balance_sheet):
    # ... (كود حساب نسبة الدين/حقوق الملكية)
