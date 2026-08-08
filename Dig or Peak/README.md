# Bot Trading Forex Otomatis (MetaTrader 5 + Python)

Bot ini membaca pasar lewat indikator teknikal (EMA, RSI, MACD, ATR), lalu
otomatis mengirim order BUY/SELL ke MetaTrader 5 lengkap dengan Stop Loss
dan Take Profit, plus beberapa lapis manajemen risiko.

## ⚠️ Baca Ini Dulu

- **Tidak ada bot yang menjamin profit.** ini alat bantu berbasis aturan
  teknikal (EMA/RSI/MACD), bukan mesin pencetak uang. Backtest atau
  performa masa lalu tidak menjamin hasil ke depan.
- **Forex umumnya memakai leverage tinggi.** Ini memperbesar untung *dan*
  rugi — pergerakan harga kecil bisa berdampak besar ke saldo akun.
- Bot ini **mendukung live trading penuh**, tapi secara default berjalan
  dalam mode `DRY_RUN = True` (simulasi, tidak ada order sungguhan)
  supaya kamu bisa lihat dulu perilakunya sebelum mempertaruhkan uang asli.
- Kalau kamu set `DRY_RUN = False` dan MT5 login ke akun REAL, bot akan
  minta kamu mengetik kalimat konfirmasi manual sekali di awal — ini
  jaring pengaman, bukan penghalang.
- Uji di **akun demo** dulu, idealnya beberapa minggu di berbagai kondisi
  pasar, sebelum pindah ke akun real.
- Ini bukan nasihat keuangan, dan saya bukan penasihat keuangan berlisensi.

## Prasyarat

1. **Windows** — package `MetaTrader5` resmi cuma jalan di Windows. Untuk
   Mac/Linux, jalankan lewat VM Windows atau VPS Windows.
2. Aplikasi **MetaTrader 5** sudah terinstall dan kamu sudah punya akun
   (demo atau real) dari broker forex-mu.
3. Di MT5: aktifkan **Algo/Expert Trading** — Tools → Options → Expert
   Advisors → centang "Allow algorithmic trading".
4. Python 3.10 atau lebih baru.

## Instalasi

```bash
pip install -r requirements.txt
```

## Konfigurasi

**1. Kredensial** — salin `.env.example` menjadi `.env`, isi data login
MT5-mu:

```
MT5_LOGIN=12345678
MT5_PASSWORD=passwordmu
MT5_SERVER=NamaBroker-Server
MT5_TERMINAL_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
```

Nama server bisa dilihat di MT5: klik kanan nama akun di navigator →
Properties.

**2. Parameter bot** — buka `config.py`, yang paling penting untuk
disesuaikan:

| Parameter | Fungsi |
|---|---|
| `SYMBOLS` | Pair yang dipantau |
| `RISK_PERCENT_PER_TRADE` | % saldo yang dipertaruhkan tiap trade — mulai kecil (0.5–1%) |
| `MAX_DAILY_LOSS_PERCENT` | Bot berhenti buka posisi baru kalau rugi harian melewati ini |
| `DRY_RUN` | `True` = simulasi aman, `False` = order sungguhan dikirim |

## Menjalankan

```bash
python bot.py
```

Bot akan menampilkan info akun (saldo, leverage, jenis akun) lalu mulai
memantau pasar tiap `LOOP_INTERVAL_SECONDS`. Tekan `Ctrl+C` kapan saja
untuk berhenti.

## Struktur Kode

| File | Isi |
|---|---|
| `config.py` | Semua parameter yang bisa diubah |
| `indicators.py` | Perhitungan EMA, RSI, MACD, ATR |
| `strategy.py` | Logika sinyal BUY / SELL / HOLD |
| `risk_manager.py` | Position sizing, SL/TP, circuit breaker harian |
| `mt5_connector.py` | Koneksi & eksekusi order ke MT5 |
| `bot.py` | Loop utama yang menjalankan semuanya |
| `trade_log.csv` | Dibuat otomatis, mencatat tiap sinyal/order |

## Strategi Default

BUY saat EMA cepat memotong ke atas EMA lambat, RSI belum overbought, dan
histogram MACD positif. SELL kebalikannya. Ganti isi `strategy.py` kalau
mau pakai strategi sendiri — bagian lain bot tidak perlu diubah selama
`generate_signal()` tetap mengembalikan `"BUY"`, `"SELL"`, atau `"HOLD"`.

## Ide Pengembangan Lanjutan

- Backtest historis sebelum live (bisa dibuatkan kalau perlu)
- Notifikasi Telegram/WhatsApp tiap ada order
- Jalankan sebagai scheduled task di VPS Windows biar aktif 24/5
- Logging ke file, bukan cuma print ke konsol

## Batasan yang Perlu Disadari

- Bot hanya aktif memantau selama `python bot.py` berjalan. Kalau
  laptop mati atau internet putus, bot berhenti membuka posisi baru
  (posisi yang sudah terbuka dengan SL/TP tetap dieksekusi otomatis di
  server broker).
- Strategi EMA/RSI/MACD adalah strategi umum yang bisa dipelajari siapa
  saja — tidak ada keunggulan rahasia yang menjamin menang.
- Forex tutup di akhir pekan; jangan berasumsi bot selalu bisa entry.
