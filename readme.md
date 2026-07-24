# Binance Futures Testnet Trading Bot CLI

A robust, lightweight Command-Line Interface (CLI) built in Python for executing Market and Limit orders on the **Binance Futures Testnet (USDT-M)** platform. 

Designed with strict input validation, automatic credential management, HMAC-SHA256 request signing, rich terminal formatting, and an offline `--dry-run` simulation mode.

---

##  Features

- **Order Types Supported:** 
  - `MARKET` Orders (Instant execution at current market price)
  - `LIMIT` Orders (Requires target execution price)
- **Robust Input Validation (`Pydantic`):**
  - Symbol validation (Must end with `USDT` or `BUSD`)
  - Order side check (`BUY` or `SELL`)
  - Quantity & Price non-zero positive enforcement
- **Secure Authentication:**
  - HMAC SHA-256 signature generation with timestamping
  - `.env` file configuration with automatic quote & whitespace sanitization
- **Terminal UI (`Rich`):**
  - Formatted tables for Order Request Summaries & Execution Results
  - Live loading spinners during HTTP requests
- **Logging & Auditing:**
  - Detailed log tracking saved automatically to `trading_bot.log`
- **Simulation Mode (`--dry-run`):**
  - Validate parameters and build order structures locally without triggering HTTP requests or requiring active API keys.

---

## 📁 Project Structure

```text
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API client & HMAC signing logic
│   ├── logging_config.py  # File logging setup
│   ├── orders.py          # Order execution manager
│   └── validators.py      # Pydantic input validation models
├── .env.example           # Template for environment variables
├── .gitignore             # Ignores venv, secrets, and logs
├── cli.py                 # Typer CLI application entry point
├── README.md              # Project documentation
├── requirements.txt       # Project dependencies
└── trading_bot.log        # Local execution logs