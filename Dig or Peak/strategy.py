"""
Logika sinyal trading: menentukan BUY / SELL / HOLD dari indikator.

Strategi default: EMA crossover menentukan arah tren, RSI sebagai filter
supaya tidak entry saat pasar sudah jenuh beli/jual, histogram MACD
sebagai konfirmasi momentum.

Ganti isi generate_signal() kalau kamu mau pakai strategi sendiri —
bagian lain bot tidak perlu diubah selama fungsi ini tetap mengembalikan
"BUY", "SELL", atau "HOLD".
"""
import config as cfg


def generate_signal(df) -> str:
    min_len = max(cfg.EMA_SLOW, cfg.MACD_SLOW, cfg.RSI_PERIOD) + 5
    if len(df) < min_len:
        return "HOLD"  # data historis belum cukup untuk indikator yang valid

    prev, curr = df.iloc[-2], df.iloc[-1]

    cross_up = prev["ema_fast"] <= prev["ema_slow"] and curr["ema_fast"] > curr["ema_slow"]
    cross_down = prev["ema_fast"] >= prev["ema_slow"] and curr["ema_fast"] < curr["ema_slow"]

    if cross_up and curr["rsi"] < cfg.RSI_OVERBOUGHT and curr["macd_hist"] > 0:
        return "BUY"
    if cross_down and curr["rsi"] > cfg.RSI_OVERSOLD and curr["macd_hist"] < 0:
        return "SELL"
    return "HOLD"
