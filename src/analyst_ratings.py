import requests
import yfinance as yf
from typing import Dict, Optional, Union
import pandas as pd
from functools import lru_cache
import os
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AnalystRatings:
    """
    جمع وتجميع تقييمات المحللين من:
    - Yahoo Finance
    - TradingView
    - TipRanks
    """

    @staticmethod
    @lru_cache(maxsize=100)
    def get_yahoo_analyst_ratings(ticker: str) -> Optional[Dict]:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            mean_rating = info.get('recommendationMean')
            total_analysts = info.get('numberOfAnalystOpinions')
            return {
                'mean_rating': mean_rating,
                'total_analysts': total_analysts
            } if mean_rating else None
        except Exception as e:
            logger.error(f"[Yahoo] Error fetching ratings for {ticker}: {e}")
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
            logger.error(f"[TradingView] Error scraping {ticker}: {e}")
            return None

    @staticmethod
    def get_tipranks_rating(ticker: str) -> Optional[Dict]:
        api_key = os.getenv("TIPRANKS_API_KEY")
        if not api_key:
            logger.warning("No TipRanks API key found.")
            return None

        try:
            url = f"https://api.tipranks.com/api/v2/stocks/{ticker}/consensus"
            headers = {'Authorization': f'Bearer {api_key}'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                'score': data.get('score'),
                'ratings_count': data.get('ratingsCount'),
                'bullish': data.get('bullish'),
                'bearish': data.get('bearish')
            }
        except Exception as e:
            logger.error(f"[TipRanks] Error fetching data for {ticker}: {e}")
            return None

    @classmethod
    def aggregate_ratings(cls, ticker: str) -> Dict[str, Union[float, Dict]]:
        sources = {
            'yahoo': cls.get_yahoo_analyst_ratings(ticker),
            'tradingview': cls.get_tradingview_rating(ticker),
            'tipranks': cls.get_tipranks_rating(ticker)
        }

        weights = {'yahoo': 0.5, 'tradingview': 0.3, 'tipranks': 0.2}
        weighted_sum = 0.0
        total_weight = 0.0

        for source, data in sources.items():
            if not data:
                continue
            if source == 'yahoo' and isinstance(data, dict) and data.get('mean_rating'):
                weighted_sum += data['mean_rating'] * weights[source]
                total_weight += weights[source]
            elif source == 'tradingview' and isinstance(data, float):
                weighted_sum += data * weights[source]
                total_weight += weights[source]
            elif source == 'tipranks' and isinstance(data, dict) and data.get('score'):
                weighted_sum += data['score'] * weights[source]
                total_weight += weights[source]

        final_rating = round(weighted_sum / total_weight, 2) if total_weight > 0 else None

        return {
            'ticker': ticker,
            'final_rating': final_rating,
            'details': {k: v for k, v in sources.items() if v is not None},
            'timestamp': pd.Timestamp.now().isoformat(),
            'error': None if total_weight > 0 else 'لم تتوفر تقييمات من أي مصدر'
        }
