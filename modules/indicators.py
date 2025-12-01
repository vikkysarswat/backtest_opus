"""
Technical Indicators Module
Provides vectorized calculation of various technical indicators
"""

import numpy as np
import pandas as pd
from typing import Dict, Any


class IndicatorCalculator:
    """Vectorized technical indicator calculator"""
    
    def __init__(self):
        self.indicator_map = {
            'SMA': self.sma, 'EMA': self.ema, 'WMA': self.wma,
            'DEMA': self.dema, 'TEMA': self.tema, 'RSI': self.rsi,
            'STOCH': self.stochastic, 'CCI': self.cci, 'WILLR': self.williams_r,
            'ATR': self.atr, 'BBANDS': self.bollinger_bands,
            'KC': self.keltner_channel, 'MACD': self.macd, 'ADX': self.adx,
            'MOM': self.momentum, 'ROC': self.rate_of_change,
            'OBV': self.obv, 'VWAP': self.vwap
        }
    
    def calculate(self, df: pd.DataFrame, indicator: str, params: Dict[str, Any] = None):
        if params is None:
            params = {}
        indicator_func = self.indicator_map.get(indicator.upper())
        if not indicator_func:
            raise ValueError(f"Unknown indicator: {indicator}")
        return indicator_func(df, **params)
    
    # Moving Averages
    def sma(self, df, period=20, column='close'):
        return df[column].rolling(window=period, min_periods=1).mean()
    
    def ema(self, df, period=20, column='close'):
        return df[column].ewm(span=period, adjust=False, min_periods=1).mean()
    
    def wma(self, df, period=20, column='close'):
        weights = np.arange(1, period + 1)
        def wavg(x):
            if len(x) < period:
                w = np.arange(1, len(x) + 1)
                return np.dot(x, w) / w.sum()
            return np.dot(x, weights) / weights.sum()
        return df[column].rolling(window=period, min_periods=1).apply(wavg, raw=True)
    
    def dema(self, df, period=20, column='close'):
        ema1 = self.ema(df, period, column)
        ema2 = ema1.ewm(span=period, adjust=False, min_periods=1).mean()
        return 2 * ema1 - ema2
    
    def tema(self, df, period=20, column='close'):
        ema1 = self.ema(df, period, column)
        ema2 = ema1.ewm(span=period, adjust=False, min_periods=1).mean()
        ema3 = ema2.ewm(span=period, adjust=False, min_periods=1).mean()
        return 3 * ema1 - 3 * ema2 + ema3
    
    # Oscillators
    def rsi(self, df, period=14, column='close'):
        delta = df[column].diff()
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)
        avg_gain = gain.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
        avg_loss = loss.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        return (100 - (100 / (1 + rs))).fillna(50)
    
    def stochastic(self, df, k_period=14, d_period=3):
        lowest = df['low'].rolling(window=k_period, min_periods=1).min()
        highest = df['high'].rolling(window=k_period, min_periods=1).max()
        k = 100 * (df['close'] - lowest) / (highest - lowest).replace(0, np.nan)
        k = k.fillna(50)
        d = k.rolling(window=d_period, min_periods=1).mean()
        return {'k': k, 'd': d}
    
    def cci(self, df, period=20):
        tp = (df['high'] + df['low'] + df['close']) / 3
        sma = tp.rolling(window=period, min_periods=1).mean()
        mad = tp.rolling(window=period, min_periods=1).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
        return ((tp - sma) / (0.015 * mad).replace(0, np.nan)).fillna(0)
    
    def williams_r(self, df, period=14):
        highest = df['high'].rolling(window=period, min_periods=1).max()
        lowest = df['low'].rolling(window=period, min_periods=1).min()
        return (-100 * (highest - df['close']) / (highest - lowest).replace(0, np.nan)).fillna(-50)
    
    # Volatility
    def atr(self, df, period=14):
        hl = df['high'] - df['low']
        hc = np.abs(df['high'] - df['close'].shift())
        lc = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
        return tr.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    
    def bollinger_bands(self, df, period=20, std_dev=2.0, column='close'):
        middle = df[column].rolling(window=period, min_periods=1).mean()
        std = df[column].rolling(window=period, min_periods=1).std()
        return {'upper': middle + std * std_dev, 'middle': middle, 'lower': middle - std * std_dev}
    
    def keltner_channel(self, df, period=20, multiplier=2.0):
        tp = (df['high'] + df['low'] + df['close']) / 3
        middle = tp.ewm(span=period, adjust=False, min_periods=1).mean()
        atr = self.atr(df, period)
        return {'upper': middle + atr * multiplier, 'middle': middle, 'lower': middle - atr * multiplier}
    
    # Momentum
    def macd(self, df, fast_period=12, slow_period=26, signal_period=9, column='close'):
        fast = df[column].ewm(span=fast_period, adjust=False, min_periods=1).mean()
        slow = df[column].ewm(span=slow_period, adjust=False, min_periods=1).mean()
        macd = fast - slow
        signal = macd.ewm(span=signal_period, adjust=False, min_periods=1).mean()
        return {'macd': macd, 'signal': signal, 'histogram': macd - signal}
    
    def adx(self, df, period=14):
        plus_dm = df['high'].diff().where(lambda x: x > 0, 0)
        minus_dm = df['low'].diff().abs().where(lambda x: x > 0, 0)
        tr = self.atr(df, 1)
        smoothed_tr = tr.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
        plus_di = 100 * plus_dm.ewm(alpha=1/period, adjust=False, min_periods=period).mean() / smoothed_tr
        minus_di = 100 * minus_dm.ewm(alpha=1/period, adjust=False, min_periods=period).mean() / smoothed_tr
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)
        return {'adx': dx.ewm(alpha=1/period, adjust=False, min_periods=period).mean().fillna(0)}
    
    def momentum(self, df, period=10, column='close'):
        return df[column] - df[column].shift(period)
    
    def rate_of_change(self, df, period=10, column='close'):
        return ((df[column] - df[column].shift(period)) / df[column].shift(period).replace(0, np.nan)) * 100
    
    # Volume
    def obv(self, df):
        direction = np.sign(df['close'].diff())
        direction.iloc[0] = 0
        return (direction * df['volume']).cumsum()
    
    def vwap(self, df):
        tp = (df['high'] + df['low'] + df['close']) / 3
        return (tp * df['volume']).cumsum() / df['volume'].cumsum()
