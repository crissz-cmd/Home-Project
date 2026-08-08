"""
Konfigurasi bot trading XAUUSD (Gold).
Preset: scalping, take profit NOMINAL USD (bukan price-based) lewat watcher
real-time, dan SL yang divalidasi otomatis terhadap aturan broker sebelum
dikirim. Baca README.md sebelum menjalankan.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# KREDENSIAL AKUN MT5 (diambil dari file .env — JANGAN hardcode di sini)
# ============================================================
MT5_LOGIN = int(os.getenv("MT5_LOGIN", "0") or "0")
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
MT5_SERVER = os.getenv("MT5_SERVER", "")
MT5_TERMINAL_PATH = os.getenv("MT5_TERMINAL_PATH", "")

# ============================================================
# INSTRUMEN & TIMEFRAME
# ============================================================
SYMBOLS = ["GOLDi"]        # sesuaikan kalau broker pakai nama lain, mis. "XAUUSDm" / "GOLD" / "XAUUSD.m"
TIMEFRAME = "M1"
CANDLES_LOOKBACK = 300

# ============================================================
# PARAMETER STRATEGI — tidak disentuh, logika EMA/RSI/MACD sudah jalan
# ============================================================
EMA_FAST = 5
EMA_SLOW = 13
RSI_PERIOD = 7
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_FAST = 5
MACD_SLOW = 13
MACD_SIGNAL = 4

# ============================================================
# STOP LOSS & TAKE PROFIT BERBASIS ATR
# ============================================================
RISK_PERCENT_PER_TRADE = 0.3
ATR_PERIOD = 7
SL_ATR_MULTIPLIER = 1.0
TP_ATR_MULTIPLIER = 1.5     # tetap dihitung untuk referensi, tapi TIDAK dikirim ke order
                            # selama USE_NOMINAL_PROFIT_TARGET = True (lihat di bawah)

# FIX SL #2: buffer tambahan (dalam points) di ATAS trade_stops_level broker,
# supaya SL tidak mepet pas di batas minimum dan tetap aman dari pergerakan
# harga sekecil apa pun sebelum order sampai ke server.
MIN_STOP_BUFFER_POINTS = 2

MAX_OPEN_POSITIONS = 5
MAX_DAILY_LOSS_PERCENT = 2.0
MAGIC_NUMBER = 234002       # beda dari preset sebelumnya biar posisi/log tidak tercampur

# PENTING untuk XAUUSD: skala spread gold BEDA dari pasangan forex 5-digit.
# Cek dulu spread khas XAUUSD di brokermu (Market Watch -> klik kanan XAUUSD
# -> Spread) sebelum percaya angka default di bawah ini.
MAX_SPREAD_POINTS = 30

TRADING_SESSION_START_UTC = 7
TRADING_SESSION_END_UTC = 17

# ============================================================
# FITUR BARU: TAKE PROFIT NOMINAL (USD) + RE-ENTRY OTOMATIS
# ============================================================
# True  = TP price-based TIDAK dikirim ke order. Bot memantau posisi lewat
#         watcher dan menutup manual begitu floating profit >= TARGET_PROFIT_USD.
#         Setelah ditutup, symbol otomatis kembali discan untuk sinyal baru
#         (tidak perlu logika tambahan -- already_has_position() otomatis
#         jadi False lagi begitu posisi hilang).
# False = kembali ke TP price-based lama (pakai TP_ATR_MULTIPLIER).
USE_NOMINAL_PROFIT_TARGET = True
TARGET_PROFIT_USD = 2.0

# CATATAN AKURASI: position.profit dari MT5 adalah floating profit MURNI
# dari pergerakan harga -- TIDAK termasuk komisi maupun swap. Kalau akunmu
# kena komisi per lot, profit BERSIH saat posisi ditutup akan sedikit lebih
# kecil dari angka ini. Kalau mau aman, set target sedikit di atas target
# net yang sebenarnya kamu mau (mis. target net $2 + komisi ~$0.5/lot -> isi 2.5).

WATCHER_INTERVAL_SECONDS = 1     # jeda cek profit posisi -- dibuat lebih rapat dari jeda scan sinyal

# ============================================================
# EKSEKUSI
# ============================================================
DEVIATION_POINTS = 10
LOOP_INTERVAL_SECONDS = 3        # jeda SCAN sinyal baru (watcher profit pakai WATCHER_INTERVAL_SECONDS sendiri)
STATUS_PRINT_EVERY_N_LOOPS = 20

# ============================================================
# SAKLAR KESELAMATAN — BACA INI
# ============================================================
DRY_RUN = False
REQUIRE_LIVE_CONFIRMATION = True
