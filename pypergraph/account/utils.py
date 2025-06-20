def normalize_public_key(public_key: str) -> str:
    if len(public_key) == 130:
        return public_key[2:]
    elif len(public_key) == 128:
        return public_key
    else:
        raise ValueError("Public key has wrong length")
