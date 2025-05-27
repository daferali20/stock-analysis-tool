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

    @classmethod
    def aggregate_ratings(cls, ticker: str) -> Dict[str, Union[float, Dict]]:
        config = cls._load_config()
        sources = {
            'yahoo': cls.get_yahoo_analyst_ratings(ticker),
            'tradingview': cls.get_tradingview_rating(ticker)
        }

        weights = {'yahoo': 0.6, 'tradingview': 0.4}
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

        final_rating = round(weighted_sum / total_weight, 2) if total_weight > 0 else None
        return {
            'ticker': ticker,
            'final_rating': final_rating,
            'details': {k: v for k, v in sources.items() if v is not None},
            'timestamp': pd.Timestamp.now().isoformat()
        }
