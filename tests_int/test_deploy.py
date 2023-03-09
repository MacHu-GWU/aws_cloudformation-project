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
    make_tpl_0_malformed,
)

bucket = f"{bsm.aws_account_id}-{bsm.aws_region}-artifacts"


def _test_with_change_set():
    # ----------------------------------------------------------------------
    # prepare some variables
    # ----------------------------------------------------------------------
    project_name = "aws-cf-deploy-with-change-set"
    stack_name = project_name
    params = [
        aws_cf.Parameter(
            key="ProjectName",
            value=project_name,
        )
    ]

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

    delete_it()
    deployment_1()
    deployment_2()
    inspect_output()
    deployment_3()
    deployment_4()
    delete_it()


def _test_without_change_set():
    # ----------------------------------------------------------------------
    # prepare some variables
    # ----------------------------------------------------------------------
    bucket = f"{bsm.aws_account_id}-{bsm.aws_region}-artifacts"

    project_name = "aws-cf-deploy-without-change-set"
    stack_name = project_name
    params = [
        aws_cf.Parameter(
            key="ProjectName",
            value=project_name,
        )
    ]

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
            skip_plan=True,
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
            skip_plan=True,
            skip_prompt=True,
            plan_nested_stack=True,
        )

    delete_it()
    deployment_1()
    deployment_2()
    inspect_output()
    deployment_3()
    deployment_4()
    delete_it()


def _test_malformed_template():
    # ----------------------------------------------------------------------
    # prepare some variables
    # ----------------------------------------------------------------------
    project_name = "aws-cf-deploy-malformed-template"
    stack_name = project_name

    # ----------------------------------------------------------------------
    # prepare test cases
    # ----------------------------------------------------------------------
    def delete_it():
        aws_cf.remove_stack(
            bsm=bsm,
            stack_name=stack_name,
            skip_prompt=True,
        )

    def ensure_stack_not_exist():
        stack = aws_cf.better_boto.describe_live_stack(
            bsm=bsm,
            name=stack_name,
        )
        assert stack is None

    def ensure_stack_exist_and_stopped():
        stack = aws_cf.better_boto.describe_live_stack(
            bsm=bsm,
            name=stack_name,
        )
        assert stack.is_stopped()

    def deployment_will_fail_but_not_deleted():
        aws_cf.deploy_stack(
            bsm=bsm,
            stack_name=stack_name,
            template=make_tpl_0_malformed().to_json(),
            include_named_iam=True,
            skip_plan=True,
            skip_prompt=True,
        )

    def deployment_will_fail_and_deleted():
        aws_cf.deploy_stack(
            bsm=bsm,
            stack_name=stack_name,
            template=make_tpl_0_malformed().to_json(),
            include_named_iam=True,
            on_failure_delete=True,
            skip_plan=True,
            skip_prompt=True,
        )

    delete_it()
    ensure_stack_not_exist()

    deployment_will_fail_but_not_deleted()
    ensure_stack_exist_and_stopped()

    delete_it()
    ensure_stack_not_exist()

    deployment_will_fail_and_deleted()
    ensure_stack_not_exist()


def test():
    _test_with_change_set()
    _test_without_change_set()
    _test_malformed_template()


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.deploy", preview=True)
