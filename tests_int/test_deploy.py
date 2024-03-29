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
)

bucket = "cf-templates-x33wndcdbt1e-us-east-1"


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


def deploy_stack(
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
        timeout=180,
        change_set_delays=1,
        change_set_timeout=180,
        wait_until_exec_stopped_on_failure=wait_until_exec_stopped_on_failure,
        skip_plan=skip_plan,
        skip_prompt=True,
    )


def describe_stack_set(
    stack_set_name: str,
) -> T.Optional[aws_cf.StackSet]:
    stack_set = aws_cf.better_boto.describe_stack_set(
        bsm=bsm, name=stack_set_name, call_as_delegated_admin=True
    )
    if stack_set is not None:
        print(f"preview stack set: {stack_set.console_url}")
    return stack_set


def delete_stack_set(stack_set_name: str):
    aws_cf.remove_stack_set(
        bsm=bsm,
        stack_set_name=stack_set_name,
        call_as_delegated_admin=True,
    )


def ensure_stack_set_exist_or_not(stack_set_name: str, exists: bool):
    stack_set = aws_cf.better_boto.describe_stack_set(
        bsm=bsm,
        name=stack_set_name,
        call_as_delegated_admin=True,
    )
    if exists:
        assert stack_set is not None
    else:
        assert stack_set is None


def deploy_stack_set(
    stack_set_name: str,
    template: str,
    params: T.List[aws_cf.Parameter],
) -> T.Tuple[bool, str]:
    return aws_cf.deploy_stack_set(
        bsm=bsm,
        stack_set_name=stack_set_name,
        template=template,
        parameters=params,
        permission_model_is_service_managed=True,
        auto_deployment_is_enabled=False,
        call_as_delegated_admin=True,
    )


def _deploy_stack_instances(
    stack_set_name: str,
    ou_id_list: T.List[str],
    func: T.Callable,
):
    kwargs = dict(
        bsm=bsm,
        stack_set_name=stack_set_name,
        regions=["us-east-1"],
        deployment_targets=dict(
            OrganizationalUnitIds=ou_id_list,
        ),
        call_as_delegated_admin=True,
    )
    if func.__name__ == "delete_stack_instances":
        kwargs["retain_stacks"] = False
    func(**kwargs)


def create_stack_instances(
    stack_set_name: str,
    ou_id_list: T.List[str],
):
    _deploy_stack_instances(
        stack_set_name=stack_set_name,
        ou_id_list=ou_id_list,
        func=aws_cf.better_boto.create_stack_instances,
    )


def update_stack_instances(
    stack_set_name: str,
    ou_id_list: T.List[str],
):
    _deploy_stack_instances(
        stack_set_name=stack_set_name,
        ou_id_list=ou_id_list,
        func=aws_cf.better_boto.update_stack_instances,
    )


def delete_stack_instances(
    stack_set_name: str,
    ou_id_list: T.List[str],
):
    _deploy_stack_instances(
        stack_set_name=stack_set_name,
        ou_id_list=ou_id_list,
        func=aws_cf.better_boto.delete_stack_instances,
    )


def wait_deploy_stack_instances_to_stop(
    stack_set_name: str,
):
    stack_instances = aws_cf.better_boto.wait_deploy_stack_instances_to_stop(
        bsm=bsm,
        stack_set_name=stack_set_name,
        raise_error_until_exec_stopped=True,
        delays=5,
        timeout=120,
        verbose=True,
        call_as_delegated_admin=True,
    )
    # rprint(stack_instances)


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
        deploy_stack(
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
        deploy_stack(
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
        deploy_stack(
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
    deploy_stack(
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
    deploy_stack(
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
        deploy_stack(
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
        deploy_stack(
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
        deploy_stack(
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
    deploy_stack(
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
    deploy_stack(
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
    deploy_stack(
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
        deploy_stack(
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

    stack_set = describe_stack_set(stack_set_name)

    # ----------------------------------------------------------------------
    # get organizational id from aws_organizations
    # ----------------------------------------------------------------------
    import aws_organizations as aws_orgs

    org_struct = aws_orgs.OrgStructure.get_org_structure(bsm)
    ou_id_infra = org_struct.get_node_by_name("infra").id
    ou_id_app = org_struct.get_node_by_name("app").id

    # ----------------------------------------------------------------------
    # clean possible existing stack at begin
    # ----------------------------------------------------------------------
    if stack_set:
        delete_stack_instances(stack_set_name, [ou_id_infra, ou_id_app])
        wait_deploy_stack_instances_to_stop(stack_set_name)
    delete_stack_set(stack_set_name)
    ensure_stack_set_exist_or_not(stack_set_name, exists=False)

    # ----------------------------------------------------------------------
    # create a new stack set
    # ----------------------------------------------------------------------
    is_create, stack_set_id = deploy_stack_set(
        stack_set_name,
        template=happy_path.tpl_1,
        params=params,
    )
    assert is_create is True
    ensure_stack_set_exist_or_not(stack_set_name, exists=True)
    describe_stack_set(stack_set_name)

    # ----------------------------------------------------------------------
    # create initial stack instances
    # ----------------------------------------------------------------------
    create_stack_instances(
        stack_set_name,
        [ou_id_infra],
    )
    wait_deploy_stack_instances_to_stop(stack_set_name)

    # ----------------------------------------------------------------------
    # create more stack instances
    # ----------------------------------------------------------------------
    create_stack_instances(
        stack_set_name,
        [ou_id_app],
    )
    wait_deploy_stack_instances_to_stop(stack_set_name)

    # ----------------------------------------------------------------------
    # update the stack set
    # ----------------------------------------------------------------------
    is_create, stack_set_id = deploy_stack_set(
        stack_set_name,
        template=happy_path.tpl_2,
        params=params,
    )
    assert is_create is False
    ensure_stack_set_exist_or_not(stack_set_name, exists=True)
    wait_deploy_stack_instances_to_stop(stack_set_name)

    # ----------------------------------------------------------------------
    # delete all stack instances
    # ----------------------------------------------------------------------
    delete_stack_instances(stack_set_name, [ou_id_infra, ou_id_app])
    wait_deploy_stack_instances_to_stop(stack_set_name)

    # ----------------------------------------------------------------------
    # clean stack at the end
    # ----------------------------------------------------------------------
    delete_stack_set(stack_set_name)
    ensure_stack_set_exist_or_not(stack_set_name, exists=False)


def test():
    print("")
    with DateTimeTimer():
        _test_deploy_happy_path(with_change_set=False)
        _test_deploy_happy_path(with_change_set=True)

        _test_creation_failed_with_change_set()
        _test_creation_failed_without_change_set()

        _test_deploy_stack_set_happy_path()


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.deploy", preview=False)
