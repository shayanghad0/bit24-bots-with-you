# file: strategy.py

import time
from decimal import Decimal
from bit24_client import Bit24Client


# =========================
# CONFIG
# =========================

BASE = "ADA"
QUOTE = "IRT"

# MARKET BUY SPEND
# IRT Amount
MARKET_BUY_SPEND = "200000"

# LIMIT BUY AMOUNT
LIMIT_BUY_AMOUNT = "2"

# BUY DIP %
LIMIT_BUY_DROP_PERCENT = Decimal("0.2")

# TAKE PROFIT %
TAKE_PROFIT_PERCENT = Decimal("0.73")


class Strategy:

    def __init__(self,
                 client: Bit24Client):

        self.client = client

        self.first_buy_price = Decimal("0")

        self.limit_buy_price = Decimal("0")

        self.last_trade_price = Decimal("0")

        self.sell_target_price = Decimal("0")

    # =========================
    # START BOT
    # =========================

    def start(self):

        # =========================
        # GET CURRENT PRICE
        # =========================

        current_price = self.client.get_best_ask(
            BASE,
            QUOTE
        )

        print(f"Current Price : {current_price}")

        # =========================
        # MARKET BUY
        # =========================

        print("Executing MARKET BUY...")

        market_response = self.client.market_buy(
            BASE,
            QUOTE,
            MARKET_BUY_SPEND
        )

        print(market_response)

        self.first_buy_price = current_price

        print(
            f"First Buy Price : "
            f"{self.first_buy_price}"
        )

        # =========================
        # LIMIT BUY PRICE
        # =========================

        self.limit_buy_price = (
            current_price *
            (
                Decimal("1")
                - LIMIT_BUY_DROP_PERCENT / Decimal("100")
            )
        )

        self.limit_buy_price = self.limit_buy_price.quantize(
            Decimal("1")
        )

        print(
            f"Limit Buy Price : "
            f"{self.limit_buy_price}"
        )

        # =========================
        # CREATE LIMIT BUY
        # =========================

        limit_response = self.client.limit_buy(
            BASE,
            QUOTE,
            LIMIT_BUY_AMOUNT,
            str(self.limit_buy_price)
        )

        print(limit_response)

        # =========================
        # LAST TRADE PRICE
        # =========================

        self.last_trade_price = self.limit_buy_price

        print(
            f"Last Trade Price : "
            f"{self.last_trade_price}"
        )

        # =========================
        # TAKE PROFIT TARGET
        # =========================

        self.sell_target_price = (
            self.last_trade_price *
            (
                Decimal("1")
                + TAKE_PROFIT_PERCENT / Decimal("100")
            )
        )

        print(
            f"Take Profit Price : "
            f"{self.sell_target_price}"
        )

        # =========================
        # LOOP
        # =========================

        while True:

            try:

                current_price = self.client.get_best_ask(
                    BASE,
                    QUOTE
                )

                print(
                    f"Current : {current_price} | "
                    f"Target : {self.sell_target_price}"
                )

                # =========================
                # SELL ALL
                # =========================

                if current_price >= self.sell_target_price:

                    balance = self.client.get_coin_balance(
                        BASE
                    )

                    print(
                        f"Selling ALL {BASE} : "
                        f"{balance}"
                    )

                    sell_response = self.client.market_sell(
                        BASE,
                        QUOTE,
                        str(balance)
                    )

                    print(sell_response)

                    print("Take Profit Executed.")

                    break

                time.sleep(5)

            except Exception as error:

                print(error)

                time.sleep(5)