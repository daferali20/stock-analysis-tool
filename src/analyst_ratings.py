import requests
import yfinance as yf
from typing import Dict, Optional, Union
import pandas as pd
from functools import lru_cache
from bs4 import BeautifulSoup
import yaml

class AnalystRatings:
    @classmethod
    def _load_config(cls):
        try:
            with open('config/config.yml', 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    @staticmethod
    @lru_cache(maxsize=100)
    def get_yahoo_analyst_ratings(ticker: str) -> Optional[Dict]:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            ratings = {
                'mean_rating': info.get('recommendationMean'),
                'total_analysts': info.get('numberOfAnalystOpinions'),
                'breakdown': info.get('recommendationKey')
            }
            return {k: v for k, v in ratings.items() if v is not None}
        except Exception as e:
            print(f"[Yahoo] Error fetching ratings for {ticker}: {e}")
            return None

    @staticmethod
    def get_tradingview_rating(ticker: str) -> Optional[float]:
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
    def get_polygon_rating(ticker: str, api_key: str) -> Optional[Dict]:
        """
        استخدام API من Polygon.io لجلب بيانات تقييم المحللين أو بيانات الأسهم.
        يمكن تعديل نقطة النهاية حسب توفر البيانات.
        """
        try:
            url = f"https://api.polygon.io/v3/reference/analysts/{ticker}?apiKey={api_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            # مثال على معالجة الرد - يجب تعديل حسب هيكل الرد الحقيقي من Polygon
            if 'results' in data and len(data['results']) > 0:
                # هنا نأخذ متوسط تقييمات المحللين (كمثال)
                scores = [r.get('rating') for r in data['results'] if r.get('rating') is not None]
                if scores:
                    mean_rating = sum(scores) / len(scores)
                    return {
                        'mean_rating': mean_rating,
                        'analyst_count': len(scores),
                        'details': data['results']
                    }
            return None
        except Exception as e:
            print(f"[Polygon.io] Error fetching ratings for {ticker}: {e}")
            return None

    @classmethod
    def aggregate_ratings(cls, ticker: str) -> Dict[str, Union[float, Dict]]:
        config = cls._load_config()
        polygon_api_key = config.get('api_keys', {}).get('polygon')
        sources = {
            'yahoo': cls.get_yahoo_analyst_ratings(ticker),
            'tradingview': cls.get_tradingview_rating(ticker),
        }

        if polygon_api_key:
            sources['polygon'] = cls.get_polygon_rating(ticker, polygon_api_key)

        weights = {'yahoo': 0.5, 'tradingview': 0.3, 'polygon': 0.2}
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
            elif source == 'polygon' and data.get('mean_rating'):
                weighted_sum += data['mean_rating'] * weights[source]
                total_weight += weights[source]

        final_rating = round(weighted_sum / total_weight, 2) if total_weight > 0 else None
        return {
            'ticker': ticker,
            'final_rating': final_rating,
            'details': {k: v for k, v in sources.items() if v is not None},
            'timestamp': pd.Timestamp.now().isoformat()
        }
