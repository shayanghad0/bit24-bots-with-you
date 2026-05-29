# 🤖 ربات استراتژی ساده ADA برای Bit24

یک ربات معاملاتی ساده برای صرافی Bit24 با زبان Python.

این ربات به صورت خودکار:

1. خرید اولیه را با سفارش MARKET انجام می‌دهد.
2. یک سفارش LIMIT BUY در قیمت 0.2٪ پایین‌تر ثبت می‌کند.
3. قیمت بازار را به صورت مداوم بررسی می‌کند.
4. زمانی که قیمت به 0.73٪ سود نسبت به آخرین خرید برسد، تمام موجودی ADA را می‌فروشد.
5. تمام معاملات را در فایل `trade.json` ذخیره می‌کند.
6. در صورت فشردن `CTRL + C` تلاش می‌کند تمام موجودی قابل فروش را به صورت MARKET SELL بفروشد.

---

# 📈 منطق استراتژی

## مرحله اول — خرید اولیه

ربات در شروع اجرا:

```python
2 ADA
```

را با سفارش MARKET خریداری می‌کند.

---

## مرحله دوم — خرید پله‌ای

پس از خرید اولیه، یک سفارش LIMIT BUY ایجاد می‌شود.

قیمت سفارش:

```text
0.2٪ پایین‌تر از قیمت فعلی بازار
```

مثال:

| قیمت فعلی | قیمت سفارش |
| --------- | ---------- |
| 100000    | 99800      |

---

## مرحله سوم — حد سود

ربات هر 5 ثانیه قیمت بازار را بررسی می‌کند.

اگر قیمت به:

```text
0.73٪ بالاتر از آخرین خرید
```

برسد:

```text
تمام موجودی ADA فروخته می‌شود.
```

---

# 📂 ساختار پروژه

```text
project/
├── auth.py
├── bit24_client.py
├── trade_storage.py
├── strategy.py
├── main.py
├── trade.json
└── requirements.txt
```

---

# ⚙️ نصب

## دریافت پروژه

```bash
git clone YOUR_REPOSITORY
```

---

## نصب کتابخانه‌ها

```bash
pip install -r requirements.txt
```

---

# ▶️ اجرای ربات

```bash
python main.py
```

---

# 🔑 کلیدهای API

هنگام اجرا ربات از شما دریافت می‌کند:

```text
API KEY
SECRET KEY
```

مثال:

```text
API KEY : xxxxxxxxx
SECRET KEY : xxxxxxxxx
```

---

# 🛠 تنظیمات

در فایل:

```python
strategy.py
```

مقادیر زیر قابل تغییر هستند:

```python
BASE = "ADA"
QUOTE = "IRT"

MARKET_BUY_SPEND = "200000"

LIMIT_BUY_AMOUNT = "2"

LIMIT_BUY_DROP_PERCENT = Decimal("0.2")

TAKE_PROFIT_PERCENT = Decimal("0.73")
```

می‌توانید موارد زیر را تغییر دهید:

* ارز مورد معامله
* مقدار خرید اولیه
* مقدار خرید پله‌ای
* درصد خرید در اصلاح قیمت
* درصد حد سود

---

# 💾 ذخیره معاملات

تمام معاملات در فایل زیر ذخیره می‌شوند:

```text
trade.json
```

اطلاعات ذخیره شده شامل:

* زمان معامله
* نوع معامله
* مقدار
* قیمت
* پاسخ API

---

# 🚨 خروج اضطراری

در صورت فشردن:

```text
CTRL + C
```

ربات:

1. موجودی فعلی ارز را دریافت می‌کند.
2. موجودی قابل فروش را محاسبه می‌کند.
3. سفارش فروش MARKET ارسال می‌کند.
4. نتیجه را در `trade.json` ذخیره می‌کند.

---

# ✨ امکانات

* خرید MARKET
* خرید LIMIT
* فروش MARKET
* حد سود خودکار
* ذخیره تاریخچه معاملات
* خروج اضطراری با CTRL+C
* امضای HMAC SHA256
* ساختار چند فایلی و قابل توسعه
* مدیریت خطاهای API

---

# 📋 پیش‌نیازها

* Python 3.10 یا جدیدتر
* دسترسی به API صرافی Bit24
* API Key و Secret Key معتبر

