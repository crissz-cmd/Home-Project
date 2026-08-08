# Bot Trading Forex Otomatis (MetaTrader 5 + Python) — Preset Scalping

Bot ini membaca pasar lewat indikator teknikal (EMA, RSI, MACD, ATR), lalu
otomatis mengirim order BUY/SELL ke MetaTrader 5 lengkap dengan Stop Loss
dan Take Profit, plus beberapa lapis manajemen risiko. Preset saat ini
dikonfigurasi untuk **scalping** (timeframe M1, loop cepat, filter spread
& jam sesi).

## ⚠️ Baca Ini Dulu

- **Tidak ada bot yang menjamin profit**, apalagi scalping. Ini alat bantu
  berbasis aturan teknikal, bukan mesin pencetak uang.
- **Scalping secara struktural lebih berat dari swing/day trading**:
  target profit per trade kecil, jadi spread & komisi jadi porsi biaya
  yang jauh lebih besar; sebagian broker retail membatasi/melarang
  scalping (cek syarat & ketentuan brokermu); dan koneksi Python↔MT5
  (lewat IPC ke terminal) punya latency lebih tinggi dibanding Expert
  Advisor native MQL5 yang jalan langsung di dalam platform. Ini bukan
  alasan untuk tidak mencoba — hanya supaya ekspektasinya realistis.
- **Forex umumnya memakai leverage tinggi**, yang memperbesar untung *dan*
  rugi — dan dengan frekuensi trade yang jauh lebih tinggi saat scalping,
  kerugian bisa terkumpul lebih cepat kalau strategi/parameter belum pas.
- Bot ini **mendukung live trading penuh**, tapi secara default berjalan
  dalam mode `DRY_RUN = True` (simulasi, tidak ada order sungguhan).
- Kalau kamu set `DRY_RUN = False` dan MT5 login ke akun REAL, bot akan
  minta kamu mengetik kalimat konfirmasi manual sekali di awal.
- Uji di **akun demo** dulu, idealnya beberapa minggu di berbagai kondisi
  pasar dan jam sesi, sebelum pindah ke akun real.
- Ini bukan nasihat keuangan, dan saya bukan penasihat keuangan berlisensi.

## Prasyarat

1. **Windows** — package `MetaTrader5` resmi cuma jalan di Windows. Untuk
   Mac/Linux, jalankan lewat VM Windows atau VPS Windows (VPS yang dekat
   secara jaringan ke server broker juga membantu mengurangi latency,
   cukup relevan untuk scalping).
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
MT5-mu (nama server bisa dilihat di MT5: klik kanan akun di navigator →
Properties):

```
MT5_LOGIN=12345678
MT5_PASSWORD=passwordmu
MT5_SERVER=NamaBroker-Server
MT5_TERMINAL_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
```

**2. Parameter bot** — di `config.py`:

| Parameter | Fungsi |
|---|---|
| `SYMBOLS` | Pair yang dipantau — mulai dari 1 pair dulu saat tes |
| `TIMEFRAME` | `M1` untuk scalping |
| `EMA_FAST/SLOW`, `RSI_PERIOD`, `MACD_*` | Kecepatan indikator — preset sudah dipercepat, tapi wajib diuji/dituning sendiri |
| `SL_ATR_MULTIPLIER` / `TP_ATR_MULTIPLIER` | Jarak SL/TP relatif terhadap ATR — sudah diperketat untuk scalping |
| `RISK_PERCENT_PER_TRADE` | % saldo dipertaruhkan per trade — dikecilkan karena frekuensi trade tinggi |
| `MAX_SPREAD_POINTS` | **Baru** — lewati sinyal kalau spread saat ini lebih lebar dari ini |
| `TRADING_SESSION_START/END_UTC` | **Baru** — bot hanya entry di jam ini (default: sesi London + overlap New York) |
| `LOOP_INTERVAL_SECONDS` | Jeda antar pengecekan — 3 detik untuk scalping (dulu 60) |
| `STATUS_PRINT_EVERY_N_LOOPS` | Supaya konsol tidak banjir print di loop 3 detik |
| `MAX_DAILY_LOSS_PERCENT` | Bot berhenti buka posisi baru kalau rugi harian melewati ini |
| `DRY_RUN` | `True` = simulasi aman, `False` = order sungguhan dikirim |

## Menjalankan

```bash
python bot.py
```

Bot menampilkan info akun, lalu memantau tiap `LOOP_INTERVAL_SECONDS`
selama masih dalam jam sesi yang dikonfigurasi. Tekan `Ctrl+C` kapan saja
untuk berhenti.

## Struktur Kode

| File | Isi |
|---|---|
| `config.py` | Semua parameter yang bisa diubah |
| `indicators.py` | Perhitungan EMA, RSI, MACD, ATR |
| `strategy.py` | Logika sinyal BUY / SELL / HOLD — hanya memakai candle yang sudah closed |
| `risk_manager.py` | Position sizing, SL/TP, circuit breaker harian |
| `mt5_connector.py` | Koneksi, data candle, **cek spread**, dan eksekusi order ke MT5 |
| `bot.py` | Loop utama: filter jam sesi, filter spread, throttle output konsol |
| `trade_log.csv` | Dibuat otomatis, mencatat tiap sinyal/order |

## Apa yang Berubah dari Preset Swing/Day Trading Sebelumnya

- Timeframe M15 → **M1**, indikator dipercepat (EMA 20/50 → 5/13, dst.)
- SL/TP dari 1.5x/3x ATR → **1x/1.5x ATR** (lebih ketat, khas scalping)
- Loop 60 detik → **3 detik**
- **Filter spread** ditambahkan (`get_spread_points` di `mt5_connector.py`) — sinyal dilewati kalau spread sedang melebar, karena di scalping spread lebar bisa memakan seluruh target profit
- **Filter jam sesi** ditambahkan — bot hanya entry saat sesi likuiditas tinggi
- **Sinyal hanya berdasarkan candle yang sudah closed** (`df.iloc[-3]`/`df.iloc[-2]`, bukan `-2`/`-1`) — penting supaya sinyal tidak "berkedip" berubah-ubah tiap 3 detik selagi candle M1 masih berjalan
- Output konsol di-throttle (`STATUS_PRINT_EVERY_N_LOOPS`) supaya tidak banjir di loop 3 detik
- `RISK_PERCENT_PER_TRADE` dan `MAX_DAILY_LOSS_PERCENT` dikecilkan karena frekuensi trade jauh lebih tinggi

## Ide Pengembangan Lanjutan

- Backtest historis dengan data M1 sebelum live (bisa dibuatkan kalau perlu)
- Kalau butuh eksekusi lebih cepat lagi: pertimbangkan menulis ulang
  strategi sebagai Expert Advisor MQL5 native (jalan di dalam terminal,
  tanpa IPC ke Python) — trade-off-nya development lebih rumit
- Notifikasi Telegram/WhatsApp tiap ada order
- VPS Windows dekat server broker untuk mengurangi latency

## Batasan yang Perlu Disadari

- Bot hanya aktif memantau selama `python bot.py` berjalan.
- Preset EMA/RSI/MACD cepat ini titik awal umum, bukan hasil optimasi
  atau backtest — performanya bisa sangat berbeda per pair/broker/kondisi
  pasar, dan wajib diuji dulu di demo sebelum dipakai live.
- Forex tutup di akhir pekan; jangan berasumsi bot selalu bisa entry.
