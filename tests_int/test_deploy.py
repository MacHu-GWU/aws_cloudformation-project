# -*- coding: utf-8 -*-

import typing as T
import pytest

from rich import print as rprint
from fixa.timer import DateTimeTimer
import cottonformation as cf

import aws_cloudformation as aws_cf
from aws_cloudformation.tests.boto_ses import bsm
from aws_cloudformation.tests.stacks import (
    happy_path,
    malformed,
    iam_stack,
    secretmanager_stack,
)

from aws_cloudformation.tests.stacks.iam_stack import (
    make_tpl_1,
    make_tpl_2,
    make_tpl_3,
    make_tpl_4,
    make_tpl_0_malformed,
)

bucket = f"{bsm.aws_account_id}-{bsm.aws_region}-artifacts"



# ------------------------------------------------------------------------------
# Helper functions for tests
# ------------------------------------------------------------------------------
def delete_stack(stack_name: str):
    aws_cf.remove_stack(
        bsm=bsm,
        stack_name=stack_name,
        skip_prompt=True,
    )


def ensure_stack_exist_or_not(stack_name: str, exists: bool):
    stack = aws_cf.better_boto.describe_live_stack(
        bsm=bsm,
        name=stack_name,
    )
    if exists:
        assert stack is not None
    else:
        assert stack is None


def deployment(
    stack_name: str,
    template: str,
    params: T.List[aws_cf.Parameter],
    on_failure_delete: bool,
    skip_plan: bool,
    wait_until_exec_stopped_on_failure: bool,
):
    aws_cf.deploy_stack(
        bsm=bsm,
        stack_name=stack_name,
        template=template,
        parameters=params,
        on_failure_delete=on_failure_delete,
        delays=1,
        change_set_delays=1,
        wait_until_exec_stopped_on_failure=wait_until_exec_stopped_on_failure,
        skip_plan=skip_plan,
        skip_prompt=True,
    )


def _test_deploy_happy_path(
    with_change_set: bool,
):
    # ----------------------------------------------------------------------
    # prepare some variables
    # ----------------------------------------------------------------------
    if with_change_set:
        project_name = "aws-cf-deploy-with-change-set"
        skip_plan = False
    else:
        project_name = "aws-cf-deploy-without-change-set"
        skip_plan = True
    stack_name = project_name
    params = [
        aws_cf.Parameter(
            key="ProjectName",
            value=project_name,
        )
    ]

    env = cf.Env(bsm=bsm)

    delete_stack(stack_name)
    ensure_stack_exist_or_not(stack_name, exists=False)

    def deployment_this(template: str):
        deployment(
            stack_name,
            template=template,
            params=params,
            on_failure_delete=False,
            skip_plan=skip_plan,
            wait_until_exec_stopped_on_failure=True,
        )

    # --------------------------------------------------------------------------
    # 1st deployment
    # --------------------------------------------------------------------------
    deployment_this(happy_path.tpl_1)
    ensure_stack_exist_or_not(stack_name, exists=True)

    # --------------------------------------------------------------------------
    # 2nd deployment
    # --------------------------------------------------------------------------
    deployment_this(happy_path.tpl_2)
    ensure_stack_exist_or_not(stack_name, exists=True)

    # --------------------------------------------------------------------------
    # inspect output
    # --------------------------------------------------------------------------
    def inspect_output():
        stack = aws_cf.better_boto.describe_live_stack(bsm=bsm, name=stack_name)
        assert stack.outputs["Database2LogicId"].value == f"{project_name}_database_2"

    inspect_output()

    # --------------------------------------------------------------------------
    # 3rd deployment
    # --------------------------------------------------------------------------
    deployment_this(happy_path.tpl_3)
    ensure_stack_exist_or_not(stack_name, exists=True)

    # --------------------------------------------------------------------------
    # 4th deployment
    # --------------------------------------------------------------------------
    tpl = happy_path.make_tpl_4()
    env.package(tpl, bucket)
    deployment_this(tpl.to_json())
    ensure_stack_exist_or_not(stack_name, exists=True)

    # ----------------------------------------------------------------------
    # clean the stack at the end
    # ----------------------------------------------------------------------
    delete_stack(stack_name)
    ensure_stack_exist_or_not(stack_name, exists=False)


