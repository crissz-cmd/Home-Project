"""
Logika sinyal trading: menentukan BUY / SELL / HOLD dari indikator.

Strategi default: EMA crossover menentukan arah tren, RSI sebagai filter
supaya tidak entry saat pasar sudah jenuh beli/jual, histogram MACD
sebagai konfirmasi momentum.

PENTING (terutama untuk scalping dengan loop cepat): keputusan HANYA
memakai dua candle yang sudah CLOSED (df.iloc[-3] dan df.iloc[-2]).
df.iloc[-1] adalah candle yang MASIH BERJALAN — sengaja diabaikan di sini
supaya sinyal tidak berubah-ubah tiap beberapa detik hanya karena candle
itu sendiri belum selesai terbentuk.

Ganti isi generate_signal() kalau kamu mau pakai strategi sendiri —
bagian lain bot tidak perlu diubah selama fungsi ini tetap mengembalikan
"BUY", "SELL", atau "HOLD".
"""
import config as cfg


def generate_signal(df) -> str:
    min_len = max(cfg.EMA_SLOW, cfg.MACD_SLOW, cfg.RSI_PERIOD) + 5
    if len(df) < min_len + 1:
        return "HOLD"  # data historis belum cukup untuk indikator yang valid

    prev, curr = df.iloc[-3], df.iloc[-2]  # dua candle terakhir yang SUDAH closed

    cross_up = prev["ema_fast"] <= prev["ema_slow"] and curr["ema_fast"] > curr["ema_slow"]
    cross_down = prev["ema_fast"] >= prev["ema_slow"] and curr["ema_fast"] < curr["ema_slow"]

    if cross_up and curr["rsi"] < cfg.RSI_OVERBOUGHT and curr["macd_hist"] > 0:
        return "BUY"
    if cross_down and curr["rsi"] > cfg.RSI_OVERSOLD and curr["macd_hist"] < 0:
        return "SELL"
    return "HOLD"
