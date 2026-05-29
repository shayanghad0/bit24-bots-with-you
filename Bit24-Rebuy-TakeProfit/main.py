# file: main.py

from bit24_client import Bit24Client
from strategy import Strategy


API_KEY = input(
    "API KEY : "
)

SECRET_KEY = input(
    "SECRET KEY : "
)

client = Bit24Client(
    API_KEY,
    SECRET_KEY
)

bot = Strategy(client)

bot.start()