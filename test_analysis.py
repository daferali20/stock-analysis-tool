from src.financial_analysis import calculate_composite_score

def test_composite_score():
    score = calculate_composite_score("AAPL")
    assert score is None or (0 <= score <= 100)