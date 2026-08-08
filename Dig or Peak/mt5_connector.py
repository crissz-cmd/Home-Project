"""
Wrapper untuk semua interaksi dengan terminal MetaTrader 5: konek, ambil
data candle, dan kirim order (dengan fallback mode filling order karena
tiap broker bisa beda dukungannya).
"""
from typing import Optional
import pandas as pd
import MetaTrader5 as mt5
import config as cfg

TIMEFRAME_MAP = {
    "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30, "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}


def connect() -> bool:
    kwargs = {}
    if cfg.MT5_TERMINAL_PATH:
        kwargs["path"] = cfg.MT5_TERMINAL_PATH
    if cfg.MT5_LOGIN:
        kwargs.update(login=cfg.MT5_LOGIN, password=cfg.MT5_PASSWORD, server=cfg.MT5_SERVER)

    if not mt5.initialize(**kwargs):
        print("Gagal konek ke MT5:", mt5.last_error())
        return False

    account = mt5.account_info()
    if account is None:
        print("Tidak bisa membaca info akun:", mt5.last_error())
        mt5.shutdown()
        return False

    mode = {0: "DEMO", 1: "CONTEST", 2: "REAL (UANG ASLI)"}.get(account.trade_mode, "TIDAK DIKETAHUI")
    print("=" * 60)
    print(f"Terhubung ke akun #{account.login} ({account.server})")
    print(f"Jenis akun : {mode}")
    print(f"Saldo      : {account.balance:,.2f} {account.currency}")
    print(f"Leverage   : 1:{account.leverage}")
    print(f"Mode bot   : {'DRY RUN (simulasi)' if cfg.DRY_RUN else 'LIVE (order sungguhan dikirim)'}")
    print("=" * 60)

    if account.trade_mode == 2 and cfg.REQUIRE_LIVE_CONFIRMATION and not cfg.DRY_RUN:
        print("\n⚠️  PERINGATAN: Ini akun REAL — setiap order akan memakai UANG SUNGGUHAN.")
        answer = input('Ketik persis: SAYA MENGERTI RISIKONYA   (atau Enter untuk batal): ')
        if answer.strip() != "SAYA MENGERTI RISIKONYA":
            print("Dibatalkan. Tidak ada order yang dikirim.")
            mt5.shutdown()
            return False

    return True


def ensure_symbol(symbol: str) -> bool:
    info = mt5.symbol_info(symbol)
    if info is None:
        print(f"Simbol {symbol} tidak ditemukan di broker ini.")
        return False
    if not info.visible:
        return mt5.symbol_select(symbol, True)
    return True


def get_candles(symbol: str, count: int) -> Optional[pd.DataFrame]:
    tf = TIMEFRAME_MAP[cfg.TIMEFRAME]
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
    if rates is None or len(rates) == 0:
        return None
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df


def send_market_order(symbol: str, order_type: str, volume: float, sl: float, tp: float):
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None

    price = tick.ask if order_type == "BUY" else tick.bid
    base_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": cfg.DEVIATION_POINTS,
        "magic": cfg.MAGIC_NUMBER,
        "comment": "auto-bot",
        "type_time": mt5.ORDER_TIME_GTC,
    }

    # Tiap broker kadang cuma terima satu mode filling tertentu -> coba berurutan.
    result = None
    for filling in (mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_RETURN):
        request = {**base_request, "type_filling": filling}
        result = mt5.order_send(request)
        if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
            return result
    return result  # kembalikan percobaan terakhir untuk keperluan logging error


def disconnect():
    mt5.shutdown()
