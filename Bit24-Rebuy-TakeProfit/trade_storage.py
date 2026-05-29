# file: trade_storage.py

import json
import os
from datetime import datetime

TRADE_FILE = "trade.json"


def ensure_trade_file():

    if not os.path.exists(TRADE_FILE):

        with open(
            TRADE_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                [],
                f,
                indent=4,
                ensure_ascii=False
            )


def save_trade(
    trade_type,
    coin,
    amount,
    price,
    response
):

    ensure_trade_file()

    with open(
        TRADE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    data.append(
        {
            "time": datetime.now().isoformat(),
            "type": trade_type,
            "coin": coin,
            "amount": str(amount),
            "price": str(price),
            "response": response
        }
    )

    with open(
        TRADE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )