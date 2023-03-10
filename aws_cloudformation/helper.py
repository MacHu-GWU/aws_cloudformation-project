# -*- coding: utf-8 -*-

import typing as T
import enum
import random
import hashlib
from func_args import NOTHING


def md5_of_text(text: str) -> str:
    md5 = hashlib.md5()
    md5.update(text.encode("utf-8"))
    return md5.hexdigest()


hexdigits = "0123456789abcdef"


def rand_hex(length: int) -> str:
    return "".join([random.choice(hexdigits) for _ in range(length)])


def get_enum_by_name(enum_class: T.Type[enum.Enum], name: T.Optional[str]):
    if name is None:
        return None
    else:
        return enum_class[name]


def get_true_flag_count(args: T.List[T.Optional[bool]]) -> int:
    return sum([False if arg is NOTHING else arg for arg in args])
