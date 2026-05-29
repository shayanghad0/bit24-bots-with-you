# file: auth.py

import hmac
import hashlib


def sign_params(secret_key: str, params: dict) -> str:

    query_string = "&".join(
        f"{k}={params[k]}"
        for k in sorted(params)
    )

    return hmac.new(
        secret_key.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()