# -*- coding: utf-8 -*-

import pytest

from rich import print as rprint
import cottonformation as cf

import aws_cloudformation as aws_cf
from aws_cloudformation.tests.boto_ses import bsm
from aws_cloudformation.tests.stacks.iam_stack import (
    make_tpl_1,
    make_tpl_2,
    make_tpl_3,
    make_tpl_4,
)


def _test_with_change_set():
    # ----------------------------------------------------------------------
    # prepare some variables
    # ----------------------------------------------------------------------
    bucket = f"{bsm.aws_account_id}-{bsm.aws_region}-artifacts"

    project_name = "aws-cf-deploy-test"
    stack_name = project_name
    params = [
        aws_cf.Parameter(
            key="ProjectName",
            value=project_name,
        )
    ]

    bsm.s3_client.create_bucket(Bucket=bucket)
    env = cf.Env(bsm=bsm)

    # ----------------------------------------------------------------------
    # prepare test cases
    # ----------------------------------------------------------------------
    def delete_it():
        aws_cf.remove_stack(
            bsm=bsm,
            stack_name=stack_name,
            skip_prompt=True,
        )

    def deployment_1():
        print("****** deployment 1 ******")
        aws_cf.deploy_stack(
            bsm=bsm,
            stack_name=stack_name,
            bucket=bucket,
            template=make_tpl_1().to_json(),
            parameters=params,
            include_named_iam=True,
            skip_prompt=True,
        )

    def deployment_2():
        print("****** deployment 2 ******")
        aws_cf.deploy_stack(
            bsm=bsm,
            stack_name=stack_name,
            bucket=bucket,
            template=make_tpl_2().to_json(),
            parameters=params,
            include_named_iam=True,
            skip_prompt=True,
        )

    def inspect_output():
        print("****** inspect output ******")
        stack = aws_cf.better_boto.describe_live_stack(bsm=bsm, name=stack_name)
        print(stack.outputs["Policy222Arn"])


    def deployment_3():
        print("****** deployment 3 ******")
        aws_cf.deploy_stack(
            bsm=bsm,
            stack_name=stack_name,
            bucket=bucket,
            template=make_tpl_3().to_json(),
            parameters=params,
            include_named_iam=True,
            skip_prompt=True,
            plan_nested_stack=True,
        )

    def deployment_4():
        print("****** deployment 4 ******")
        tpl = make_tpl_4()

        env.package(tpl, bucket)

        aws_cf.deploy_stack(
            bsm=bsm,
            stack_name=stack_name,
            bucket=bucket,
            template=tpl.to_json(),
            parameters=params,
            include_named_iam=True,
            skip_prompt=True,
            plan_nested_stack=True,
        )

    # delete_it()
    # deployment_1()
    # deployment_2()
    # inspect_output()
    # deployment_3()
    # deployment_4()
    # delete_it()


def _test_without_change_set():
    # ----------------------------------------------------------------------
    # prepare some variables
    # ----------------------------------------------------------------------
    bucket = f"{bsm.aws_account_id}-{bsm.aws_region}-artifacts"

    project_name = "aws-cf-deploy-test"
    stack_name = project_name
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

    bsm.s3_client.create_bucket(Bucket=bucket)
    env = cf.Env(bsm=bsm)

    # ----------------------------------------------------------------------
    # prepare test cases
    # ----------------------------------------------------------------------
    def delete_it():
        aws_cf.remove_stack(
            bsm=bsm,
            stack_name=stack_name,
            skip_prompt=True,
        )

    def deployment_1():
        print("****** deployment 1 ******")
        aws_cf.deploy_stack(
            bsm=bsm,
            stack_name=stack_name,
            bucket=bucket,
            template=make_tpl_1().to_json(),
            parameters=params,
            include_named_iam=True,
            skip_plan=True,
            skip_prompt=True,
        )

    def deployment_2():
        print("****** deployment 2 ******")
        aws_cf.deploy_stack(
            bsm=bsm,
            stack_name=stack_name,
            bucket=bucket,
            template=make_tpl_2().to_json(),
            parameters=params,
            include_named_iam=True,
            skip_plan=True,
            skip_prompt=True,
        )

    def inspect_output():
        print("****** inspect output ******")
        stack = aws_cf.better_boto.describe_live_stack(bsm=bsm, name=stack_name)
        print(stack.outputs["Policy222Arn"])


    def deployment_3():
        print("****** deployment 3 ******")
        aws_cf.deploy_stack(
            bsm=bsm,
            stack_name=stack_name,
            bucket=bucket,
            template=make_tpl_3().to_json(),
            parameters=params,
            include_named_iam=True,
            skip_prompt=True,
            plan_nested_stack=True,
        )

    def deployment_4():
        print("****** deployment 4 ******")
        tpl = make_tpl_4()

        env.package(tpl, bucket)

        aws_cf.deploy_stack(
            bsm=bsm,
            stack_name=stack_name,
            bucket=bucket,
            template=tpl.to_json(),
            parameters=params,
            include_named_iam=True,
            skip_prompt=True,
            plan_nested_stack=True,
        )

    # delete_it()
    # deployment_1()
    # deployment_2()
    # inspect_output()
    # deployment_3()
    # deployment_4()
    # delete_it()


def test():
    _test_with_change_set()
    _test_without_change_set()


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.deploy", preview=True)
