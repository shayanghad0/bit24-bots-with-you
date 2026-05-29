# file: strategy.py

import time
import signal
import sys

from decimal import Decimal

from trade_storage import save_trade


BASE = "ADA"
QUOTE = "IRT"

# MARKET BUY
MARKET_BUY_SPEND = "200000"

# LIMIT BUY
LIMIT_BUY_AMOUNT = "2"

# REBUY %
LIMIT_BUY_DROP_PERCENT = Decimal("0.2")

# TAKE PROFIT %
TAKE_PROFIT_PERCENT = Decimal("0.73")


class Strategy:

    def __init__(
        self,
        client
    ):

        self.client = client

        self.limit_price = Decimal("0")

        self.sell_target = Decimal("0")

        signal.signal(
            signal.SIGINT,
            self.ctrl_c_handler
        )

    # =========================
    # CTRL + C
    # =========================

    def ctrl_c_handler(
        self,
        sig,
        frame
    ):

        print(
            "\nCTRL+C detected."
        )

        try:

            balance = (
                self.client
                .get_coin_balance(BASE)
            )

            print(
                f"Balance: {balance}"
            )

            if balance <= 0:

                print(
                    "No balance found."
                )

                sys.exit(0)

            response = (
                self.client
                .market_sell(
                    BASE,
                    QUOTE,
                    balance
                )
            )

            save_trade(
                "CTRL_C_SELL",
                BASE,
                balance,
                "MARKET",
                response
            )

            print(
                "Emergency sell completed."
            )

        except Exception as e:

            print(
                "Emergency sell error:",
                e
            )

        sys.exit(0)

    # =========================
    # START
    # =========================

    def start(self):

        current_price = (
            self.client
            .get_best_ask(
                BASE,
                QUOTE
            )
        )

        print(
            f"Current Price: {current_price}"
        )

        # =========================
        # MARKET BUY
        # =========================

        market_response = (
            self.client
            .market_buy(
                BASE,
                QUOTE,
                MARKET_BUY_SPEND
            )
        )

        save_trade(
            "MARKET_BUY",
            BASE,
            MARKET_BUY_SPEND,
            current_price,
            market_response
        )

        print(
            "Market Buy Success."
        )

        # =========================
        # LIMIT BUY
        # =========================

        self.limit_price = (
            current_price
            * (
                Decimal("1")
                - (
                    LIMIT_BUY_DROP_PERCENT
                    / Decimal("100")
                )
            )
        )

        self.limit_price = (
            self.limit_price
            .quantize(
                Decimal("1")
            )
        )

        print(
            f"Limit Buy Price: "
            f"{self.limit_price}"
        )

        limit_response = (
            self.client
            .limit_buy(
                BASE,
                QUOTE,
                LIMIT_BUY_AMOUNT,
                self.limit_price
            )
        )

        save_trade(
            "LIMIT_BUY",
            BASE,
            LIMIT_BUY_AMOUNT,
            self.limit_price,
            limit_response
        )

        print(
            "Limit Buy Created."
        )

        # =========================
        # LAST TRADE TARGET
        # =========================

        self.sell_target = (
            self.limit_price
            * (
                Decimal("1")
                + (
                    TAKE_PROFIT_PERCENT
                    / Decimal("100")
                )
            )
        )

        print(
            f"Sell Target: "
            f"{self.sell_target}"
        )

        # =========================
        # LOOP
        # =========================

        while True:

            try:

                price = (
                    self.client
                    .get_best_ask(
                        BASE,
                        QUOTE
                    )
                )

                print(
                    f"Current: {price} | "
                    f"Target: {self.sell_target}"
                )

                if price >= self.sell_target:

                    balance = (
                        self.client
                        .get_coin_balance(BASE)
                    )

                    if balance <= 0:

                        print(
                            "No balance."
                        )

                        break

                    response = (
                        self.client
                        .market_sell(
                            BASE,
                            QUOTE,
                            balance
                        )
                    )

                    save_trade(
                        "TAKE_PROFIT_SELL",
                        BASE,
                        balance,
                        price,
                        response
                    )

                    print(
                        "Take Profit Hit."
                    )

                    break

                time.sleep(5)

            except Exception as e:

                print(
                    "Loop Error:",
                    e
                )

                time.sleep(5)