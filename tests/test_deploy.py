# -*- coding: utf-8 -*-

import cottonformation as cf

import aws_cloudformation as aws_cf
from aws_cloudformation.deploy import deploy_stack, remove_stack

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
        bucket = "my-bucket"

        project_name = "aws-cf-deploy-test"
        stack_name = project_name
        params = [
            aws_cf.Parameter(
                key="ProjectName",
                value=project_name,
            )
        ]

        self.bsm.s3_client.create_bucket(Bucket=bucket)
        env = cf.Env(bsm=self.bsm)

        # ----------------------------------------------------------------------
        # prepare test cases
        # ----------------------------------------------------------------------
        def delete_it():
            remove_stack(
                bsm=self.bsm,
                stack_name=stack_name,
                delays=0.1,
                skip_prompt=True,
            )

        def deployment_1():
            print("****** deployment 1 ******")
            deploy_stack(
                bsm=self.bsm,
                stack_name=stack_name,
                bucket=bucket,
                template=make_tpl_1().to_json(),
                parameters=params,
                delays=0.1,
                skip_plan=True,
                skip_prompt=True,
                include_named_iam=True,
            )

        def deployment_2():
            print("****** deployment 2 ******")
            deploy_stack(
                bsm=self.bsm,
                stack_name=stack_name,
                bucket=bucket,
                template=make_tpl_2().to_json(),
                parameters=params,
                delays=0.1,
                change_set_delays=0.1,
                skip_prompt=True,
                include_named_iam=True,
            )

        def deployment_3():
            print("****** deployment 3 ******")
            deploy_stack(
                bsm=self.bsm,
                stack_name=stack_name,
                bucket=bucket,
                template=make_tpl_3().to_json(),
                parameters=params,
                delays=0.1,
                skip_plan=True,
                skip_prompt=True,
                include_named_iam=True,
                plan_nested_stack=True,
            )

        def deployment_4():
            print("****** deployment 4 ******")
            tpl = make_tpl_4()

            env.package(tpl, bucket)

            deploy_stack(
                bsm=self.bsm,
                stack_name=stack_name,
                bucket=bucket,
                template=tpl.to_json(),
                parameters=params,
                delays=0.1,
                change_set_delays=0.1,
                skip_prompt=True,
                include_named_iam=True,
                plan_nested_stack=True,
            )

        delete_it()
        deployment_1()
        deployment_2()
        deployment_3()
        deployment_4()


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.deploy", preview=False)
