# -*- coding: utf-8 -*-

import cottonformation as cf

import aws_cloudformation as aws_cf
from aws_cloudformation.deploy import (
    deploy_stack,
    remove_stack,
    deploy_stack_set,
    remove_stack_set,
)

from aws_cloudformation.tests.mocker import BaseTest
from aws_cloudformation.tests.stacks.iam_stack import (
    make_tpl_1,
    make_tpl_2,
    make_tpl_3,
    make_tpl_4,
)


class Test(BaseTest):
    def _test_stack(self):
        # ----------------------------------------------------------------------
        # prepare some variables
        # ----------------------------------------------------------------------
        project_name = "aws-cf-deploy-stack-test"
        stack_name = project_name
        params = [
            aws_cf.Parameter(
                key="ProjectName",
                value=project_name,
            )
        ]

        env = cf.Env(bsm=self.bsm)

        # ----------------------------------------------------------------------
        # prepare test cases
        # ----------------------------------------------------------------------
        def delete_stack():
            remove_stack(
                bsm=self.bsm,
                stack_name=stack_name,
                delays=0.1,
                skip_prompt=True,
            )

        def deployment(
            ith: int,
            tpl: cf.Template,
            has_nested: bool = False,
        ):
            print(f"****** deployment {ith} ******")
            if has_nested:
                env.package(tpl, self.bucket)
            return deploy_stack(
                bsm=self.bsm,
                stack_name=stack_name,
                template=tpl.to_json(),
                bucket=self.bucket,
                parameters=params,
                delays=0.1,
                skip_plan=True,
                skip_prompt=True,
                include_named_iam=True,
            )

        delete_stack()
        response = deployment(ith=1, tpl=make_tpl_1())
        assert response.is_deploy_happened is True
        assert response.is_create is True

        response = deployment(ith=1, tpl=make_tpl_1())
        assert response.is_deploy_happened is False
        assert response.is_create is None
        assert response.stack_id is None
        assert response.change_set_id is None

        response = deployment(ith=2, tpl=make_tpl_2())
        assert response.is_deploy_happened is True
        assert response.is_create is False

        response = deployment(ith=3, tpl=make_tpl_3())
        assert response.is_deploy_happened is True
        assert response.is_create is False

        response = deployment(ith=4, tpl=make_tpl_4(), has_nested=True)
        assert response.is_deploy_happened is True
        assert response.is_create is False

    def _test_stack_set(self):
        # ----------------------------------------------------------------------
        # prepare some variables
        # ----------------------------------------------------------------------
        project_name = "aws-cf-deploy-stack-set-test"
        stack_set_name = project_name
        params = [
            aws_cf.Parameter(
                key="ProjectName",
                value=project_name,
            )
        ]

        env = cf.Env(bsm=self.bsm)

        # ----------------------------------------------------------------------
        # prepare test cases
        # ----------------------------------------------------------------------
        def delete_stack_set():
            remove_stack_set(
                bsm=self.bsm,
                stack_set_name=stack_set_name,
            )

        def deployment(
            ith: int,
            tpl: cf.Template,
        ):
            print(f"****** deployment {ith} ******")
            deploy_stack_set(
                bsm=self.bsm,
                stack_set_name=stack_set_name,
                template=tpl.to_json(),
                bucket=self.bucket,
                parameters=params,
            )

        delete_stack_set()
        deployment(ith=1, tpl=make_tpl_1())
        deployment(ith=2, tpl=make_tpl_2())

    def test(self):
        self._test_stack()
        self._test_stack_set()


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.deploy", preview=False)
