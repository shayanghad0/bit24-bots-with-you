# file: strategy.py

import time
from decimal import Decimal
from bit24_client import Bit24Client


# =========================
# CONFIG
# =========================

BASE = "ADA"
QUOTE = "IRT"

# First Market Buy
MARKET_BUY_AMOUNT = "2"

# Second Limit Buy
LIMIT_BUY_AMOUNT = "2"

# Limit Buy Percentage
LIMIT_BUY_DROP_PERCENT = Decimal("0.2")

# Take Profit
TAKE_PROFIT_PERCENT = Decimal("0.73")


class Strategy:

    def __init__(self, client: Bit24Client):

        self.client = client

        self.first_buy_price = Decimal("0")

        self.limit_buy_price = Decimal("0")

        self.last_trade_price = Decimal("0")

        self.sell_target_price = Decimal("0")

    # =========================
    # START
    # =========================

    def start(self):

        print("Getting market price...")

        current_price = self.client.get_best_ask(
            BASE,
            QUOTE
        )

        print(f"Current Price : {current_price}")

        # =========================
        # FIRST BUY
        # MARKET BUY 2 ADA
        # =========================

        print("Executing MARKET BUY...")

        market_buy_response = self.client.market_buy(
            BASE,
            QUOTE,
            MARKET_BUY_AMOUNT
        )

        print(market_buy_response)

        self.first_buy_price = current_price

        print(
            f"First Buy Price : "
            f"{self.first_buy_price}"
        )

        # =========================
        # SECOND BUY
        # LIMIT BUY
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
            f"Creating LIMIT BUY at "
            f"{self.limit_buy_price}"
        )

        limit_buy_response = self.client.limit_buy(
            BASE,
            QUOTE,
            LIMIT_BUY_AMOUNT,
            str(self.limit_buy_price)
        )

        print(limit_buy_response)

        # =========================
        # LAST TRADE PRICE
        # =========================

        self.last_trade_price = self.limit_buy_price

        print(
            f"Last Trade Price : "
            f"{self.last_trade_price}"
        )

        # =========================
        # TARGET SELL PRICE
        # =========================

        self.sell_target_price = (
            self.last_trade_price *
            (
                Decimal("1")
                + TAKE_PROFIT_PERCENT / Decimal("100")
            )
        )

        print(
            f"Target Sell Price : "
            f"{self.sell_target_price}"
        )

        # =========================
        # MONITOR MARKET
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
                # TAKE PROFIT
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