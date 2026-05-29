#!/usr/bin/env python3
"""
ADA/IRT DCA Bot - Bit24 Exchange
- Initial MARKET BUY (2 ADA) – wait for fill, get executed price
- Two limit buys at -0.21% and -0.42% of the executed start price
- Fixed take‑profit levels (from start price): +0.5%, +0.7%, +1.0%
- Market sell when best bid reaches TP
- Graceful shutdown: cancel ALL open orders → market‑sell remaining ADA
"""

import time
import signal
import sys
import json
import requests
import hmac
import hashlib
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone

# ─── Configuration ────────────────────────────────────────────────
PAIR_BASE = "ADA"
PAIR_QUOTE = "IRT"
QTY = "2"                     # each order buys exactly 2 ADA
BASE_URL = "https://rest.bit24.cash"

# TP percentages (from the executed initial market buy price)
TP_PERCENT = {
    "initial": Decimal("0.5"),   # +0.5%
    "limit1":  Decimal("0.7"),   # +0.7%
    "limit2":  Decimal("1.0"),   # +1.0%
}

# ─── Global state ─────────────────────────────────────────────────
API_KEY = ""
SECRET_KEY = ""
MARKET_INFO = {}               # decimals, min order sizes

positions = {
    "initial": {
        "buy_id": None,
        "filled_amount": None,
        "tp_price": None,      # set once start_price is known
        "executed": False,
    },
    "limit1": {
        "buy_id": None,
        "filled_amount": None,
        "tp_price": None,
        "executed": False,
    },
    "limit2": {
        "buy_id": None,
        "filled_amount": None,
        "tp_price": None,
        "executed": False,
    },
}

start_price = None             # executed price of the initial market buy
running = True
trades = []

# ─── Helpers ─────────────────────────────────────────────────────
def sign_params(params: dict) -> str:
    p = {k: v for k, v in params.items() if k != "signature"}
    q = "&".join(f"{k}={v}" for k, v in sorted(p.items()))
    return hmac.new(SECRET_KEY.encode(), q.encode(), hashlib.sha256).hexdigest()

def api_get(endpoint: str, params: dict = None) -> dict:
    url = f"{BASE_URL}{endpoint}"
    headers = {"Accept": "application/json", "X-BIT24-APIKEY": API_KEY}
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    data = r.json()
    if not data.get("success"):
        raise RuntimeError(f"API error: {data.get('error')}")
    return data

def api_post(endpoint: str, params: dict, sign: bool = True) -> dict:
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-BIT24-APIKEY": API_KEY,
    }
    if sign:
        params["signature"] = sign_params(params)
    r = requests.post(url, headers=headers, data=params)
    r.raise_for_status()
    data = r.json()
    if not data.get("success"):
        raise RuntimeError(f"API error: {data.get('error')}")
    return data

def get_market_info():
    data = api_get("/pro/capi/v1/markets")
    for m in data["data"]["results"]:
        if m["base_coin_symbol"] == PAIR_BASE and m["quote_coin_symbol"] == PAIR_QUOTE:
            MARKET_INFO["base_decimal"] = m["base_coin_decimal"]
            MARKET_INFO["quote_decimal"] = m["quote_coin_decimal"]
            MARKET_INFO["min_order_base"] = m.get("total_min", "0.000001")
            MARKET_INFO["min_market_base"] = m.get("market_order_base_coin_total_min", "0.000001")
            return
    raise RuntimeError(f"Market {PAIR_BASE}/{PAIR_QUOTE} not found")

def round_price(value: Decimal) -> str:
    dec = MARKET_INFO["quote_decimal"]
    quant = Decimal("1e-{}".format(dec))
    return str(value.quantize(quant, rounding=ROUND_HALF_UP))

def round_amount(value: Decimal) -> str:
    dec = MARKET_INFO["base_decimal"]
    quant = Decimal("1e-{}".format(dec))
    return str(value.quantize(quant, rounding=ROUND_HALF_UP))

