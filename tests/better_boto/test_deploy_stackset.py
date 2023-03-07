# -*- coding: utf-8 -*-

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
        # print(self.bsm.aws_account_id)
        # ====== begin of 1st deploy =========================================
        stack_set_name = "test"

        stack_set = aws_cf.better_boto.describe_stack_set(
            bsm=self.bsm,
            name=stack_set_name,
        )
        assert stack_set is None

        # --- deploy stack set
        tpl = make_tpl_1()
        params = [
            aws_cf.Parameter(
                key="ProjectName",
                value="aws-cf-int-test"
            )
        ]
        aws_cf.deploy_stack_set(
            bsm=self.bsm,
            stack_set_name=stack_set_name,
            description="1st deploy",
            template_body=tpl.to_json(),
            include_named_iam=True,
            parameters=params,
            tags=dict(Creator="alice"),
        )

        # --- after
        stack_set = aws_cf.better_boto.describe_stack_set(
            bsm=self.bsm,
            name=stack_set_name,
        )
        assert stack_set.description == "1st deploy"
        # rprint(stack_set)
        # ====== end of 1st deploy =========================================
        # ====== begin of 2nd deploy =========================================
        aws_cf.deploy_stack_set(
            bsm=self.bsm,
            stack_set_name=stack_set_name,
            description="2st deploy",
            template_body=tpl.to_json(),
            include_named_iam=True,
            parameters=params,
            tags=dict(Creator="alice"),
        )
        stack_set = aws_cf.better_boto.describe_stack_set(
            bsm=self.bsm,
            name=stack_set_name,
        )
        assert stack_set.description == "2st deploy"
        # ====== end of 2nd deploy =========================================

if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.better_boto.stacks", preview=False)
