# ربات معاملاتی DCA ADA/IRT (Bit24)

این پروژه یک ربات معاملاتی خودکار برای بازار **ADA/IRT** در صرافی Bit24 است که از استراتژی **DCA + برداشت سود مرحله‌ای** استفاده می‌کند.

---

## 📌 توضیح استراتژی

این ربات یک ساختار ورود پله‌ای و خروج مستقل دارد:

### ورودها (Buy)

* **ورود اولیه:** خرید مارکت دقیقاً 2 ADA
* **خرید پله‌ای 1:** سفارش لیمیت در قیمت **0.21٪ پایین‌تر از قیمت ورود اولیه**
* **خرید پله‌ای 2:** سفارش لیمیت در قیمت **0.42٪ پایین‌تر از قیمت ورود اولیه**

---

### خروج‌ها (Take Profit)

هر پوزیشن به صورت مستقل مدیریت می‌شود:

| پوزیشن | نوع ورود | حد سود |
| ------ | -------- | ------ |
| اولیه  | مارکت    | +0.5٪  |
| پله 1  | لیمیت    | +0.7٪  |
| پله 2  | لیمیت    | +1.0٪  |

نکته مهم:

* هر پوزیشن جداگانه فروخته می‌شود
* بقیه سفارش‌ها بعد از TP لغو نمی‌شوند
* سیستم کاملاً غیرهمبسته (Independent Positions) است

---

## 🔁 روند اجرای ربات

1. خرید مارکت 2 ADA
2. ذخیره قیمت ورود (start_price)
3. ثبت دو سفارش لیمیت پایین‌تر از قیمت ورود
4. مانیتورینگ مداوم:

   * وضعیت پر شدن سفارش‌ها
   * قیمت بهترین BID
5. فعال شدن حد سودها و فروش مارکت
6. هنگام توقف (Ctrl+C):

   * لغو تمام سفارش‌های باز
   * فروش باقی‌مانده ADA

---

## ⚙️ ویژگی‌ها

* ✔ استراتژی DCA چندمرحله‌ای
* ✔ مدیریت مستقل هر پوزیشن
* ✔ حد سود جداگانه برای هر ورود
* ✔ خروج سریع با مارکت
* ✔ ثبت کامل معاملات (Logging)
* ✔ ذخیره وضعیت TP در فایل
* ✔ هندلینگ توقف امن (Graceful Shutdown)

---

## 🧠 تنظیمات اصلی

در فایل اصلی:

```python
PAIR_BASE = "ADA"
PAIR_QUOTE = "IRT"
QTY = "2"
```

---

## 📈 قوانین حد سود

* ورود اولیه → +0.5٪
* پله اول → +0.7٪
* پله دوم → +1.0٪

---

## ⚠️ مدل ریسک

این ربات:

* بر اساس میانگین‌گیری (DCA) طراحی شده
* در روند نزولی خرید اضافه انجام می‌دهد
* حد ضرر ندارد (Stop Loss پیش‌فرض ندارد)
* مناسب بازارهای پرنوسان با مدیریت دستی ریسک است

---

## 📦 نیازمندی‌ها

```bash
pip install requests
```

---

## 🔌 API مورد نیاز

این پروژه از API صرافی Bit24 استفاده می‌کند:

