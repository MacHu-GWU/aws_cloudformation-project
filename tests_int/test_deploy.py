# -*- coding: utf-8 -*-

import cottonformation as cf
from aws_cloudformation.stack import Parameter
from aws_cloudformation.tests import bsm
from aws_cloudformation.tests.stacks.iam_stack import (
    make_tpl_1,
    make_tpl_2,
    make_tpl_3,
    make_tpl_4,
)
from aws_cloudformation.better_boto import describe_live_stack
from aws_cloudformation.deploy import deploy_stack, remove_stack


env = cf.Env(bsm)


def test_case_1():
    stack_name = "aws-cf-int-test"
    bucket = "aws-data-lab-sanhe-for-everything-us-east-1"

    params = [
        Parameter(
            key="ProjectName",
            value="aws-cf-int-test"
        )
    ]

    def delete_it():
        remove_stack(
            bsm=bsm,
            stack_name=stack_name,
            skip_prompt=True,
        )

    def deployment_1():
        deploy_stack(
            bsm=bsm,
            stack_name=stack_name,
            bucket=bucket,
            template=make_tpl_1().to_json(),
            parameters=params,
            skip_prompt=True,
            include_named_iam=True,
        )

    def deployment_2():
        deploy_stack(
            bsm=bsm,
            stack_name=stack_name,
            bucket=bucket,
            template=make_tpl_2().to_json(),
            parameters=params,
            skip_prompt=True,
            include_named_iam=True,
        )

    def inspect_output():
        stack = describe_live_stack(bsm=bsm, name=stack_name)
        print(stack.outputs["Policy222Arn"])


    def deployment_3():
        deploy_stack(
            bsm=bsm,
            stack_name=stack_name,
            bucket=bucket,
            template=make_tpl_3().to_json(),
            parameters=params,
            skip_prompt=True,
            include_named_iam=True,
            plan_nested_stack=True,
        )

    def deployment_4():
        tpl = make_tpl_4()

        env.package(tpl, bucket)

        deploy_stack(
            bsm=bsm,
            stack_name=stack_name,
            bucket=bucket,
            template=tpl.to_json(),
            parameters=params,
            skip_prompt=True,
            include_named_iam=True,
            plan_nested_stack=True,
        )

    delete_it()
    deployment_1()
    deployment_2()
    inspect_output()
    deployment_3()
    deployment_4()
    delete_it()


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.better_boto")
