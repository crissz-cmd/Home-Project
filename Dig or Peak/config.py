"""
Konfigurasi bot trading forex.
Ubah nilai-nilai di bawah sesuai kebutuhanmu. Baca README.md dulu sebelum
mengubah RISK_PERCENT_PER_TRADE atau DRY_RUN.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# KREDENSIAL AKUN MT5 (diambil dari file .env — JANGAN hardcode di sini,
# supaya tidak ter-commit ke git / bocor tanpa sengaja)
# ============================================================
MT5_LOGIN = int(os.getenv("MT5_LOGIN", "0") or "0")
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
MT5_SERVER = os.getenv("MT5_SERVER", "")
MT5_TERMINAL_PATH = os.getenv("MT5_TERMINAL_PATH", "")  # contoh: C:\Program Files\MetaTrader 5\terminal64.exe

# ============================================================
# INSTRUMEN & TIMEFRAME
# ============================================================
SYMBOLS = ["XAGUSDi", "EURUSDi", "GOLDi"]   # ganti/sesuaikan pair yang mau dipantau
TIMEFRAME = "H1"                          # M1, M5, M15, M30, H1, H4, D1
CANDLES_LOOKBACK = 300                     # jumlah candle historis diambil tiap loop

# ============================================================
# PARAMETER STRATEGI (EMA crossover + filter RSI + konfirmasi MACD)
# ============================================================
EMA_FAST = 20
EMA_SLOW = 50
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# ============================================================
# MANAJEMEN RISIKO — JANGAN DIABAIKAN
# ============================================================
RISK_PERCENT_PER_TRADE = 0.5      # % saldo akun dipertaruhkan per trade (mulai kecil!)
ATR_PERIOD = 14
SL_ATR_MULTIPLIER = 1.5           # jarak Stop Loss = 1.5 x ATR
TP_ATR_MULTIPLIER = 3.0           # jarak Take Profit = 3 x ATR (risk:reward ~1:2)

MAX_OPEN_POSITIONS = 3            # maksimum posisi terbuka bersamaan (semua simbol)
MAX_DAILY_LOSS_PERCENT = 3.0      # circuit breaker: stop buka posisi baru kalau rugi harian > ini
MAGIC_NUMBER = 234000              # ID unik EA/bot ini di MT5 (biar tidak bentrok EA lain)

# ============================================================
# EKSEKUSI
# ============================================================
DEVIATION_POINTS = 20             # slippage maksimum yang ditoleransi (dalam points)
LOOP_INTERVAL_SECONDS = 60        # jeda antar pengecekan sinyal

# ============================================================
# SAKLAR KESELAMATAN — BACA INI
# ============================================================
# True  = mode simulasi. Sinyal & lot dihitung dan dicatat ke trade_log.csv,
#         TAPI TIDAK ADA order sungguhan yang dikirim ke MT5. Aman untuk tes.
# False = order sungguhan dikirim. Kalau MT5 login ke akun REAL, ini uang asli.
DRY_RUN = False

# Kalau akun yang sedang login di MT5 terdeteksi akun REAL (bukan demo),
# bot akan minta konfirmasi ketik manual sekali di awal sebelum jalan.
# Sangat disarankan dibiarkan True.
REQUIRE_LIVE_CONFIRMATION = True
