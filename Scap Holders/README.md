# Scap Holders — Windows Product

Scap Holders is a Python + MetaTrader 5 automated gold-scalping experiment packaged as a Windows desktop product.

> ⚠️ **Risk warning:** This software can place real trades and can lose money. It is experimental software, not financial advice, and no profitability or performance is guaranteed.

## What the customer receives

- `ScapHolders.exe` desktop launcher
- configuration UI
- signed, machine-bound license verification
- DRY RUN / demo mode
- Start / Stop controls
- runtime log in `%APPDATA%\ScapHolders\runtime.log`
- persistent settings
- MetaTrader 5 integration

The customer does **not** need VS Code or a Python installation. The customer **does** need MetaTrader 5 installed and logged into the intended broker account.

## Engine

- M1 timeframe
- EMA 5/13 crossover
- RSI 7 filter
- MACD 5/13/4 confirmation
- ATR-based stop loss
- risk-based position sizing
- spread and UTC-session filters
- maximum open positions
- daily-loss circuit breaker
- nominal USD profit watcher
- broker minimum-stop-distance validation
- fresh-signal re-entry

These are implementation and risk-control features, not proof of profitability.

## Product architecture

```text
Customer
   │
   ▼
ScapHolders.exe
   ├── License verifier (Ed25519 + machine ID)
   ├── Configuration UI
   └── Trading engine
         └── MetaTrader 5 terminal

Seller
   ├── private_key.pem        (NEVER publish)
   ├── license_issuer.py      (offline license creation)
   └── build_product.bat      (PyInstaller build)
```

## Seller setup

Generate the signing keypair once on the seller/developer machine:

```bash
python tools/generate_keys.py
```

The command prints `SCAP_PUBLIC_KEY_B64`. Keep `private_key.pem` offline and backed up. Never commit it.

Set the public key and build:

```bat
set SCAP_PUBLIC_KEY_B64=YOUR_PUBLIC_KEY_BASE64
build_product.bat
```

Output:

```text
dist\ScapHolders\ScapHolders.exe
```

Test this executable on a clean Windows machine without Python or VS Code before selling it.

## License activation

The customer opens the app and clicks **Copy Machine ID**. The seller issues a signed license:

```bash
python tools/license_issuer.py --private-key private_key.pem --machine-id CUSTOMER_MACHINE_ID --expires 2027-09-03T00:00:00Z --license-id SH-0001 --output license.key
```

The customer places `license.key` in:

```text
%APPDATA%\ScapHolders\
```

The app then verifies product, machine binding, expiration, and digital signature before allowing the trading engine to start.

## Customer setup

1. Install MetaTrader 5 from the broker/provider.
2. Log into the customer's own MT5 account.
3. Open Scap Holders and copy the Machine ID.
4. Send the Machine ID to the seller.
5. Put the issued `license.key` into `%APPDATA%\ScapHolders\`.
6. Start with DRY RUN enabled.
7. Verify the broker symbol; default is `GOLDi`, but brokers may use names such as `XAUUSD`, `XAUUSDm`, or `XAUUSD.m`.
8. Only enable LIVE after independently verifying the settings.

## Packaging

`ScapHolders.spec` builds a GUI executable without a console window and includes the Python/MetaTrader runtime dependencies. `installer/ScapHolders.iss` can be compiled with Inno Setup to create a Windows installer after the EXE has passed testing.

A GitHub Actions workflow is also included. It expects the repository secret `SCAP_PUBLIC_KEY_B64` and builds the Windows artifact when manually triggered or when a tag matching `scap-v*` is pushed.

## Security limitation

A PyInstaller executable is harder to inspect than raw source but is not impossible to reverse engineer. For a stronger commercial version, porting the trading engine to native MQL5 and shipping `.ex5` is the next step.

## Suggested launch pricing

Initial positioning: **US$29.99**. After meaningful testing and evidence, consider **US$39.99–59.99**. Never market guaranteed returns, guaranteed win rate, or guaranteed profit.

## License

Scap Holders is proprietary software. See [`LICENSE`](./LICENSE).
