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
        # ----------------------------------------------------------------------
        # prepare some variables
        # ----------------------------------------------------------------------
        project_name = "aws-cf-better-boto-stacksets-test"
        stack_set_name = project_name
        params = [
            aws_cf.Parameter(
                key="ProjectName",
                value=project_name,
            )
        ]
        tpl1 = make_tpl_1()
        tpl2 = make_tpl_2()
        tpl3 = make_tpl_3()
        tpl4 = make_tpl_4()

        regions = ["us-east-1", "us-east-2"]
        accounts = ["111111111111", "222222222222", "333333333333"]

        # ----------------------------------------------------------------------
        # Stack set should not exists yet
        # ----------------------------------------------------------------------
        stack_set = aws_cf.better_boto.describe_stack_set(
            bsm=self.bsm,
            name=stack_set_name,
            call_as_self=True,
        )
        assert stack_set is None

        # ----------------------------------------------------------------------
        # Create a stack set definition
        # ----------------------------------------------------------------------
        aws_cf.better_boto.create_stack_set(
            bsm=self.bsm,
            stack_set_name=stack_set_name,
            description="1st deploy",
            template_body=tpl1.to_json(),
            include_named_iam=True,
            parameters=params,
            tags=dict(Creator="alice"),
            call_as_self=True,
        )
        stack_set = aws_cf.better_boto.describe_stack_set(
            bsm=self.bsm,
            name=stack_set_name,
            call_as_self=True,
        )
        assert stack_set.name == stack_set_name

        stack_instance_iterproxy = aws_cf.better_boto.list_stack_instances(
            bsm=self.bsm,
            stack_set_name=stack_set_name,
            call_as_self=True,
        )
        assert len(stack_instance_iterproxy.all()) == 0

        stack_instance = aws_cf.better_boto.describe_stack_instance(
            bsm=self.bsm,
            stack_set_name=stack_set_name,
            stack_instance_account=accounts[0],
            stack_instance_region=regions[0],
            call_as_self=True,
        )
        assert stack_instance is None

        # ----------------------------------------------------------------------
        # Create some stack instances
        # ----------------------------------------------------------------------
        op_id = aws_cf.better_boto.create_stack_instances(
            bsm=self.bsm,
            stack_set_name=stack_set_name,
            regions=regions,
            accounts=accounts,
            call_as_self=True,
        )

        stack_instance_iterproxy = aws_cf.better_boto.list_stack_instances(
            bsm=self.bsm,
            stack_set_name=stack_set_name,
            call_as_self=True,
        )
        assert len(stack_instance_iterproxy.all()) == (len(accounts) * len(regions))

        # ----------------------------------------------------------------------
        # Update stack instances
        # ----------------------------------------------------------------------
        op_id = aws_cf.better_boto.update_stack_instances(
            bsm=self.bsm,
            stack_set_name=stack_set_name,
            regions=regions,
            accounts=accounts,
            param_overrides=[
                aws_cf.Parameter(key="ProjectName", value=f"{project_name}-v1"),
            ],
            call_as_self=True,
        )
        stack_instance = aws_cf.better_boto.describe_stack_instance(
            bsm=self.bsm,
            stack_set_name=stack_set_name,
            stack_instance_account=accounts[0],
            stack_instance_region=regions[0],
            call_as_self=True,
        )
        assert stack_instance.param_overrides["ProjectName"].value == f"{project_name}-v1"

        # ----------------------------------------------------------------------
        # Add more stack instances
        # ----------------------------------------------------------------------
        new_account = "444444444444"
        accounts.append(new_account)
        op_id = aws_cf.better_boto.create_stack_instances(
            bsm=self.bsm,
            stack_set_name=stack_set_name,
            regions=regions,
            accounts=[new_account],
            call_as_self=True,
        )

        stack_instance_iterproxy = aws_cf.better_boto.list_stack_instances(
            bsm=self.bsm,
            stack_set_name=stack_set_name,
            call_as_self=True,
        )
        assert len(stack_instance_iterproxy.all()) == (len(accounts) * len(regions))

        # ----------------------------------------------------------------------
        # Update stack set
        # ----------------------------------------------------------------------
        aws_cf.better_boto.update_stack_set(
            bsm=self.bsm,
            stack_set_name=stack_set_name,
            description="2st deploy",
            template_body=tpl2.to_json(),
            include_named_iam=True,
            parameters=params,
            tags=dict(Creator="bob"),
            call_as_self=True,
        )

        # ----------------------------------------------------------------------
        # Delete stack set, not gonna work
        # ----------------------------------------------------------------------
        with pytest.raises(Exception) as e:
            aws_cf.better_boto.delete_stack_set(
                bsm=self.bsm,
                stack_set_name=stack_set_name,
                call_as_self=True,
            )
        assert "StackSet is not empty" in str(e)

        # ----------------------------------------------------------------------
        # Delete stack instances
        # ----------------------------------------------------------------------
        aws_cf.better_boto.delete_stack_instances(
            bsm=self.bsm,
            stack_set_name=stack_set_name,
            regions=regions,
            accounts=accounts,
            retain_stacks=False,
            call_as_self=True,
        )
        stack_instance_iterproxy = aws_cf.better_boto.list_stack_instances(
            bsm=self.bsm,
            stack_set_name=stack_set_name,
            call_as_self=True,
        )
        assert len(stack_instance_iterproxy.all()) == 0

        # ----------------------------------------------------------------------
        # Delete stack set, not gonna work
        # ----------------------------------------------------------------------
        aws_cf.better_boto.delete_stack_set(
            bsm=self.bsm,
            stack_set_name=stack_set_name,
            call_as_self=True,
        )
        stack_set = aws_cf.better_boto.describe_stack_set(
            bsm=self.bsm,
            name=stack_set_name,
            call_as_self=True,
        )
        assert stack_set is None


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.better_boto.stacksets", preview=False)