def _test_creation_failed_with_change_set():
    # ----------------------------------------------------------------------
    # prepare some variables
    # ----------------------------------------------------------------------
    project_name = "aws-cf-creation-failed-with-change-set"
    stack_name = project_name
    params = [
        aws_cf.Parameter(key="ProjectName", value=project_name),
    ]

    delete_stack(stack_name)
    ensure_stack_exist_or_not(stack_name, exists=False)

    # ----------------------------------------------------------------------
    # first creation with ChangeSet
    # the stack creation failed, but the stack is still in ROLLBACK_COMPLETE
    # you cannot create / update it
    # ----------------------------------------------------------------------
    with pytest.raises(aws_cf.exc.DeployStackFailedError):
        deployment(
            stack_name,
            template=malformed.tpl_0_malformed,
            params=params,
            on_failure_delete=False,
            skip_plan=False,
            wait_until_exec_stopped_on_failure=True,
        )
    ensure_stack_exist_or_not(stack_name, exists=True)

    # ----------------------------------------------------------------------
    # the stack is still in ROLLBACK_COMPLETE you cannot create / update it
    # ----------------------------------------------------------------------
    with pytest.raises(Exception):
        deployment(
            stack_name,
            template=malformed.tpl_1,
            params=params,
            on_failure_delete=False,
            skip_plan=False,
            wait_until_exec_stopped_on_failure=True,
        )

    # ----------------------------------------------------------------------
    # delete the stack so we can create new stack
    # ----------------------------------------------------------------------
    delete_stack(stack_name)
    ensure_stack_exist_or_not(stack_name, exists=False)

    # ----------------------------------------------------------------------
    # then we can deploy a new stack, and it will succeed
    # ----------------------------------------------------------------------
    deployment(
        stack_name,
        template=malformed.tpl_1,
        params=params,
        on_failure_delete=False,
        skip_plan=False,
        wait_until_exec_stopped_on_failure=True,
    )
    ensure_stack_exist_or_not(stack_name, exists=True)

    # ----------------------------------------------------------------------
    # then we can deploy the same stack, and it will show some message
    # and succeed
    # ----------------------------------------------------------------------
    deployment(
        stack_name,
        template=malformed.tpl_1,
        params=params,
        on_failure_delete=False,
        skip_plan=False,
        wait_until_exec_stopped_on_failure=True,
    )
    ensure_stack_exist_or_not(stack_name, exists=True)

    # ----------------------------------------------------------------------
    # then we can update the stack, and it will fail and raise error
    # on_failure_delete is ignored since it is not a create
    # ----------------------------------------------------------------------
    with pytest.raises(aws_cf.exc.DeployStackFailedError):
        deployment(
            stack_name,
            template=malformed.tpl_2_malformed,
            params=params,
            on_failure_delete=True,
            skip_plan=False,
            wait_until_exec_stopped_on_failure=True,
        )
    ensure_stack_exist_or_not(stack_name, exists=True)

    # ----------------------------------------------------------------------
    # clean the stack at the end
    # ----------------------------------------------------------------------
    delete_stack(stack_name)
    ensure_stack_exist_or_not(stack_name, exists=False)


