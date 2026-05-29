# file: auth.py

import hmac
import hashlib
from urllib.parse import urlencode


def sign_params(secret_key: str, params: dict) -> str:

    query = urlencode(sorted(params.items()))

    signature = hmac.new(
        secret_key.encode(),
        query.encode(),
        hashlib.sha256
    ).hexdigest()

    return signature