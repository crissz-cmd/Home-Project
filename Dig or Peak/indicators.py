"""
Perhitungan indikator teknikal, diimplementasikan manual dengan pandas/numpy
(supaya tidak perlu install TA-Lib yang butuh compiler C dan sering
merepotkan terutama di Windows).
"""
import pandas as pd
import numpy as np


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    result = 100 - (100 / (1 + rs))
    return result.fillna(50)  # netral selama data pemanasan belum cukup


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    true_range = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def add_all_indicators(df: pd.DataFrame, cfg) -> pd.DataFrame:
    """Tambahkan semua kolom indikator yang dibutuhkan strategy.py ke DataFrame candle."""
    df = df.copy()
    df["ema_fast"] = ema(df["close"], cfg.EMA_FAST)
    df["ema_slow"] = ema(df["close"], cfg.EMA_SLOW)
    df["rsi"] = rsi(df["close"], cfg.RSI_PERIOD)
    macd_line, signal_line, hist = macd(df["close"], cfg.MACD_FAST, cfg.MACD_SLOW, cfg.MACD_SIGNAL)
    df["macd"] = macd_line
    df["macd_signal"] = signal_line
    df["macd_hist"] = hist
    df["atr"] = atr(df, cfg.ATR_PERIOD)
    return df
