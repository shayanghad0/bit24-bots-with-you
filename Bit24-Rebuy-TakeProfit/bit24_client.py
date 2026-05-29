# file: bit24_client.py

import requests

from decimal import Decimal
from decimal import ROUND_DOWN

from auth import sign_params


class Bit24Client:

    BASE_URL = "https://rest.bit24.cash"

    def __init__(
        self,
        api_key,
        secret_key
    ):

        self.api_key = api_key
        self.secret_key = secret_key

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-BIT24-APIKEY": api_key
        }

    # =========================
    # FORMAT AMOUNT
    # BIT24 MAX 2 DECIMALS
    # =========================

    @staticmethod
    def format_amount(value):

        return str(
            Decimal(value)
            .quantize(
                Decimal("0.01"),
                rounding=ROUND_DOWN
            )
        )

    # =========================
    # GET BEST ASK
    # =========================

    def get_best_ask(
        self,
        base,
        quote
    ):

        url = (
            f"{self.BASE_URL}"
            "/pro/capi/v1/markets/order-books"
        )

        response = requests.get(
            url,
            headers=self.headers,
            params={
                "base_coin": base,
                "quote_coin": quote
            }
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("success"):
            raise Exception(data)

        return Decimal(
            data["data"]["sell_orders"][0]["price"]
        )

    # =========================
    # GET BALANCE
    # =========================

    def get_coin_balance(
        self,
        symbol
    ):

        url = (
            f"{self.BASE_URL}"
            "/asset/capi/v1/wallet/assets"
        )

        response = requests.get(
            url,
            headers=self.headers,
            params={
                "without_zero": "1",
                "without_irt": "0"
            }
        )

        response.raise_for_status()

        assets = (
            response.json()
            .get("data", {})
            .get("asset", [])
        )

        for asset in assets:

            if asset["symbol"] == symbol:

                return Decimal(
                    asset["available_balance"]
                )

        return Decimal("0")

    # =========================
    # SEND ORDER
    # =========================

    def submit_order(
        self,
        params
    ):

        url = (
            f"{self.BASE_URL}"
            "/pro/capi/v1/orders/submit"
        )

        params["signature"] = sign_params(
            self.secret_key,
            params
        )

        response = requests.post(
            url,
            headers=self.headers,
            data=params
        )

        print(
            "\nSTATUS:",
            response.status_code
        )

        print(
            "BODY:",
            response.text
        )

        response.raise_for_status()

        return response.json()

    # =========================
    # MARKET BUY
    # =========================

    def market_buy(
        self,
        base,
        quote,
        spend_irt
    ):

        params = {
            "base_coin_symbol": base,
            "quote_coin_symbol": quote,
            "type": "1",
            "category_type": "1",
            "quote_coin_amount": str(spend_irt)
        }

        return self.submit_order(params)

    # =========================
    # LIMIT BUY
    # =========================

    def limit_buy(
        self,
        base,
        quote,
        amount,
        price
    ):

        params = {
            "base_coin_symbol": base,
            "quote_coin_symbol": quote,
            "type": "1",
            "category_type": "0",
            "price": str(price),
            "amount": self.format_amount(amount)
        }

        return self.submit_order(params)

    # =========================
    # MARKET SELL
    # =========================

    def market_sell(
        self,
        base,
        quote,
        amount
    ):

        params = {
            "base_coin_symbol": base,
            "quote_coin_symbol": quote,
            "type": "0",
            "category_type": "1",
            "amount": self.format_amount(amount)
        }

        return self.submit_order(params)