---

# 🔒 نکات امنیتی

هرگز اطلاعات زیر را داخل کد ذخیره نکنید:

```python
API_KEY
SECRET_KEY
```

همیشه از:

```python
input()
```

یا متغیرهای محیطی (Environment Variables) استفاده کنید.

---

# ⚠️ سلب مسئولیت

این پروژه صرفاً برای اهداف آموزشی و تحقیقاتی ارائه شده است.

معامله در بازار رمزارزها دارای ریسک مالی است و تمامی مسئولیت سود و زیان بر عهده کاربر خواهد بود.

# 🤖 Bit24 ADA Simple Strategy Bot

A lightweight automated trading bot for the Bit24 exchange written in Python.

The bot automatically:

1. Executes an initial MARKET BUY.
2. Creates one LIMIT BUY order 0.2% below the current market price.
3. Monitors the market continuously.
4. Sells the entire ADA balance when the configured profit target is reached.
5. Stores all trade activity in `trade.json`.
6. Attempts an emergency MARKET SELL when the user presses `CTRL + C`.

---

# 📈 Strategy Logic

## Step 1 — Initial Market Buy

The bot starts by purchasing ADA instantly using a MARKET order.

Example:

```python
2 ADA
```

---

## Step 2 — Rebuy Order

After the first purchase, the bot creates a single LIMIT BUY order.

Order price:

```text
0.2% below the current market price
```

Example:

| Current Price | Limit Buy Price |
| ------------- | --------------- |
| 100000        | 99800           |

---

## Step 3 — Take Profit

The bot checks the market price every 5 seconds.

When the price reaches:

```text
+0.73% profit from the latest buy price
```

the bot will:

```text
SELL ALL AVAILABLE ADA BALANCE
```

using a MARKET SELL order.

---

# 📂 Project Structure

```text
project/
├── auth.py
├── bit24_client.py
├── trade_storage.py
├── strategy.py
├── main.py
├── trade.json
└── requirements.txt
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone YOUR_REPOSITORY
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run Bot

```bash
python main.py
```

---

# 🔑 API Credentials

The bot will ask for:

```text
API KEY
SECRET KEY
```

when starting.

Example:

```text
API KEY : xxxxxxxxx
SECRET KEY : xxxxxxxxx
```

---

# 🛠 Configuration

Inside:

```python
strategy.py
```

you can customize:

```python
BASE = "ADA"
QUOTE = "IRT"

MARKET_BUY_SPEND = "200000"

LIMIT_BUY_AMOUNT = "2"

LIMIT_BUY_DROP_PERCENT = Decimal("0.2")

TAKE_PROFIT_PERCENT = Decimal("0.73")
```

Available customizations:

* Trading coin
* Base currency
* Initial buy amount
* Rebuy amount
* Rebuy percentage
* Take-profit percentage

---

# 💾 Trade History

All trades are automatically stored in:

```text
trade.json
```

Each record contains:

* Timestamp
* Trade type
* Coin
* Amount
* Price
* API response

This makes debugging and strategy analysis easier.

---

# 🚨 Emergency Exit (CTRL + C)

When:

```text
CTRL + C
```

is pressed during execution, the bot will:

1. Fetch the available ADA balance.
2. Calculate the sellable amount.
3. Send a MARKET SELL order.
4. Save the result into `trade.json`.
5. Exit safely.

---

# ✨ Features

* MARKET BUY
* LIMIT BUY
* MARKET SELL
* Automatic Take Profit
* Trade History Logging
* Emergency Exit Support
* HMAC SHA256 Signature Authentication
* Multi-file Architecture
* Error Handling
* Bit24 API Integration

---

# 📋 Requirements

* Python 3.10+
* Bit24 API Access
* Valid API Key
* Valid Secret Key

---

# 🔒 Security Warning

Never hardcode:

```python
API_KEY
SECRET_KEY
```

inside source code.

Always use:

```python
input()
```

or Environment Variables.

---

# ⚠️ Disclaimer

This project is provided for educational and research purposes only.

Cryptocurrency trading involves financial risk.

Use this software entirely at your own risk. The author assumes no responsibility for any financial losses, damages, or account-related issues resulting from the use of this bot.
