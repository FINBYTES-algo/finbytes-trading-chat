"""
OHLC API Client for fetching market data from Cloud Run API.
"""
import requests
import pandas as pd
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def fetch_ohlc_data(
    symbol: str,
    interval: str,
    start_date: str,
    end_date: str,
    api_url: str = "https://ohlca-date-api-331576355022.us-central1.run.app/data"
) -> pd.DataFrame:
    """
    Fetch OHLC data from Cloud Run API.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        interval: Time interval ('1d', '1w', '1mo')
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        api_url: Base API URL
        
    Returns:
        DataFrame with columns: Date (index), Open, High, Low, Close, Volume
        
    Raises:
        requests.RequestException: If API request fails
    """
    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "start_date": start_date,
        "end_date": end_date
    }
    
    try:
        logger.info(f"Fetching data for {symbol} ({interval}) from {start_date} to {end_date}")
        resp = requests.get(api_url, params=params, timeout=30)
        resp.raise_for_status()
        
        raw = resp.json()
        
        if "data" not in raw:
            raise ValueError("API response missing 'data' key")
            
        data = raw["data"]
        
        if not data:
            raise ValueError(f"No data returned for {symbol} in date range")
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        
        # Standardize column names
        df = df.rename(columns={
            "date": "Date",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume"
        })
        
        # Select and order columns
        df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
        df.set_index("Date", inplace=True)
        df.sort_index(inplace=True)
        
        logger.info(f"Successfully fetched {len(df)} rows")
        return df
        
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Error processing API response: {e}")
        raise

