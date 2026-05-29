# file: bit24_client.py

import requests
from decimal import Decimal
from auth import sign_params


class Bit24Client:

    BASE_URL = "https://rest.bit24.cash"

    def __init__(self, api_key: str, secret_key: str):

        self.api_key = api_key
        self.secret_key = secret_key

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-BIT24-APIKEY": api_key
        }

    # =========================
    # GET BEST ASK
    # =========================

    def get_best_ask(self, base: str, quote: str) -> Decimal:

        url = f"{self.BASE_URL}/pro/capi/v1/markets/order-books"

        params = {
            "base_coin": base,
            "quote_coin": quote
        }

        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )

        response.raise_for_status()

        data = response.json()

        sell_orders = data["data"]["sell_orders"]

        if not sell_orders:
            raise Exception("No sell orders found.")

        return Decimal(sell_orders[0]["price"])

    # =========================
    # GET WALLET BALANCE
    # =========================

    def get_coin_balance(self, symbol: str) -> Decimal:

        url = f"{self.BASE_URL}/asset/capi/v1/wallet/assets"

        params = {
            "without_zero": "1",
            "without_irt": "0"
        }

        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )

        response.raise_for_status()

        data = response.json()

        assets = data.get("data", {}).get("asset", [])

        for asset in assets:

            if asset["symbol"] == symbol:

                return Decimal(asset["available_balance"])

        return Decimal("0")

    # =========================
    # SUBMIT ORDER
    # =========================

    def submit_order(self, params: dict):

        url = f"{self.BASE_URL}/pro/capi/v1/orders/submit"

        params["signature"] = sign_params(
            self.secret_key,
            params
        )

        response = requests.post(
            url,
            headers=self.headers,
            data=params
        )

        response.raise_for_status()

        return response.json()

    # =========================
    # MARKET BUY
    # =========================

    def market_buy(self,
                   base: str,
                   quote: str,
                   amount: str):

        params = {
            "base_coin_symbol": base,
            "quote_coin_symbol": quote,
            "type": "1",
            "category_type": "1",
            "amount": amount
        }

        return self.submit_order(params)

    # =========================
    # LIMIT BUY
    # =========================

    def limit_buy(self,
                  base: str,
                  quote: str,
                  amount: str,
                  price: str):

        params = {
            "base_coin_symbol": base,
            "quote_coin_symbol": quote,
            "type": "1",
            "category_type": "0",
            "price": price,
            "amount": amount
        }

        return self.submit_order(params)

    # =========================
    # MARKET SELL
    # =========================

    def market_sell(self,
                    base: str,
                    quote: str,
                    amount: str):

        params = {
            "base_coin_symbol": base,
            "quote_coin_symbol": quote,
            "type": "0",
            "category_type": "1",
            "amount": amount
        }

        return self.submit_order(params)