def _test_creation_failed_without_change_set():
    # ----------------------------------------------------------------------
    # prepare some variables
    # ----------------------------------------------------------------------
    project_name = "aws-cf-creation-failed-without-change-set"
    stack_name = project_name
    params = [
        aws_cf.Parameter(key="ProjectName", value=project_name),
    ]

    delete_stack(stack_name)
    ensure_stack_exist_or_not(stack_name, exists=False)

    # ----------------------------------------------------------------------
    # first creation without ChangeSet
    # the stack creation failed, but the stack is still in ROLLBACK_COMPLETE
    # you cannot create / update it
    # ----------------------------------------------------------------------
    with pytest.raises(aws_cf.exc.DeployStackFailedError):
        deployment(
            stack_name,
            template=malformed.tpl_0_malformed,
            params=params,
            on_failure_delete=False,
            skip_plan=True,
            wait_until_exec_stopped_on_failure=True,
        )
    ensure_stack_exist_or_not(stack_name, exists=True)

    # ----------------------------------------------------------------------
    # the stack is still in ROLLBACK_COMPLETE you cannot create / update it
    # ----------------------------------------------------------------------
    with pytest.raises(Exception):
        deployment(
            stack_name,
            template=malformed.tpl_1,
            params=params,
            on_failure_delete=False,
            skip_plan=True,
            wait_until_exec_stopped_on_failure=True,
        )

    # ----------------------------------------------------------------------
    # clean the stack before start creating new one
    # ----------------------------------------------------------------------
    delete_stack(stack_name)
    ensure_stack_exist_or_not(stack_name, exists=False)

    # ----------------------------------------------------------------------
    # create a new stack with ``on_failure_delete = True``
    # it will fail and automatically delete it, and it won't raise exception
    # ----------------------------------------------------------------------
    deployment(
        stack_name,
        template=malformed.tpl_0_malformed,
        params=params,
        on_failure_delete=True,
        skip_plan=True,
        wait_until_exec_stopped_on_failure=True,
    )
    ensure_stack_exist_or_not(stack_name, exists=False)

    # ----------------------------------------------------------------------
    # then we can deploy a new stack, and it will succeed
    # ----------------------------------------------------------------------
    deployment(
        stack_name,
        template=malformed.tpl_1,
        params=params,
        on_failure_delete=False,
        skip_plan=True,
        wait_until_exec_stopped_on_failure=True,
    )
    ensure_stack_exist_or_not(stack_name, exists=True)

    # ----------------------------------------------------------------------
    # then we can deploy the same stack, and it will show some message
    # and succeed
    # ----------------------------------------------------------------------
    deployment(
        stack_name,
        template=malformed.tpl_1,
        params=params,
        on_failure_delete=False,
        skip_plan=True,
        wait_until_exec_stopped_on_failure=True,
    )
    ensure_stack_exist_or_not(stack_name, exists=True)

    # ----------------------------------------------------------------------
    # then we can update the stack, and it will fail and raise error
    # on_failure_delete is ignored since it is not a create
    # ----------------------------------------------------------------------
    with pytest.raises(aws_cf.exc.DeployStackFailedError):
        deployment(
            stack_name,
            template=malformed.tpl_2_malformed,
            params=params,
            on_failure_delete=True,
            skip_plan=True,
            wait_until_exec_stopped_on_failure=True,
        )
    ensure_stack_exist_or_not(stack_name, exists=True)

    # ----------------------------------------------------------------------
    # clean the stack at the end
    # ----------------------------------------------------------------------
    delete_stack(stack_name)
    ensure_stack_exist_or_not(stack_name, exists=False)


def _test_deploy_stack_set_happy_path():
    # ----------------------------------------------------------------------
    # prepare some variables
    # ----------------------------------------------------------------------
    project_name = "aws-cf-deploy-stack-set"
    stack_set_name = project_name
    params = [
        aws_cf.Parameter(key="ProjectName", value=project_name),
    ]

    aws_cf.deploy_stack_set(
        bsm=bsm,
        stack_set_name=stack_set_name,
        template=happy_path.tpl_1,
        parameters=params,
        permission_model_is_service_managed=True,
        auto_deployment_is_enabled=False,
        call_as_delegated_admin=True,
    )


def test():
    print("")
    with DateTimeTimer():
        # _test_deploy_happy_path(with_change_set=False)
        # _test_deploy_happy_path(with_change_set=True)
        #
        # _test_creation_failed_with_change_set()
        # _test_creation_failed_without_change_set()

        _test_deploy_stack_set_happy_path()


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.deploy", preview=False)
