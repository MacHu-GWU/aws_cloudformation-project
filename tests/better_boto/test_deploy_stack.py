# -*- coding: utf-8 -*-

from aws_cloudformation.console import (
    parse_stack_id,
    get_stacks_view_console_url,
    get_stack_details_console_url,
    get_change_set_console_url,
    ConsoleHrefEnum,
)
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
        stack_name = "test"

        stacks = aws_cf.better_boto.describe_stacks(
            bsm=self.bsm,
            name=stack_name,
        )
        assert len(stacks) == 0

        # --- deploy stack
        tpl = make_tpl_1()
        params = [
            aws_cf.Parameter(
                key="ProjectName",
                value="aws-cf-int-test"
            )
        ]
        aws_cf.deploy_stack(
            bsm=self.bsm,
            stack_name="test",
            template=tpl.to_json(),
            bucket=self.bucket,
            parameters=params,
            skip_prompt=True,
            include_named_iam=True,
        )

        # --- after
        stacks = aws_cf.better_boto.describe_stacks(
            bsm=self.bsm,
            name=stack_name,
        )
        assert len(stacks) == 1
        assert stacks[0].name == stack_name


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.better_boto.stacks", preview=False)
