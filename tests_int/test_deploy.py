# -*- coding: utf-8 -*-

from aws_cloudformation.deploy import deploy_stack, remove_stack
from aws_cloudformation.tests import bsm
from aws_cloudformation.tests.stacks.secretmanager_stack import (
    make_tpl_1,
    make_tpl_2,
    make_tpl_3,
)


def test_deploy_stack():
    stack_name = "cottonformation-deploy-stack-test"

    # deploy_stack(
    #     bsm,
    #     stack_name=stack_name,
    #     template=make_tpl_1().to_json(),
    #     skip_prompt=True,  # by default, it prompt user input for YES / NO to proceed
    #     # skip_plan=False, # by default, it does plan first
    #     # wait=True, # by default, it waits the update to finish
    # )

    # deploy_stack(
    #     bsm,
    #     stack_name=stack_name,
    #     template=make_tpl_2().to_json(),
    #     skip_prompt=True,
    #     # skip_plan=False,
    #     # wait=True,
    # )

    # deploy_stack(
    #     bsm,
    #     stack_name=stack_name,
    #     template=make_tpl_3().to_json(),
    #     skip_prompt=True,
    #     # skip_plan=False,
    #     # wait=True,
    # )

    remove_stack(
        bsm,
        stack_name=stack_name,
        skip_prompt=True,
    )


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.better_boto", preview=False)
