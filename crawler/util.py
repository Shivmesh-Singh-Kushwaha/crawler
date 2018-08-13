def make_bytes(val, encoding='utf-8'):
    if isinstance(val, bytes):
        return val
    elif isinstance(val, str):
        return val.encode(encoding)
    else:
        return str(val).encode(encoding)


def make_str(val, encoding='utf-8'):
    if isinstance(val, str):
        return val
    elif isinstance(val, bytes):
        return val.decode(encoding)
    else:
        return str(val)
