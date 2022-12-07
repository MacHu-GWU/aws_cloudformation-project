# -*- coding: utf-8 -*-

import hashlib


def md5_of_text(text: str) -> str:
    md5 = hashlib.md5()
    md5.update(text.encode("utf-8"))
    return md5.hexdigest()
