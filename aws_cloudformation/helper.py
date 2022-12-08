# -*- coding: utf-8 -*-

import hashlib
import random


def md5_of_text(text: str) -> str:
    md5 = hashlib.md5()
    md5.update(text.encode("utf-8"))
    return md5.hexdigest()


hexdigits = "0123456789abcdef"


def rand_hex(length: int) -> str:
    return "".join([random.choice(hexdigits) for _ in range(length)])