def get_best_bid() -> Decimal:
    """Highest buy order price – what we can sell at."""
    data = api_get("/pro/capi/v1/markets/order-books",
                   {"base_coin": PAIR_BASE, "quote_coin": PAIR_QUOTE})
    return Decimal(data["data"]["buy_orders"][0]["price"])

def place_market_buy(amount: str) -> int:
    """True market buy. Returns order ID."""
    params = {
        "base_coin_symbol": PAIR_BASE,
        "quote_coin_symbol": PAIR_QUOTE,
        "type": "1",
        "category_type": "1",   # market
        "amount": amount,
    }
    result = api_post("/pro/capi/v1/orders/submit", params)
    return result["data"]["order"]["id"]

def place_limit_buy(price_str: str, amount: str) -> int:
    params = {
        "base_coin_symbol": PAIR_BASE,
        "quote_coin_symbol": PAIR_QUOTE,
        "type": "1",
        "category_type": "0",
        "price": price_str,
        "amount": amount,
    }
    result = api_post("/pro/capi/v1/orders/submit", params)
    return result["data"]["order"]["id"]

def place_market_sell(amount: str) -> dict:
    params = {
        "base_coin_symbol": PAIR_BASE,
        "quote_coin_symbol": PAIR_QUOTE,
        "type": "0",
        "category_type": "1",
        "amount": amount,
    }
    result = api_post("/pro/capi/v1/orders/submit", params)
    return result["data"]["order"]

def get_order_details(order_id: int) -> dict:
    data = api_get(f"/pro/capi/v1/orders", {"id": order_id})
    return data["data"]["order"]

def cancel_all_orders():
    """
    Cancel every open order.
    API docs: no secret key needed when order_id is omitted.
    """
    url = f"{BASE_URL}/pro/capi/v1/orders/cancel"
    headers = {
        "Accept": "application/json",
        "X-BIT24-APIKEY": API_KEY,
    }
    resp = requests.post(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"Cancel all failed: {data.get('error')}")

def get_balance(coin: str) -> Decimal:
    data = api_get("/asset/capi/v1/wallet/assets",
                   {"without_irt": "0", "without_zero": "1"})
    for a in data["data"]["asset"]:
        if a["symbol"] == coin:
            return Decimal(a["available_balance"])
    return Decimal("0")

def market_sell_all_remaining():
    bal = get_balance(PAIR_BASE)
    min_base = Decimal(MARKET_INFO["min_market_base"])
    if bal < min_base:
        print(f"Balance {bal} below minimum {min_base}, cannot sell.")
        return
    amount_str = round_amount(bal)
    print(f"Selling remaining {amount_str} ADA at market...")
    order = place_market_sell(amount_str)
    log_trade("sell_remaining", "shutdown", order)

# ─── Persistence ─────────────────────────────────────────────────
def save_tp_targets():
    tp_list = []
    for key in ["initial", "limit1", "limit2"]:
        pos = positions[key]
        if pos["tp_price"] is not None:
            tp_list.append({
                "position": key,
                "tp_price": str(pos["tp_price"]),
                "amount": pos["filled_amount"] if pos["filled_amount"] else "0",
                "executed": pos["executed"],
            })
    with open("tp.json", "w", encoding="utf-8") as f:
        json.dump(tp_list, f, indent=2, ensure_ascii=False)

def save_trades():
    with open("trade.json", "w", encoding="utf-8") as f:
        json.dump(trades, f, indent=2, ensure_ascii=False)

def log_trade(event_type, position, order):
    trades.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        "position": position,
        "order_id": order["id"],
        "symbol": f"{PAIR_BASE}/{PAIR_QUOTE}",
        "price": order.get("each_price", order.get("price", "")),
        "amount": order.get("done_value") if event_type == "buy_fill" else order.get("amount", ""),
        "total": order.get("total", ""),
        "commission": order.get("commission", "0"),
        "status": order.get("status_text", ""),
    })
    save_trades()

# ─── Signal handler ──────────────────────────────────────────────
def signal_handler(sig, frame):
    global running
    print("\nCtrl+C – shutting down...")
    running = False

