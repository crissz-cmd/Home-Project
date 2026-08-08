# Bot Trading Otomatis XAUUSD (MetaTrader 5 + Python)

Bot ini membaca pasar lewat indikator teknikal (EMA, RSI, MACD, ATR), lalu
otomatis mengirim order BUY/SELL ke MetaTrader 5 dengan Stop Loss yang
sudah divalidasi terhadap aturan broker, dan Take Profit **nominal USD**
yang dipantau oleh watcher real-time.

## ⚠️ Baca Ini Dulu

- **Tidak ada bot yang menjamin profit.** Ini alat bantu berbasis aturan
  teknikal, bukan mesin pencetak uang.
- **`position.profit` TIDAK termasuk komisi & swap** (lihat bagian "Take
  Profit Nominal" di bawah) — profit bersih saat posisi ditutup bisa
  sedikit lebih kecil dari `TARGET_PROFIT_USD` kalau akunmu kena komisi.
- Forex/gold umumnya memakai leverage tinggi — pergerakan kecil bisa
  berdampak besar ke saldo, apalagi dengan frekuensi trade tinggi.
- Bot ini **mendukung live trading penuh**, tapi default `DRY_RUN = True`
  (simulasi, tidak ada order sungguhan).
- Kalau `DRY_RUN = False` dan MT5 login ke akun REAL, bot minta konfirmasi
  ketik manual sekali di awal.
- Uji di **akun demo** dulu sebelum live. Ini bukan nasihat keuangan, dan
  saya bukan penasihat keuangan berlisensi.

## Prasyarat

1. **Windows** — package `MetaTrader5` resmi cuma jalan di Windows.
2. Aplikasi **MetaTrader 5** terinstall, sudah punya akun (demo/real).
3. Di MT5: Tools → Options → Expert Advisors → centang "Allow algorithmic trading".
4. Python 3.10+.

## Instalasi & Konfigurasi

```bash
pip install -r requirements.txt
```

Salin `.env.example` → `.env`, isi kredensial MT5-mu. Lalu sesuaikan
`config.py` — parameter yang paling relevan ada di tabel bawah.

| Parameter | Fungsi |
|---|---|
| `SYMBOLS` | `["XAUUSD"]` — cek nama persis di brokermu (`XAUUSDm`, `GOLD`, dst. bisa beda-beda) |
| `MAX_SPREAD_POINTS` | **Cek dulu ke broker** — skala spread gold beda dari forex 5-digit |
| `TARGET_PROFIT_USD` | Target profit nominal (USD) sebelum posisi ditutup otomatis |
| `USE_NOMINAL_PROFIT_TARGET` | `True` = TP price-based dimatikan, diganti watcher nominal |
| `WATCHER_INTERVAL_SECONDS` | Jeda cek profit posisi terbuka (default 1 detik) |
| `LOOP_INTERVAL_SECONDS` | Jeda scan sinyal baru (default 3 detik, terpisah dari watcher) |
| `MIN_STOP_BUFFER_POINTS` | Buffer ekstra di atas `trade_stops_level` broker untuk SL |
| `DRY_RUN` | `True` = simulasi aman, `False` = order sungguhan dikirim |

## Menjalankan

```bash
python bot.py
```

## Fitur Baru

### 1. Take Profit Nominal (USD) + Re-entry Otomatis

Alih-alih TP berbasis jarak harga, `bot.py` punya fungsi `check_profit_targets()`
yang jalan tiap `WATCHER_INTERVAL_SECONDS` (independen dari jadwal scan
sinyal, supaya lebih real-time) dan menutup posisi manual lewat
`mt5_connector.close_position()` begitu `position.profit >= TARGET_PROFIT_USD`.

Cara kerja *close* di MT5 Python: bukan ada fungsi `Close()` khusus — kamu
kirim `order_send` baru dengan `action=TRADE_ACTION_DEAL`, `type` **berlawanan**
arah posisi asal, dan field `"position"` diisi ticket posisi yang mau
ditutup. Itu yang membuat MT5 tahu ini menutup posisi, bukan membuka order baru.

**Re-entry otomatis** terjadi tanpa logika tambahan: begitu posisi hilang
dari `positions_get()` (karena sudah ditutup), fungsi `already_has_position()`
yang sudah ada otomatis kembali `False`, dan `process_symbol()` lanjut ke
`strategy.generate_signal()` seperti biasa di loop berikutnya — menunggu
sinyal EMA/RSI/MACD baru, bukan asal buka posisi lagi.

**Catatan akurasi**: `position.profit` di MT5 adalah floating profit murni
dari pergerakan harga, **tidak termasuk komisi maupun swap**. Kalau
brokermu charge komisi per lot, profit bersih yang benar-benar masuk ke
saldo akan sedikit lebih kecil dari `TARGET_PROFIT_USD`. Kalau mau aman,
set target sedikit di atas target net sebenarnya.

### 2. Fix Stop Loss Otomatis (Invalid Stops)

Order tanpa SL karena "Invalid Stops" biasanya punya **dua** penyebab, dan
`mt5_connector.py` sekarang menangani keduanya sebelum order dikirim:

1. **Pembulatan desimal** (`round_price`) — SL dibulatkan ke jumlah digit
   yang diizinkan broker (`symbol_info(symbol).digits`) sebelum dikirim.
2. **Jarak minimum broker** (`enforce_min_stop_distance`) — kalau SL hasil
   ATR terlalu dekat ke harga (melanggar `symbol_info(symbol).trade_stops_level`),
   SL otomatis dilebarkan ke jarak minimum + buffer (`MIN_STOP_BUFFER_POINTS`).
   Ini sama seringnya jadi penyebab "Invalid Stops" seperti masalah
   pembulatan, dan cukup relevan untuk XAUUSD karena `trade_stops_level`
   gold kadang jauh lebih lebar (dalam satuan harga) dibanding forex mayor.

Urutan di `process_symbol()` sengaja: **validasi/lebarkan SL dulu, baru
hitung lot size** dari SL final — supaya `RISK_PERCENT_PER_TRADE` tetap
akurat walau SL harus dilebarkan.

## Struktur Kode

| File | Isi |
|---|---|
| `config.py` | Semua parameter yang bisa diubah |
| `indicators.py` | EMA, RSI, MACD, ATR (tidak diubah) |
| `strategy.py` | Sinyal BUY/SELL/HOLD dari candle yang sudah closed (tidak diubah) |
| `risk_manager.py` | Position sizing, SL/TP dari ATR, circuit breaker harian (tidak diubah) |
| `mt5_connector.py` | Koneksi, data candle/spread, **validasi SL**, kirim order, **tutup posisi** |
| `bot.py` | Loop utama + **watcher profit nominal** |
| `trade_log.csv` | Dibuat otomatis, mencatat tiap sinyal/order/close |

## Batasan yang Perlu Disadari

- Watcher profit maupun scan sinyal baru cuma aktif selama `python bot.py`
  berjalan. SL tetap dieksekusi server-side oleh broker walau bot mati,
  tapi TP nominal TIDAK — kalau bot berhenti sementara posisi profit,
  posisi itu tidak akan otomatis ditutup sampai bot jalan lagi (atau SL
  kena, atau kamu tutup manual).
- `trade_stops_level` bisa 0 di sebagian broker (artinya broker tidak
  melaporkan batas) — `enforce_min_stop_distance` akan diam saja dalam
  kasus ini, jadi tetap perhatikan hasil order di `trade_log.csv`.
- Preset EMA/RSI/MACD ini titik awal umum, bukan hasil optimasi — wajib
  diuji dulu di demo, khususnya karena instrumen (XAUUSD) dan parameter
  TP-nya baru saja berubah signifikan.
