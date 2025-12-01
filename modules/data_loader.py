"""
Data Loader Module
Handles loading options data from folder structure
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class OptionsDataLoader:
    """Loads options data from folder-based structure"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self._expiry_folders = None
        self._strike_cache = {}
        self._data_cache = {}
        
        if not self.base_path.exists():
            raise ValueError(f"Base path does not exist: {base_path}")
        
        self._scan_expiries()
    
    def _scan_expiries(self):
        self._expiry_folders = {}
        for folder in self.base_path.iterdir():
            if folder.is_dir():
                try:
                    expiry_date = datetime.strptime(folder.name, '%Y-%m-%d').date()
                    self._expiry_folders[expiry_date] = folder
                except ValueError:
                    continue
        logger.info(f"Found {len(self._expiry_folders)} expiry folders")
    
    def get_available_expiries(self) -> List[datetime]:
        return sorted(self._expiry_folders.keys())
    
    def get_expiry_for_date(self, trade_date: datetime) -> Optional[datetime]:
        if isinstance(trade_date, datetime):
            trade_date = trade_date.date()
        for expiry in self.get_available_expiries():
            if expiry >= trade_date:
                return expiry
        return None
    
    def get_available_strikes(self, expiry_date) -> Dict[str, List[float]]:
        if isinstance(expiry_date, datetime):
            expiry_date = expiry_date.date()
        
        cache_key = str(expiry_date)
        if cache_key in self._strike_cache:
            return self._strike_cache[cache_key]
        
        folder = self._expiry_folders.get(expiry_date)
        if not folder:
            return {'CE': [], 'PE': []}
        
        strikes = {'CE': [], 'PE': []}
        for file in folder.glob('*.csv'):
            parts = file.stem.rsplit('_', 1)
            if len(parts) == 2:
                try:
                    strike = float(parts[0])
                    opt_type = parts[1].upper()
                    if opt_type in strikes:
                        strikes[opt_type].append(strike)
                except ValueError:
                    continue
        
        strikes['CE'] = sorted(set(strikes['CE']))
        strikes['PE'] = sorted(set(strikes['PE']))
        self._strike_cache[cache_key] = strikes
        return strikes
    
    def load_option_data(self, expiry_date, strike: float, option_type: str) -> Optional[pd.DataFrame]:
        if isinstance(expiry_date, datetime):
            expiry_date = expiry_date.date()
        
        cache_key = f"{expiry_date}_{strike}_{option_type}"
        if cache_key in self._data_cache:
            return self._data_cache[cache_key]
        
        folder = self._expiry_folders.get(expiry_date)
        if not folder:
            return None
        
        file_name = f"{strike}_{option_type.upper()}.csv"
        file_path = folder / file_name
        
        if not file_path.exists():
            int_strike = int(strike)
            file_name = f"{int_strike}.0_{option_type.upper()}.csv"
            file_path = folder / file_name
        
        if not file_path.exists():
            return None
        
        try:
            df = pd.read_csv(file_path)
            df = self._standardize_dataframe(df)
            df['strike'] = strike
            df['option_type'] = option_type.upper()
            self._data_cache[cache_key] = df
            return df
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None
    
    def _standardize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df.columns = df.columns.str.lower().str.strip()
        datetime_cols = ['datetime', 'date', 'time', 'timestamp']
        dt_col = None
        for col in datetime_cols:
            if col in df.columns:
                dt_col = col
                break
        if dt_col:
            df['datetime'] = pd.to_datetime(df[dt_col], errors='coerce')
        numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'oi']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    
    def get_option_price_at_time(self, expiry_date, strike: float, option_type: str,
                                  timestamp: datetime, tolerance_minutes: int = 5) -> Optional[Dict]:
        df = self.load_option_data(expiry_date, strike, option_type)
        if df is None or df.empty:
            return None
        
        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)
        
        df = df[df['datetime'].dt.date == timestamp.date()]
        if df.empty:
            return None
        
        time_diff = abs(df['datetime'] - timestamp)
        min_diff_idx = time_diff.idxmin()
        
        if time_diff[min_diff_idx] > timedelta(minutes=tolerance_minutes):
            return None
        
        row = df.loc[min_diff_idx]
        return {
            'datetime': row['datetime'],
            'open': float(row['open']),
            'high': float(row['high']),
            'low': float(row['low']),
            'close': float(row['close']),
            'volume': int(row.get('volume', 0)),
            'oi': int(row.get('oi', 0))
        }
    
    def clear_cache(self):
        self._data_cache.clear()
        self._strike_cache.clear()
    
    def get_info(self) -> Dict[str, Any]:
        expiries = self.get_available_expiries()
        return {
            'base_path': str(self.base_path),
            'total_expiries': len(expiries),
            'date_range': {'start': str(expiries[0]) if expiries else None, 'end': str(expiries[-1]) if expiries else None},
            'expiries': [str(e) for e in expiries]
        }


