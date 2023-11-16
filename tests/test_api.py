# -*- coding: utf-8 -*-

import pytest


def test():
    import aws_cloudformation as aws_cf

    _ = aws_cf.better_boto
    _ = aws_cf.better_boto.StackIterProxy
    _ = aws_cf.better_boto.describe_stacks
    _ = aws_cf.better_boto.describe_live_stack
    _ = aws_cf.better_boto.create_stack
    _ = aws_cf.better_boto.update_stack
    _ = aws_cf.better_boto.create_change_set
    _ = aws_cf.better_boto.describe_change_set
    _ = aws_cf.better_boto.describe_change_set_with_paginator
    _ = aws_cf.better_boto.execute_change_set
    _ = aws_cf.better_boto.delete_stack
    _ = aws_cf.better_boto.wait_create_or_update_stack_to_finish
    _ = aws_cf.better_boto.wait_delete_stack_to_finish
    _ = aws_cf.better_boto.wait_create_change_set_to_finish
    _ = aws_cf.better_boto.describe_stack_set
    _ = aws_cf.better_boto.create_stack_set
    _ = aws_cf.better_boto.update_stack_set
    _ = aws_cf.better_boto.delete_stack_set
    _ = aws_cf.better_boto.describe_stack_instance
    _ = aws_cf.better_boto.create_stack_instances
    _ = aws_cf.better_boto.update_stack_instances
    _ = aws_cf.better_boto.delete_stack_instances
    _ = aws_cf.better_boto.StackInstanceIterProxy
    _ = aws_cf.better_boto.list_stack_instances
    _ = aws_cf.better_boto.wait_deploy_stack_instances_to_stop
    _ = aws_cf.exc
    _ = aws_cf.exc.StackNotExistError
    _ = aws_cf.exc.DeployStackFailedError
    _ = aws_cf.exc.DeleteStackFailedError
    _ = aws_cf.exc.CreateStackChangeSetButNotChangeError
    _ = aws_cf.exc.CreateStackChangeSetFailedError
    _ = aws_cf.exc.DeployStackInstanceFailedError
    _ = aws_cf.deploy_stack
    _ = aws_cf.remove_stack
    _ = aws_cf.deploy_stack_set
    _ = aws_cf.remove_stack_set
    _ = aws_cf.StackStatusEnum
    _ = aws_cf.Output
    _ = aws_cf.Parameter
    _ = aws_cf.DriftStatusEnum
    _ = aws_cf.Stack
    _ = aws_cf.ChangeSetStatusEnum
    _ = aws_cf.ChangeSetTypeEnum
    _ = aws_cf.ChangeSetExecutionStatusEnum
    _ = aws_cf.ChangeSet
    _ = aws_cf.StackSetStatusEnum
    _ = aws_cf.StackSetPermissionModelEnum
    _ = aws_cf.StackSetCallAsEnum
    _ = aws_cf.StackSet
    _ = aws_cf.StackInstanceStatusEnum
    _ = aws_cf.StackInstanceDetailedStatusEnum
    _ = aws_cf.StackInstanceDriftStatusEnum
    _ = aws_cf.StackInstance
    _ = aws_cf.TargetAttributeEnum
    _ = aws_cf.Target
    _ = aws_cf.Detail
    _ = aws_cf.ChangeActionEnum
    _ = aws_cf.ResourceChange
    _ = aws_cf.visualize_change_set
    _ = aws_cf.to_tag_list
    _ = aws_cf.to_tag_dict


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
