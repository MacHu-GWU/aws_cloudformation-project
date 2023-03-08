# -*- coding: utf-8 -*-

import pytest

from aws_cloudformation.stack_set import (
    StackSetStatusEnum,
    StackSetPermissionModelEnum,
    StackSetCallAsEnum,
    StackSet,
    StackInstanceStatusEnum,
    StackInstanceDetailedStatusEnum,
    StackInstanceDriftStatusEnum,
    StackInstance,
)


class TestStackSetStatusEnum:
    def test(self):
        assert (None == StackSetStatusEnum.ACTIVE) is False
        assert (None == StackSetStatusEnum.ACTIVE.value) is False
        assert (StackSetStatusEnum.ACTIVE == StackSetStatusEnum.ACTIVE) is True
        assert (StackSetStatusEnum.ACTIVE == StackSetStatusEnum.ACTIVE.value) is True
        assert (StackSetStatusEnum.ACTIVE == StackSetStatusEnum.DELETED) is False
        assert (StackSetStatusEnum.ACTIVE == StackSetStatusEnum.DELETED.value) is False



if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.stack", preview=False)