[https://docs.bit24.cash/#api-24](https://docs.bit24.cash/#api-24)

شامل:

* ثبت سفارش
* دریافت وضعیت سفارش
* داده‌های بازار
* موجودی کیف پول

---

## ▶️ اجرا

```bash
python main.py
```

سپس:

* API Key را وارد کنید
* Secret Key را وارد کنید

---

## 💾 فایل‌های خروجی

### `trade.json`

ثبت کامل تراکنش‌ها:

* خریدها
* فروش‌ها
* خروج اضطراری

### `tp.json`

ذخیره وضعیت حد سود:

* قیمت هدف
* وضعیت اجرا
* اطلاعات هر پوزیشن

---

## 🛑 توقف ربات (Ctrl+C)

در هنگام توقف:

1. تمام سفارش‌های باز لغو می‌شوند
2. موجودی باقی‌مانده ADA فروخته می‌شود
3. اطلاعات معاملات ذخیره می‌شود

---

## 📌 نکات مهم

* حد سود بر اساس **Best Bid** محاسبه می‌شود
* امکان لغزش قیمت (Slippage) در فروش وجود دارد
* سفارش‌های ناموفق retry نمی‌شوند
* فقط برای جفت‌ارز ADA/IRT طراحی شده است

---

## 🧩 معماری سیستم

* اجرای حلقه polling هر 3 ثانیه
* مدیریت state برای هر پوزیشن
* اتصال مستقیم REST API
* بدون websocket (سادگی + کنترل بیشتر)

---

## 📄 لایسنس

MIT — استفاده آزاد، مسئولیت استفاده با کاربر است.

---

# ADA/IRT DCA Trading Bot (Bit24)

A deterministic DCA (Dollar Cost Averaging) trading bot for the **ADA/IRT** market on Bit24 exchange.
It executes a 3-step entry grid with independent take-profit logic per position.

---

## Strategy Overview

This bot implements a structured accumulation + partial profit-taking system:

### Entry Logic

* **Initial Entry:** Market buy of exactly **2 ADA**
* **Grid Buy #1:** Limit buy at **-0.21%** from initial price
* **Grid Buy #2:** Limit buy at **-0.42%** from initial price

### Take Profit Logic (Independent per position)

| Position | Entry Type | TP Trigger |
| -------- | ---------- | ---------- |
| initial  | market buy | +0.5%      |
| limit1   | grid buy   | +0.7%      |
| limit2   | grid buy   | +1.0%      |

Each position:

* Is tracked independently
* Has its own TP condition
* Is sold separately via market sell
* Does NOT cancel other positions

---

## Execution Flow

1. Place market buy (2 ADA)
2. Capture executed price as `start_price`
3. Place two limit buy orders below market
4. Continuously monitor:

   * Order fill status
   * Best bid price
5. Trigger TP sells when conditions are met
6. On shutdown:

   * Cancel all open orders
   * Sell remaining ADA balance

---

## Features

* ✔ Multi-layer DCA grid
* ✔ Independent position tracking
* ✔ Automatic TP execution per entry
* ✔ Market-based execution for exits
* ✔ Graceful shutdown handler (Ctrl+C)
* ✔ Trade logging (`trade.json`)
* ✔ TP state persistence (`tp.json`)

---

## Configuration

Inside `main.py`:

```python
PAIR_BASE = "ADA"
PAIR_QUOTE = "IRT"
QTY = "2"
```

---

## Take Profit Rules

From initial market entry price:

* Initial position → +0.5%
* First limit entry → +0.7%
* Second limit entry → +1.0%

---

## Risk Model

This is a **directional averaging bot**, not a hedged system:

* Exposure increases on dips
* Exits are staggered (not all-in/all-out)
* No stop-loss is implemented by default

---

## Requirements

```bash
pip install requests
```

---

## API Dependency

This bot depends on Bit24 API:

[https://docs.bit24.cash/#api-24](https://docs.bit24.cash/#api-24)

Required endpoints:

* Market data
* Order submission
* Order status
* Wallet balance

---

## Run

```bash
python main.py
```

Then enter:

* API Key
* Secret Key

---

## Output Files

### `trade.json`

Stores all executed trades:

* buy fills
* sell executions
* shutdown liquidation

### `tp.json`

Stores active take-profit levels:

* price targets
* position state
* execution flags

---

## Shutdown Behavior

When interrupted (Ctrl+C):

1. All open orders are cancelled
2. Remaining ADA balance is liquidated at market
3. Logs are saved

---

## Important Notes

* Best bid is used as TP trigger (not last trade price)
* Market sells may suffer slippage in low liquidity conditions
* No retry queue for failed limit orders (intentional simplicity)
* Designed for single-pair execution only (ADA/IRT)

---

## Architecture Summary

* Stateless execution loop with persistent logs
* Position-based state machine (initial / limit1 / limit2)
* Polling-based market watcher (3s interval)
* Direct REST API integration (no websocket dependency)

---

## License

MIT — use freely, modify responsibly.
