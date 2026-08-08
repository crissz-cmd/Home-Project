"""
Manajemen risiko: position sizing berbasis % saldo, perhitungan SL/TP
berbasis ATR, dan circuit breaker kerugian harian. Bagian inilah yang
membuat bot tidak "all-in" secara membabi buta.
"""
from typing import Optional, Tuple, List
import MetaTrader5 as mt5
import config as cfg


def calculate_position_size(symbol: str, entry_price: float, sl_price: float) -> Optional[float]:
    """Hitung lot supaya kerugian JIKA SL kena = RISK_PERCENT_PER_TRADE % dari saldo akun."""
    account = mt5.account_info()
    symbol_info = mt5.symbol_info(symbol)
    if account is None or symbol_info is None:
        return None

    risk_amount = account.balance * (cfg.RISK_PERCENT_PER_TRADE / 100)
    sl_distance = abs(entry_price - sl_price)
    if sl_distance <= 0 or symbol_info.trade_tick_size <= 0:
        return None

    ticks_at_risk = sl_distance / symbol_info.trade_tick_size
    loss_per_lot = ticks_at_risk * symbol_info.trade_tick_value
    if loss_per_lot <= 0:
        return None

    raw_lot = risk_amount / loss_per_lot

    # Bulatkan ke kelipatan volume_step, dan batasi ke volume_min/volume_max broker
    step = symbol_info.volume_step
    lot = max(symbol_info.volume_min, (raw_lot // step) * step)
    lot = min(lot, symbol_info.volume_max)

    return round(lot, 2) if lot >= symbol_info.volume_min else None


def calculate_sl_tp(order_type: str, entry_price: float, atr_value: float) -> Tuple[float, float]:
    sl_distance = atr_value * cfg.SL_ATR_MULTIPLIER
    tp_distance = atr_value * cfg.TP_ATR_MULTIPLIER

    if order_type == "BUY":
        return entry_price - sl_distance, entry_price + tp_distance
    return entry_price + sl_distance, entry_price - tp_distance


def daily_loss_limit_hit(day_start_balance: float) -> bool:
    """Circuit breaker: True kalau kerugian harian sudah melewati batas yang diizinkan."""
    account = mt5.account_info()
    if account is None or day_start_balance <= 0:
        return False
    loss_percent = (day_start_balance - account.equity) / day_start_balance * 100
    return loss_percent >= cfg.MAX_DAILY_LOSS_PERCENT


def open_positions_count(symbols: List[str]) -> int:
    positions = mt5.positions_get()
    if positions is None:
        return 0
    return sum(1 for p in positions if p.symbol in symbols and p.magic == cfg.MAGIC_NUMBER)
