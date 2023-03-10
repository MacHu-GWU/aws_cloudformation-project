# -*- coding: utf-8 -*-

import enum
from func_args import NOTHING
from aws_cloudformation.helper import (
    md5_of_text,
    rand_hex,
    get_enum_by_name,
    get_true_flag_count,
)


def test_md5_of_text():
    md5_of_text("hello")


def test_rand_hex():
    rand_hex(32)


def test_get_enum_by_name():
    class MyEnum(str, enum.Enum):
        A = "a"
        B = "b"

    assert get_enum_by_name(MyEnum, "A") == MyEnum.A
    assert get_enum_by_name(MyEnum, "B") == MyEnum.B
    assert get_enum_by_name(MyEnum, None) is None


def test_get_true_flag_count():
    assert get_true_flag_count([True]) == 1
    assert get_true_flag_count([False]) == 0
    assert get_true_flag_count([NOTHING]) == 0
    assert get_true_flag_count([True, False, NOTHING]) == 1


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.helper", preview=False)
