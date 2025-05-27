import requests
import yfinance as yf
from typing import Dict, Optional, Union
import pandas as pd
from functools import lru_cache
import yaml
import os
from bs4 import BeautifulSoup

class AnalystRatings:
    """
    جمع وتجميع تقييمات المحللين من مصادر متعددة:
    - Yahoo Finance (مباشر عبر API)
    - TradingView (ويب سكرابينغ)
    - TipRanks (API اختياري)
    """
    
    # تحميل إعدادات API من ملف التكوين
    @classmethod
    def _load_config(cls):
        try:
            with open('config/config.yml', 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    # التخزين المؤقت لطلبات Yahoo Finance
    @staticmethod
    @lru_cache(maxsize=100)
    def get_yahoo_analyst_ratings(ticker: str) -> Optional[Dict]:
        """جلب التقييمات من Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            ratings = {
                'mean_rating': info.get('recommendationMean'),
                'total_analysts': info.get('numberOfAnalystOpinions'),
                'breakdown': {
                    'strong_buy': info.get('recommendationKey', {}).get('strongBuy'),
                    'buy': info.get('recommendationKey', {}).get('buy'),
                    'hold': info.get('recommendationKey', {}).get('hold'),
                    'sell': info.get('recommendationKey', {}).get('sell'),
                    'strong_sell': info.get('recommendationKey', {}).get('strongSell')
                }
            }
            return {k: v for k, v in ratings.items() if v is not None}
        except Exception as e:
            print(f"[Yahoo] Error fetching ratings for {ticker}: {e}")
            return None

    @staticmethod
    def get_tradingview_rating(ticker: str) -> Optional[float]:
        """جلب التقييم من TradingView (ويب سكرابينغ)"""
        try:
            url = f"https://www.tradingview.com/symbols/{ticker}/"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            rating_element = soup.find('div', class_='analyst-ratings__score')
            return float(rating_element.text.strip()) if rating_element else None
        except Exception as e:
            print(f"[TradingView] Error scraping {ticker}: {e}")
            return None

    @staticmethod
    def get_tipranks_rating(ticker: str, api_key: str = None) -> Optional[Dict]:
        """جلب التقييم من TipRanks API"""
        if not api_key:
            return None
            
        try:
            url = f"https://api.tipranks.com/api/v2/stocks/{ticker}/consensus"
            headers = {'Authorization': f'Bearer {api_key}'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                'score': data.get('score'),  # 1-5
                'ratings_count': data.get('ratingsCount'),
                'bullish': data.get('bullish'),
                'bearish': data.get('bearish')
            }
        except Exception as e:
            print(f"[TipRanks] Error fetching data for {ticker}: {e}")
            return None

    @classmethod
    def aggregate_ratings(cls, ticker: str) -> Dict[str, Union[float, Dict]]:
        """تجميع التقييمات من جميع المصادر المتاحة"""
        config = cls._load_config()
        api_key = config.get('api_keys', {}).get('tipranks')
        
        # جلب البيانات من جميع المصادر
        sources = {
            'yahoo': cls.get_yahoo_analyst_ratings(ticker),
            'tradingview': cls.get_tradingview_rating(ticker),
            'tipranks': cls.get_tipranks_rating(ticker, api_key)
        }
        
        # حساب المتوسط المرجح
        weights = {'yahoo': 0.5, 'tradingview': 0.3, 'tipranks': 0.2}
        weighted_sum = 0.0
        total_weight = 0.0
        
        for source, data in sources.items():
            if not data:
                continue
                
            if source == 'yahoo' and data.get('mean_rating'):
                weighted_sum += data['mean_rating'] * weights[source]
                total_weight += weights[source]
            elif source == 'tradingview' and isinstance(data, float):
                weighted_sum += data * weights[source]
                total_weight += weights[source]
            elif source == 'tipranks' and data.get('score'):
                weighted_sum += data['score'] * weights['tipranks']
                total_weight += weights['tipranks']
        
        final_rating = round(weighted_sum / total_weight, 2) if total_weight > 0 else None
        
        return {
            'ticker': ticker,
            'final_rating': final_rating,
            'details': {k: v for k, v in sources.items() if v is not None},
            'timestamp': pd.Timestamp.now().isoformat()
        }


if __name__ == "__main__":
    # مثال للاستخدام مع اختبار جميع الوظائف
    test_ticker = "AAPL"
    
    print("\n" + "="*50)
    print(f"Testing Analyst Ratings for {test_ticker}")
    print("="*50)
    
    yahoo_data = AnalystRatings.get_yahoo_analyst_ratings(test_ticker)
    print("\nYahoo Finance Data:")
    print(pd.DataFrame.from_dict(yahoo_data, orient='index') if yahoo_data else "No data")
    
    tv_data = AnalystRatings.get_tradingview_rating(test_ticker)
    print(f"\nTradingView Rating: {tv_data}")
    
    aggregated = AnalystRatings.aggregate_ratings(test_ticker)
    print("\nAggregated Ratings:")
    print(pd.DataFrame.from_dict(aggregated, orient='index'))