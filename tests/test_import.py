# -*- coding: utf-8 -*-

import pytest


def test():
    import aws_cloudformation

    _ = aws_cloudformation.better_boto

    _ = aws_cloudformation.deploy_stack
    _ = aws_cloudformation.remove_stack
    _ = aws_cloudformation.deploy_stack_set
    _ = aws_cloudformation.remove_stack_set

    _ = aws_cloudformation.StackStatusEnum
    _ = aws_cloudformation.Output
    _ = aws_cloudformation.Parameter
    _ = aws_cloudformation.DriftStatusEnum
    _ = aws_cloudformation.Stack
    _ = aws_cloudformation.ChangeSetStatusEnum
    _ = aws_cloudformation.ChangeSetTypeEnum
    _ = aws_cloudformation.ChangeSetExecutionStatusEnum
    _ = aws_cloudformation.ChangeSet

    _ = aws_cloudformation.StackSetStatusEnum
    _ = aws_cloudformation.StackSetPermissionModelEnum
    _ = aws_cloudformation.StackSetCallAsEnum
    _ = aws_cloudformation.StackSet
    _ = aws_cloudformation.StackInstanceStatusEnum
    _ = aws_cloudformation.StackInstanceDetailedStatusEnum
    _ = aws_cloudformation.StackInstanceDriftStatusEnum
    _ = aws_cloudformation.StackInstance

    _ = aws_cloudformation.TargetAttributeEnum
    _ = aws_cloudformation.Target
    _ = aws_cloudformation.Detail
    _ = aws_cloudformation.ChangeActionEnum
    _ = aws_cloudformation.ResourceChange
    _ = aws_cloudformation.visualize_change_set

    _ = aws_cloudformation.to_tag_dict
    _ = aws_cloudformation.to_tag_list


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
