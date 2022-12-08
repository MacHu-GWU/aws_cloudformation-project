# -*- coding: utf-8 -*-

import pytest


def test():
    import aws_cloudformation

    _ = aws_cloudformation.deploy_stack
    _ = aws_cloudformation.remove_stack

    _ = aws_cloudformation.describe_live_stack
    _ = aws_cloudformation.StackStatusEnum
    _ = aws_cloudformation.DriftStatusEnum
    _ = aws_cloudformation.Parameter
    _ = aws_cloudformation.Output
    _ = aws_cloudformation.Stack
    _ = aws_cloudformation.TargetAttributeEnum
    _ = aws_cloudformation.Target
    _ = aws_cloudformation.Detail
    _ = aws_cloudformation.ChangeActionEnum
    _ = aws_cloudformation.ResourceChange
    _ = aws_cloudformation.ChangeSet


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
