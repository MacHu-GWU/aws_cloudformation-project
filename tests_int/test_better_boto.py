# -*- coding: utf-8 -*-

from aws_cloudformation.better_boto import (
    describe_stacks,
    describe_live_stack,
)
from aws_cloudformation.tests import bsm


def test_describe_stacks():
    assert describe_stacks(bsm, name="this-stack-not-exists") == []
    assert describe_live_stack(bsm, name="this-stack-not-exists") is None


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.better_boto", preview=False)
