"""
Loop utama bot trading forex.
Jalankan dengan: python bot.py
Hentikan kapan saja dengan Ctrl+C.
"""
import csv
import os
import time
from datetime import datetime, timezone

import MetaTrader5 as mt5

import config as cfg
import mt5_connector as conn
import indicators
import strategy
import risk_manager as risk

LOG_FILE = "trade_log.csv"


def log_trade(symbol, signal, lot, price, sl, tp, retcode, comment):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["waktu_utc", "symbol", "signal", "lot", "harga", "sl", "tp", "retcode", "komentar"])
        writer.writerow([datetime.now(timezone.utc).isoformat(), symbol, signal, lot, price, sl, tp, retcode, comment])


def already_has_position(symbol: str) -> bool:
    positions = mt5.positions_get(symbol=symbol)
    if positions is None:
        return False
    return any(p.magic == cfg.MAGIC_NUMBER for p in positions)


def process_symbol(symbol: str):
    if not conn.ensure_symbol(symbol):
        return

    df = conn.get_candles(symbol, cfg.CANDLES_LOOKBACK)
    if df is None:
        print(f"[{symbol}] Gagal ambil data candle.")
        return

    df = indicators.add_all_indicators(df, cfg)
    signal = strategy.generate_signal(df)
    last = df.iloc[-1]
    print(f"[{symbol}] harga={last['close']:.5f} rsi={last['rsi']:.1f} sinyal={signal}")

    if signal == "HOLD":
        return
    if already_has_position(symbol):
        print(f"[{symbol}] Sudah ada posisi terbuka, lewati sinyal baru.")
        return
    if risk.open_positions_count(cfg.SYMBOLS) >= cfg.MAX_OPEN_POSITIONS:
        print("Batas maksimum posisi terbuka bersamaan sudah tercapai.")
        return

    tick = mt5.symbol_info_tick(symbol)
    entry_price = tick.ask if signal == "BUY" else tick.bid
    sl, tp = risk.calculate_sl_tp(signal, entry_price, last["atr"])
    lot = risk.calculate_position_size(symbol, entry_price, sl)

    if lot is None:
        print(f"[{symbol}] Lot size tidak valid, order dibatalkan (cek RISK_PERCENT_PER_TRADE / jarak SL).")
        return

    digits = mt5.symbol_info(symbol).digits
    sl, tp = round(sl, digits), round(tp, digits)

    if cfg.DRY_RUN:
        print(f"[{symbol}] (DRY RUN, tidak ada order dikirim) {signal} {lot} lot @ {entry_price}, SL={sl} TP={tp}")
        log_trade(symbol, signal, lot, entry_price, sl, tp, "DRY_RUN", "simulasi")
        return

    result = conn.send_market_order(symbol, signal, lot, sl, tp)
    if result is None:
        print(f"[{symbol}] order_send tidak mengembalikan hasil.")
        log_trade(symbol, signal, lot, entry_price, sl, tp, "NONE", "no result")
    elif result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"[{symbol}] ORDER {signal} berhasil: {lot} lot @ {entry_price}, SL={sl} TP={tp}")
        log_trade(symbol, signal, lot, entry_price, sl, tp, result.retcode, result.comment)
    else:
        print(f"[{symbol}] Order GAGAL, retcode={result.retcode}, komentar={result.comment}")
        log_trade(symbol, signal, lot, entry_price, sl, tp, result.retcode, result.comment)


def run():
    if not conn.connect():
        return

    account = mt5.account_info()
    day_start_balance = account.balance
    current_day = datetime.now(timezone.utc).date()
    trading_halted = False

    try:
        while True:
            today = datetime.now(timezone.utc).date()
            if today != current_day:
                current_day = today
                day_start_balance = mt5.account_info().balance
                trading_halted = False
                print(f"\n=== Hari baru {current_day} (UTC), circuit breaker direset ===")

            if risk.daily_loss_limit_hit(day_start_balance):
                if not trading_halted:
                    print(f"\n Batas rugi harian ({cfg.MAX_DAILY_LOSS_PERCENT}%) tercapai. "
                          f"Bot berhenti buka posisi baru sampai hari berikutnya.")
                trading_halted = True
            else:
                for symbol in cfg.SYMBOLS:
                    process_symbol(symbol)

            time.sleep(cfg.LOOP_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nDihentikan oleh pengguna (Ctrl+C).")
    finally:
        conn.disconnect()


if __name__ == "__main__":
    run()
