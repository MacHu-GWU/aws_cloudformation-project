# -*- coding: utf-8 -*-

import pytest
from rich import print as rprint
import aws_cloudformation as aws_cf

from aws_cloudformation.tests.mocker import BaseTest
from aws_cloudformation.tests.stacks.iam_stack import (
    make_tpl_1,
    make_tpl_2,
    make_tpl_3,
    make_tpl_4,
)


class Test(BaseTest):
    def test(self):
        # ======================================================================
        # Create / Update with ChangeSet
        # ======================================================================
        # ----------------------------------------------------------------------
        # prepare some variables
        # ----------------------------------------------------------------------
        project_name = "aws-cf-better-boto-stacks-test-with-changeset"
        stack_name = project_name
        params = [
            aws_cf.Parameter(
                key="ProjectName",
                value=project_name,
            )
        ]
        tpl1 = make_tpl_1()
        tpl2 = make_tpl_2()

        # ----------------------------------------------------------------------
        # Stack should not exists yet
        # ----------------------------------------------------------------------
        stack_list = aws_cf.better_boto.describe_stacks(
            bsm=self.bsm,
            name=stack_name,
        ).all()
        assert len(stack_list) == 0

        stack = aws_cf.better_boto.describe_live_stack(
            bsm=self.bsm,
            name=stack_name,
        )
        assert stack is None

        # ----------------------------------------------------------------------
        # Change set should not exists yet
        # ----------------------------------------------------------------------
        change_set_name = "cs-1"
        change_set = aws_cf.better_boto.describe_change_set(
            bsm=self.bsm,
            stack_name= stack_name,
            change_set_name=change_set_name,
        )
        assert change_set is None

        # ----------------------------------------------------------------------
        # Create a new change set for CREATE
        # ----------------------------------------------------------------------
        stack_id, change_set_id = aws_cf.better_boto.create_change_set(
            bsm=self.bsm,
            stack_name= stack_name,
            change_set_name=change_set_name,
            template_body=tpl1.to_json(),
            parameters=params,
            include_named_iam=True,
            change_set_type_is_create=True,
        )

        # ----------------------------------------------------------------------
        # wait_create_change_set_to_finish
        # ----------------------------------------------------------------------
        change_set = aws_cf.better_boto.wait_create_change_set_to_finish(
            bsm=self.bsm,
            stack_name=stack_name,
            change_set_id=change_set_id,
            delays=1,
            timeout=3,
            verbose=False,
        )

        change_set1 = aws_cf.better_boto.describe_change_set(
            bsm=self.bsm,
            stack_name=stack_name,
            change_set_name=change_set_name,
        )
        assert change_set.change_set_id == change_set_id
        assert change_set.stack_id == stack_id
        assert change_set1.change_set_id == change_set_id
        assert change_set1.stack_id == stack_id

        assert change_set.is_status_create_complete() is True
        assert change_set1.is_status_create_complete() is True

        assert change_set.changes == change_set1.changes

        # stack is created without any resources
        stack = aws_cf.better_boto.describe_live_stack(
            bsm=self.bsm,
            name=stack_name,
        )
        assert stack is not None

        # ----------------------------------------------------------------------
        # describe full changes in a ChangeSet
        # ----------------------------------------------------------------------
        change_set = aws_cf.better_boto.describe_change_set_with_paginator(
            bsm=self.bsm,
            stack_name=stack_name,
            change_set_name=change_set_id,
        )

        # ----------------------------------------------------------------------
        # Execute a new change set
        # ----------------------------------------------------------------------
        aws_cf.better_boto.execute_change_set(
            bsm=self.bsm,
            stack_name=stack_name,
            change_set_name=change_set_id,
        )

        # ----------------------------------------------------------------------
        # Create a new change set for UPDATE
        # ----------------------------------------------------------------------
        stack_id, change_set_id = aws_cf.better_boto.create_change_set(
            bsm=self.bsm,
            stack_name=stack_name,
            change_set_name=change_set_name,
            template_body=tpl2.to_json(),
            parameters=params,
            include_named_iam=True,
            change_set_type_is_update=True,
        )
        aws_cf.better_boto.execute_change_set(
            bsm=self.bsm,
            stack_name=stack_name,
            change_set_name=change_set_id,
        )

        # ----------------------------------------------------------------------
        # delete the stack
        # ----------------------------------------------------------------------
        aws_cf.better_boto.delete_stack(
            bsm=self.bsm,
            stack_name=stack_name,
        )
        aws_cf.better_boto.wait_delete_stack_to_finish(
            bsm=self.bsm,
            stack_id=stack_id,
            wait_until_exec_stopped=True,
            delays=1,
            timeout=3,
            verbose=False,
        )

        stack = aws_cf.better_boto.describe_live_stack(
            bsm=self.bsm,
            name=stack_name,
        )
        assert stack is None

        # ======================================================================
        # Create / Update without ChangeSet
        # ======================================================================
        # ----------------------------------------------------------------------
        # prepare some variables
        # ----------------------------------------------------------------------
        project_name = "aws-cf-better-boto-stacks-test-without-changeset"
        stack_name = project_name
        params = [
            aws_cf.Parameter(
                key="ProjectName",
                value=project_name,
            )
        ]
        tpl1 = make_tpl_1()
        tpl2 = make_tpl_2()

        # ----------------------------------------------------------------------
        # Create stack without ChangeSet
        # ----------------------------------------------------------------------
        stack = aws_cf.better_boto.describe_live_stack(
            bsm=self.bsm,
            name=stack_name,
        )
        assert stack is None

        stack_id = aws_cf.better_boto.create_stack(
            bsm=self.bsm,
            stack_name=stack_name,
            template_body=tpl1.to_json(),
            parameters=params,
            include_named_iam=True,
        )

        aws_cf.better_boto.wait_create_or_update_stack_to_finish(
            bsm=self.bsm,
            stack_name=stack_name,
            wait_until_exec_stopped=True,
            delays=1,
            timeout=3,
            verbose=False
        )

        stack = aws_cf.better_boto.describe_live_stack(
            bsm=self.bsm,
            name=stack_name,
        )
        assert stack.id == stack_id
        assert stack.status.is_stopped()

        # ----------------------------------------------------------------------
        # Update stack without ChangeSet
        # ----------------------------------------------------------------------
        stack_id = aws_cf.better_boto.update_stack(
            bsm=self.bsm,
            stack_name=stack_name,
            template_body=tpl2.to_json(),
            parameters=params,
            include_named_iam=True,
        )

        aws_cf.better_boto.wait_create_or_update_stack_to_finish(
            bsm=self.bsm,
            stack_name=stack_name,
            wait_until_exec_stopped=True,
            delays=1,
            timeout=3,
            verbose=False
        )

        stack = aws_cf.better_boto.describe_live_stack(
            bsm=self.bsm,
            name=stack_name,
        )
        assert stack.id == stack_id
        assert stack.status.is_stopped()



if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.better_boto.stacks", preview=False)
