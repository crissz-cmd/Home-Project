"""
Loop utama bot trading XAUUSD.
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
        print(f"[{symbol}] Gagal membaca posisi terbuka; fail-safe: tidak membuka posisi baru.")
        return True
    return any(p.magic == cfg.MAGIC_NUMBER for p in positions)


def in_trading_session() -> bool:
    hour = datetime.now(timezone.utc).hour
    return cfg.TRADING_SESSION_START_UTC <= hour < cfg.TRADING_SESSION_END_UTC


# ============================================================
# FITUR BARU 1: WATCHER TAKE PROFIT NOMINAL (USD) + RE-ENTRY
# ============================================================
def check_profit_targets():
    """Cek semua posisi terbuka milik bot ini; tutup begitu floating profit
    (price-only, lihat catatan di config.py) sudah capai TARGET_PROFIT_USD.

    Re-entry otomatis: begitu posisi ditutup di sini, already_has_position()
    untuk symbol itu otomatis jadi False lagi di loop berikutnya -- artinya
    process_symbol() akan kembali membaca indikator dari nol dan menunggu
    sinyal BARU. Tidak ada "tembak order langsung", karena entry cuma
    terjadi lewat jalur strategy.generate_signal() seperti biasa.
    """
    if not cfg.USE_NOMINAL_PROFIT_TARGET:
        return

    positions = mt5.positions_get()
    if not positions:
        return

    for pos in positions:
        if pos.magic != cfg.MAGIC_NUMBER:
            continue  # bukan posisi bot ini, jangan diutak-atik
        if pos.profit < cfg.TARGET_PROFIT_USD:
            continue

        closed = conn.close_position(pos)
        if closed:
            print(f"[{pos.symbol}] Target profit ${cfg.TARGET_PROFIT_USD:.2f} tercapai "
                  f"(profit=${pos.profit:.2f}). Posisi #{pos.ticket} ditutup -> kembali ke mode scan sinyal.")
            log_trade(pos.symbol, "CLOSE_PROFIT_TARGET", pos.volume, pos.price_current,
                      pos.sl, None, "CLOSED", f"profit={pos.profit:.2f}")
        else:
            print(f"[{pos.symbol}] Target profit tercapai tapi GAGAL menutup posisi #{pos.ticket} "
                  f"({mt5.last_error()}), dicoba lagi loop berikutnya.")


def process_symbol(symbol: str, verbose: bool):
    if not conn.ensure_symbol(symbol):
        return

    df = conn.get_candles(symbol, cfg.CANDLES_LOOKBACK)
    if df is None:
        print(f"[{symbol}] Gagal ambil data candle.")
        return

    df = indicators.add_all_indicators(df, cfg)
    signal = strategy.generate_signal(df)
    last_closed = df.iloc[-2]

    if verbose or signal != "HOLD":
        print(f"[{symbol}] harga={last_closed['close']:.5f} rsi={last_closed['rsi']:.1f} sinyal={signal}")

    if signal == "HOLD":
        return
    if already_has_position(symbol):
        if verbose:
            print(f"[{symbol}] Sudah ada posisi terbuka, lewati sinyal baru.")
        return
    if risk.open_positions_count(cfg.SYMBOLS) >= cfg.MAX_OPEN_POSITIONS:
        print("Batas maksimum posisi terbuka bersamaan sudah tercapai.")
        return

    spread = conn.get_spread_points(symbol)
    if spread is None or spread > cfg.MAX_SPREAD_POINTS:
        print(f"[{symbol}] Spread {spread} melebihi batas {cfg.MAX_SPREAD_POINTS} points, sinyal dilewati.")
        return

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print(f"[{symbol}] Tidak bisa membaca tick harga, order dibatalkan: {mt5.last_error()}")
        return
    entry_price = tick.ask if signal == "BUY" else tick.bid
    sl, tp = risk.calculate_sl_tp(signal, entry_price, last_closed["atr"])

    # ===== FIX SL (FITUR BARU 2) =====
    # Urutannya penting: validasi/lebarkan SL DULU, baru hitung lot dari SL
    # final -- supaya risk % tetap akurat walau SL harus dilebarkan karena
    # aturan stops_level broker.
    sl = conn.enforce_min_stop_distance(symbol, signal, entry_price, sl)
    sl = conn.round_price(symbol, sl)
    tp = conn.round_price(symbol, tp)
    if sl is None or tp is None:
        print(f"[{symbol}] symbol_info tidak tersedia saat validasi SL/TP, order dibatalkan.")
        return
    # ===================================

    lot = risk.calculate_position_size(symbol, entry_price, sl)
    if lot is None:
        print(f"[{symbol}] Lot size tidak valid, order dibatalkan (cek RISK_PERCENT_PER_TRADE / jarak SL).")
        return

    tp_to_send = None if cfg.USE_NOMINAL_PROFIT_TARGET else tp
    tp_label = f"watcher ${cfg.TARGET_PROFIT_USD:.2f}" if cfg.USE_NOMINAL_PROFIT_TARGET else tp_to_send

    if cfg.DRY_RUN:
        print(f"[{symbol}] (DRY RUN) {signal} {lot} lot @ {entry_price}, SL={sl} TP={tp_label}, spread={spread:.1f}pt")
        log_trade(symbol, signal, lot, entry_price, sl, tp_to_send, "DRY_RUN", "simulasi")
        return

    result = conn.send_market_order(symbol, signal, lot, sl, tp_to_send)
    if result is None:
        print(f"[{symbol}] order_send tidak mengembalikan hasil.")
        log_trade(symbol, signal, lot, entry_price, sl, tp_to_send, "NONE", "no result")
    elif result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"[{symbol}] ORDER {signal} berhasil: {lot} lot @ {entry_price}, SL={sl} TP={tp_label}")
        log_trade(symbol, signal, lot, entry_price, sl, tp_to_send, result.retcode, result.comment)
    else:
        print(f"[{symbol}] Order GAGAL, retcode={result.retcode}, komentar={result.comment}")
        log_trade(symbol, signal, lot, entry_price, sl, tp_to_send, result.retcode, result.comment)


def run():
    if not conn.connect():
        return

    account = mt5.account_info()
    day_start_balance = account.balance
    current_day = datetime.now(timezone.utc).date()
    trading_halted = False
    was_in_session = None
    scan_loop_count = 0
    last_scan_time = 0.0

    try:
        while True:
            now_ts = time.time()
            today = datetime.now(timezone.utc).date()
            if today != current_day:
                current_day = today
                day_start_balance = mt5.account_info().balance
                trading_halted = False
                print(f"\n=== Hari baru {current_day} (UTC), circuit breaker direset ===")

            # Watcher profit dicek TIAP iterasi (tiap WATCHER_INTERVAL_SECONDS),
            # independen dari jadwal scan sinyal -- supaya lebih "real-time".
            # Ini jalan terus walau circuit breaker aktif / di luar jam sesi,
            # karena tugasnya mengelola posisi yang SUDAH terbuka, bukan buka baru.
            check_profit_targets()

            # Scan sinyal baru: lebih jarang, sesuai LOOP_INTERVAL_SECONDS.
            if now_ts - last_scan_time >= cfg.LOOP_INTERVAL_SECONDS:
                last_scan_time = now_ts

                in_session = in_trading_session()
                if in_session != was_in_session:
                    label = "MASUK" if in_session else "DI LUAR"
                    print(f"\n--- {label} jam sesi trading ({cfg.TRADING_SESSION_START_UTC}:00-"
                          f"{cfg.TRADING_SESSION_END_UTC}:00 UTC) ---")
                    was_in_session = in_session

                if risk.daily_loss_limit_hit(day_start_balance):
                    if not trading_halted:
                        print(f"\n Batas rugi harian ({cfg.MAX_DAILY_LOSS_PERCENT}%) tercapai. "
                              f"Bot berhenti buka posisi baru sampai hari berikutnya.")
                    trading_halted = True
                elif in_session:
                    scan_loop_count += 1
                    verbose = (scan_loop_count % cfg.STATUS_PRINT_EVERY_N_LOOPS == 0)
                    for symbol in cfg.SYMBOLS:
                        process_symbol(symbol, verbose)

            time.sleep(cfg.WATCHER_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nDihentikan oleh pengguna (Ctrl+C).")
    finally:
        conn.disconnect()


if __name__ == "__main__":
    run()