# ─── Main ────────────────────────────────────────────────────────
def main():
    global API_KEY, SECRET_KEY, start_price, running
    signal.signal(signal.SIGINT, signal_handler)

    API_KEY = input("Enter API key: ").strip()
    SECRET_KEY = input("Enter Secret key: ").strip()

    print("Fetching market info...")
    get_market_info()

    # 1. Place a true MARKET BUY for 2 ADA
    print("Placing initial market buy for 2 ADA...")
    init_id = place_market_buy(QTY)
    positions["initial"]["buy_id"] = init_id

    # Wait for it to fill (market orders usually fill instantly, but we confirm)
    while running:
        order = get_order_details(init_id)
        if order["status"] == 1:   # filled
            start_price = Decimal(order["each_price"])
            positions["initial"]["filled_amount"] = order["done_value"]
            log_trade("buy_fill", "initial", order)
            print(f"Initial buy filled: {positions['initial']['filled_amount']} ADA @ {start_price}")
            break
        time.sleep(1)

    if not start_price:
        print("Initial buy did not fill – aborting.")
        sys.exit(1)

    # 2. Set three TP levels from the executed start price
    tp1 = start_price * Decimal("1.005")   # +0.5%
    tp2 = start_price * Decimal("1.007")   # +0.7%
    tp3 = start_price * Decimal("1.01")    # +1.0%

    positions["initial"]["tp_price"] = tp1
    positions["limit1"]["tp_price"]  = tp2
    positions["limit2"]["tp_price"]  = tp3
    save_tp_targets()

    # 3. Place the two limit buy orders (‑0.21% and ‑0.42% below start price)
    lim1_price = start_price * Decimal("0.9979")
    lim2_price = start_price * Decimal("0.9958")
    print(f"Placing limit buy #1 at {round_price(lim1_price)} (-0.21%)")
    positions["limit1"]["buy_id"] = place_limit_buy(round_price(lim1_price), QTY)
    print(f"Placing limit buy #2 at {round_price(lim2_price)} (-0.42%)")
    positions["limit2"]["buy_id"] = place_limit_buy(round_price(lim2_price), QTY)

    print("Monitoring – TP targets saved in tp.json")

    # 4. Main loop
    while running:
        try:
            # a) Check fill status of limit buys
            for key in ["limit1", "limit2"]:
                pos = positions[key]
                if pos["buy_id"] and pos["filled_amount"] is None:
                    order = get_order_details(pos["buy_id"])
                    if order["status"] == 1:          # fully filled
                        pos["filled_amount"] = order["done_value"]
                        log_trade("buy_fill", key, order)
                        print(f"{key} filled: {pos['filled_amount']} ADA @ {order['each_price']}")
                        save_tp_targets()

            # b) Check current best bid and execute TP sells
            try:
                bid = get_best_bid()
            except Exception as e:
                print(f"Price fetch error: {e}")
                time.sleep(5)
                continue

            for key, pos in positions.items():
                if (
                    pos["tp_price"] is not None and
                    pos["filled_amount"] is not None and
                    not pos["executed"]
                ):
                    if bid >= pos["tp_price"]:
                        print(
                            f"TP triggered for {key} "
                            f"(bid {bid} >= {pos['tp_price']}). "
                            f"Market selling {pos['filled_amount']} ADA"
                        )
                        try:
                            sell_order = place_market_sell(pos["filled_amount"])
                            pos["executed"] = True
                            log_trade("sell_tp", key, sell_order)
                            print(f"Sell order {sell_order['id']} placed")
                            save_tp_targets()
                        except RuntimeError as e:
                            print(f"Sell failed: {e} – will retry")

            time.sleep(3)   # poll every 3 seconds for faster reaction

        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(10)

    # 5. Graceful shutdown
    print("Cancelling all open orders...")
    try:
        cancel_all_orders()
        print("All open orders cancelled.")
    except Exception as e:
        print(f"Cancel error: {e}")

    time.sleep(3)  # let cancellations propagate

    print("Selling remaining ADA balance...")
    try:
        market_sell_all_remaining()
    except Exception as e:
        print(f"Remaining sell error: {e}")

    save_trades()
    save_tp_targets()
    print("Shutdown complete.")

if __name__ == "__main__":
    main()