class SpotDataLoader:
    """Loads spot price data"""
    
    def __init__(self, file_or_folder_path: str):
        self.path = Path(file_or_folder_path)
        self._data = None
        self._is_folder = self.path.is_dir()
        if not self._is_folder:
            self._load_single_file()
    
    def _load_single_file(self):
        if not self.path.exists():
            raise ValueError(f"File not found: {self.path}")
        self._data = pd.read_csv(self.path)
        self._standardize_data()
    
    def _standardize_data(self):
        if self._data is None:
            return
        self._data.columns = self._data.columns.str.lower().str.strip()
        if 'datetime' in self._data.columns:
            self._data['datetime'] = pd.to_datetime(self._data['datetime'], errors='coerce')
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            if col in self._data.columns:
                self._data[col] = pd.to_numeric(self._data[col], errors='coerce')
        self._data = self._data.sort_values('datetime')
    
    def get_data_for_date(self, trade_date) -> pd.DataFrame:
        if isinstance(trade_date, str):
            trade_date = pd.to_datetime(trade_date).date()
        elif isinstance(trade_date, datetime):
            trade_date = trade_date.date()
        
        if self._is_folder:
            patterns = [f"{trade_date}.csv", f"{trade_date.strftime('%Y%m%d')}.csv"]
            for pattern in patterns:
                file_path = self.path / pattern
                if file_path.exists():
                    df = pd.read_csv(file_path)
                    df.columns = df.columns.str.lower().str.strip()
                    if 'datetime' in df.columns:
                        df['datetime'] = pd.to_datetime(df['datetime'])
                    return df
            return pd.DataFrame()
        else:
            if self._data is None or 'datetime' not in self._data.columns:
                return pd.DataFrame()
            mask = self._data['datetime'].dt.date == trade_date
            return self._data[mask].copy()
    
    def get_spot_price_at_time(self, timestamp: datetime, tolerance_minutes: int = 5) -> Optional[float]:
        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)
        df = self.get_data_for_date(timestamp.date())
        if df.empty:
            return None
        time_diff = abs(df['datetime'] - timestamp)
        min_diff_idx = time_diff.idxmin()
        if time_diff[min_diff_idx] > timedelta(minutes=tolerance_minutes):
            return None
        return float(df.loc[min_diff_idx, 'close'])
    
    def get_available_dates(self) -> List[datetime]:
        if self._is_folder:
            dates = []
            for f in self.path.glob('*.csv'):
                try:
                    dt = pd.to_datetime(f.stem).date()
                    dates.append(dt)
                except:
                    continue
            return sorted(dates)
        else:
            if self._data is None or 'datetime' not in self._data.columns:
                return []
            return sorted(self._data['datetime'].dt.date.unique())


def load_backtest_data(options_folder: str, spot_file_or_folder: str, trade_dates: List = None):
    """Initialize data loaders"""
    options_loader = OptionsDataLoader(options_folder)
    spot_loader = SpotDataLoader(spot_file_or_folder)
    return options_loader, spot_loader
