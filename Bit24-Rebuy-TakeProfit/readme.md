# Bit24 ADA Simple Strategy Bot 🤖

A simple trading bot for Bit24 exchange using Python.

This bot will:

1. Buy 2 ADA instantly with MARKET order
2. Create ONE LIMIT BUY order at `-0.2%`
3. Monitor the market continuously
4. Sell ALL ADA balance when price reaches `+0.73%` profit from the last trade

---

# Strategy Logic

## Step 1 — Market Buy

The bot buys:

```python
2 ADA
```

instantly using MARKET order.

---

## Step 2 — Limit Buy

After first buy, the bot creates:

```python
1 LIMIT BUY ORDER
```

at:

```text
-0.2% lower than current price
```

Example:

| Current Price | Limit Buy |
| ------------- | --------- |
| 100000        | 99800     |

---

## Step 3 — Take Profit

The bot watches market price every 5 seconds.

When market reaches:

```text
+0.73% profit
```

from the FIRST BUY price:

```text
SELL ALL ADA BALANCE
```

using MARKET SELL.

---

# Project Structure

```text
project/
├── auth.py
├── bit24_client.py
├── strategy.py
├── main.py
└── requirements.txt
```

---

# Installation

## Clone Repository

```bash
git clone YOUR_REPOSITORY
```

---

## Install Requirements

```bash
pip install -r requirements.txt
```

---

# Run Bot

```bash
python main.py
```

---

# API Keys

The bot will ask for:

```text
API KEY
SECRET KEY
```

when running.

Example:

```text
API KEY : xxxxx
SECRET KEY : xxxxx
```

---

# Configuration

Inside `strategy.py`

```python
BASE = "ADA"
QUOTE = "IRT"

MARKET_BUY_AMOUNT = "2"

LIMIT_BUY_AMOUNT = "2"

LIMIT_BUY_DROP_PERCENT = Decimal("0.2")

TAKE_PROFIT_PERCENT = Decimal("0.73")
```

You can change:

* Coin
* Buy amount
* Limit percentage
* Profit percentage

---

# Features

* MARKET BUY
* LIMIT BUY
* TAKE PROFIT
* AUTO SELL
* HMAC SHA256 SIGNATURE
* Clean architecture
* Multi-file structure

---

# Requirements

* Python 3.10+
* Bit24 API Access

---

# Security Warning

Never hardcode:

```python
API_KEY
SECRET_KEY
```

inside source code.

Always use input or environment variables.

---

# Disclaimer

This bot is for educational purposes.

Crypto trading is risky.
Use at your own risk.
