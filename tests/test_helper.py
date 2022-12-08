# -*- coding: utf-8 -*-

from aws_cloudformation.helper import md5_of_text, rand_hex


def test_md5_of_text():
    md5_of_text("hello")


def test_rand_hex():
    rand_hex(32)


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.helper", preview=False)
