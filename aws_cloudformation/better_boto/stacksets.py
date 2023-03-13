# -*- coding: utf-8 -*-

"""
AWS CloudFormation StackSet related operations.
"""

import typing as T

from boto_session_manager import BotoSesManager
from iterproxy import IterProxy
from func_args import NOTHING, resolve_kwargs
from aws_console_url import AWSConsole

from .. import exc
from ..stack import (
    Parameter,
)
from ..stack_set import (
    StackSet,
    StackInstanceStatusEnum,
    StackInstanceDetailedStatusEnum,
    StackInstance,
)
from .stacksets_helpers import (
    resolve_callas_kwargs,
    resolve_create_update_stack_set_common_kwargs,
    resolve_create_update_stack_instances_common_kwargs,
    get_stack_set_info_console_url,
    get_stack_set_instances_console_url,
)
from ..waiter import Waiter


def describe_stack_set(
    bsm: BotoSesManager,
    name: str,
    call_as_self: T.Optional[bool] = NOTHING,
    call_as_delegated_admin: T.Optional[bool] = NOTHING,
) -> T.Optional[StackSet]:
    """
    Ref:

    - describe_stack_set: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/describe_stack_set.html#describe_stack_set
    """
    kwargs = dict(StackSetName=name)
    resolve_callas_kwargs(
        kwargs,
        call_as_self=call_as_self,
        call_as_delegated_admin=call_as_delegated_admin,
    )
    try:
        res = bsm.cloudformation_client.describe_stack_set(**kwargs)
        stack_set = StackSet.from_describe_stack_set_response(res["StackSet"])
        return stack_set
    except Exception as e:
        if "StackSetNotFoundException" in str(e):
            return None
        else:  # pragma: no cover
            raise e


def create_stack_set(
    bsm: BotoSesManager,
    stack_set_name: str,
    description: T.Optional[str] = NOTHING,
    template_body: T.Optional[str] = NOTHING,
    template_url: T.Optional[str] = NOTHING,
    stack_id: T.Optional[str] = NOTHING,
    parameters: T.Optional[T.List[Parameter]] = NOTHING,
    tags: T.Optional[T.Dict[str, str]] = NOTHING,
    include_iam: T.Optional[bool] = NOTHING,
    include_named_iam: T.Optional[bool] = NOTHING,
    include_macro: T.Optional[bool] = NOTHING,
    admin_role_arn: T.Optional[str] = NOTHING,
    execution_role_name: T.Optional[str] = NOTHING,
    permission_model_is_self_managed: T.Optional[bool] = NOTHING,
    permission_model_is_service_managed: T.Optional[bool] = NOTHING,
    auto_deployment_is_enabled: T.Optional[bool] = NOTHING,
    auto_deployment_retain_stacks_on_account_removal: T.Optional[bool] = NOTHING,
    call_as_self: T.Optional[bool] = NOTHING,
    call_as_delegated_admin: T.Optional[bool] = NOTHING,
    client_request_token: T.Optional[str] = NOTHING,
) -> str:
    """
    Ref:

    - create_stack_set: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/create_stack_set.html

    :return: stack_set_id
    """
    kwargs = dict(
        StackSetName=stack_set_name,
        Description=description,
        TemplateBody=template_body,
        TemplateURL=template_url,
        StackId=stack_id,
        AdministrationRoleARN=admin_role_arn,
        ExecutionRoleName=execution_role_name,
        ClientRequestToken=client_request_token,
    )

    resolve_create_update_stack_set_common_kwargs(
        kwargs,
        parameters=parameters,
        tags=tags,
        include_iam=include_iam,
        include_named_iam=include_named_iam,
        include_macro=include_macro,
        permission_model_is_self_managed=permission_model_is_self_managed,
        permission_model_is_service_managed=permission_model_is_service_managed,
        auto_deployment_is_enabled=auto_deployment_is_enabled,
        auto_deployment_retain_stacks_on_account_removal=auto_deployment_retain_stacks_on_account_removal,
        call_as_self=call_as_self,
        call_as_delegated_admin=call_as_delegated_admin,
    )
    res = bsm.cloudformation_client.create_stack_set(**resolve_kwargs(**kwargs))
    return res["StackSetId"]


def update_stack_set(
    bsm: BotoSesManager,
    stack_set_name: str,
    description: T.Optional[str] = NOTHING,
    template_body: T.Optional[str] = NOTHING,
    template_url: T.Optional[str] = NOTHING,
    use_previous_template: T.Optional[bool] = NOTHING,
    parameters: T.Optional[T.List[Parameter]] = NOTHING,
    tags: T.Optional[T.Dict[str, str]] = NOTHING,
    include_iam: T.Optional[bool] = NOTHING,
    include_named_iam: T.Optional[bool] = NOTHING,
    include_macro: T.Optional[bool] = NOTHING,
    operation_preferences: T.Optional[dict] = NOTHING,
    admin_role_arn: T.Optional[str] = NOTHING,
    execution_role_name: T.Optional[str] = NOTHING,
    deployment_target: T.Optional[dict] = NOTHING,
    permission_model_is_self_managed: T.Optional[bool] = NOTHING,
    permission_model_is_service_managed: T.Optional[bool] = NOTHING,
    auto_deployment_is_enabled: T.Optional[bool] = NOTHING,
    auto_deployment_retain_stacks_on_account_removal: T.Optional[bool] = NOTHING,
    operation_id: T.Optional[str] = NOTHING,
    accounts: T.Optional[T.List[str]] = NOTHING,
    regions: T.Optional[T.List[str]] = NOTHING,
    call_as_self: T.Optional[bool] = NOTHING,
    call_as_delegated_admin: T.Optional[bool] = NOTHING,
    managed_execution_active: T.Optional[bool] = NOTHING,
) -> str:
    """
    Ref:

    - update_stack_set: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/update_stack_set.html

    :return: operation_id
    """
    kwargs = dict(
        StackSetName=stack_set_name,
        Description=description,
        TemplateBody=template_body,
        TemplateURL=template_url,
        UsePreviousTemplate=use_previous_template,
        OperationPreferences=operation_preferences,
        AdministrationRoleARN=admin_role_arn,
        ExecutionRoleName=execution_role_name,
        DeploymentTargets=deployment_target,
        OperationId=operation_id,
        Accounts=accounts,
        Regions=regions,
    )
    resolve_create_update_stack_set_common_kwargs(
        kwargs,
        parameters=parameters,
        tags=tags,
        include_iam=include_iam,
        include_named_iam=include_named_iam,
        include_macro=include_macro,
        permission_model_is_self_managed=permission_model_is_self_managed,
        permission_model_is_service_managed=permission_model_is_service_managed,
        auto_deployment_is_enabled=auto_deployment_is_enabled,
        auto_deployment_retain_stacks_on_account_removal=auto_deployment_retain_stacks_on_account_removal,
        call_as_self=call_as_self,
        call_as_delegated_admin=call_as_delegated_admin,
        managed_execution_active=managed_execution_active,
    )
    res = bsm.cloudformation_client.update_stack_set(**resolve_kwargs(**kwargs))
    return res["OperationId"]


def delete_stack_set(
    bsm: BotoSesManager,
    stack_set_name: str,
    call_as_self: T.Optional[bool] = NOTHING,
    call_as_delegated_admin: T.Optional[bool] = NOTHING,
):
    """
    Ref:

    - delete_stack_set: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/delete_stack_set.html
    """
    kwargs = dict(
        StackSetName=stack_set_name,
    )
    resolve_callas_kwargs(
        kwargs,
        call_as_self=call_as_self,
        call_as_delegated_admin=call_as_delegated_admin,
    )
    res = bsm.cloudformation_client.delete_stack_set(**resolve_kwargs(**kwargs))


def describe_stack_instance(
    bsm: BotoSesManager,
    stack_set_name: str,
    stack_instance_account: str,
    stack_instance_region: str,
    call_as_self: T.Optional[bool] = NOTHING,
    call_as_delegated_admin: T.Optional[bool] = NOTHING,
) -> T.Optional[StackInstance]:
    """
    Ref:

    - describe_stack_instance: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/describe_stack_instance.html
    """
    kwargs = dict(
        StackSetName=stack_set_name,
        StackInstanceAccount=stack_instance_account,
        StackInstanceRegion=stack_instance_region,
    )
    resolve_callas_kwargs(
        kwargs,
        call_as_self=call_as_self,
        call_as_delegated_admin=call_as_delegated_admin,
    )
    try:
        res = bsm.cloudformation_client.describe_stack_instance(**kwargs)
        return StackInstance.from_describe_stack_instance_response(res["StackInstance"])
    except Exception as e:
        if "StackInstanceNotFoundException" in str(e):  # pragma: no cover
            return None
        # moto3 version of not StackInstanceNotFoundException
        elif "'NoneType' object has no attribute 'to_dict'" in str(e):
            return None
        else:  # pragma: no cover
            raise e


def create_stack_instances(
    bsm: BotoSesManager,
    stack_set_name: str,
    regions: T.List[str],
    accounts: T.Optional[T.List[str]] = NOTHING,
    deployment_targets: T.Optional[dict] = NOTHING,
    param_overrides: T.Optional[T.List[Parameter]] = NOTHING,
    operation_preference: T.Optional[dict] = NOTHING,
    operation_id: T.Optional[str] = NOTHING,
    call_as_self: T.Optional[bool] = NOTHING,
    call_as_delegated_admin: T.Optional[bool] = NOTHING,
) -> str:
    """
    Ref:

    - create_stack_instances: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/create_stack_instances.html

    :return: operation_id
    """
    kwargs = dict(
        StackSetName=stack_set_name,
        Regions=regions,
        Accounts=accounts,
        DeploymentTargets=deployment_targets,
        OperationPreferences=operation_preference,
        OperationId=operation_id,
    )
    resolve_create_update_stack_instances_common_kwargs(
        kwargs,
        parameter_overrides=param_overrides,
        call_as_self=call_as_self,
        call_as_delegated_admin=call_as_delegated_admin,
    )
    res = bsm.cloudformation_client.create_stack_instances(**resolve_kwargs(**kwargs))
    return res["OperationId"]


def update_stack_instances(
    bsm: BotoSesManager,
    stack_set_name: str,
    regions: T.List[str],
    accounts: T.Optional[T.List[str]] = NOTHING,
    deployment_targets: T.Optional[dict] = NOTHING,
    param_overrides: T.Optional[T.List[Parameter]] = NOTHING,
    operation_preference: T.Optional[dict] = NOTHING,
    operation_id: T.Optional[str] = NOTHING,
    call_as_self: T.Optional[bool] = NOTHING,
    call_as_delegated_admin: T.Optional[bool] = NOTHING,
):
    """
    Ref:

    - update_stack_instances: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/update_stack_instances.html
    """
    kwargs = dict(
        StackSetName=stack_set_name,
        Regions=regions,
        Accounts=accounts,
        DeploymentTargets=deployment_targets,
        OperationPreferences=operation_preference,
        OperationId=operation_id,
    )
    resolve_create_update_stack_instances_common_kwargs(
        kwargs,
        parameter_overrides=param_overrides,
        call_as_self=call_as_self,
        call_as_delegated_admin=call_as_delegated_admin,
    )
    res = bsm.cloudformation_client.update_stack_instances(**resolve_kwargs(**kwargs))
    return res["OperationId"]


def delete_stack_instances(
    bsm: BotoSesManager,
    stack_set_name: str,
    regions: T.List[str],
    retain_stacks: bool,
    accounts: T.Optional[T.List[str]] = NOTHING,
    deployment_targets: T.Optional[dict] = NOTHING,
    operation_preference: T.Optional[dict] = NOTHING,
    operation_id: T.Optional[str] = NOTHING,
    call_as_self: T.Optional[bool] = NOTHING,
    call_as_delegated_admin: T.Optional[bool] = NOTHING,
) -> str:
    """
    Ref:

    - delete_stack_instances: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/delete_stack_instances.html

    :return: operation_id
    """
    kwargs = dict(
        StackSetName=stack_set_name,
        Regions=regions,
        Accounts=accounts,
        DeploymentTargets=deployment_targets,
        OperationPreferences=operation_preference,
        RetainStacks=retain_stacks,
        OperationId=operation_id,
    )
    resolve_callas_kwargs(
        kwargs,
        call_as_self=call_as_self,
        call_as_delegated_admin=call_as_delegated_admin,
    )
    res = bsm.cloudformation_client.delete_stack_instances(**resolve_kwargs(**kwargs))
    return res["OperationId"]


def _list_stack_instances(
    bsm: BotoSesManager,
    stack_set_name: str,
    filters: T.Optional[T.List[dict]] = NOTHING,
    stack_instance_account: T.Optional[str] = NOTHING,
    stack_instance_region: T.Optional[str] = NOTHING,
    call_as_self: T.Optional[bool] = NOTHING,
    call_as_delegated_admin: T.Optional[bool] = NOTHING,
    page_size: int = 20,
    max_results: int = 1000,
) -> T.Iterable[StackInstance]:
    paginator = bsm.cloudformation_client.get_paginator("list_stack_instances")
    kwargs = dict(
        StackSetName=stack_set_name,
        Filters=filters,
        StackInstanceAccount=stack_instance_account,
        StackInstanceRegion=stack_instance_region,
        PaginationConfig=dict(
            PageSize=page_size,
            MaxItems=max_results,
        ),
    )
    resolve_callas_kwargs(
        kwargs,
        call_as_self=call_as_self,
        call_as_delegated_admin=call_as_delegated_admin,
    )
    for response in paginator.paginate(**resolve_kwargs(**kwargs)):
        for data in response.get("Summaries", []):
            yield StackInstance.from_describe_stack_instance_response(data)


class StackInstanceIterProxy(IterProxy[StackInstance]):
    """
    Reference:

    - https://github.com/MacHu-GWU/iterproxy-project
    """


def list_stack_instances(
    bsm: BotoSesManager,
    stack_set_name: str,
    filters: T.Optional[T.List[dict]] = NOTHING,
    stack_instance_account: T.Optional[str] = NOTHING,
    stack_instance_region: T.Optional[str] = NOTHING,
    call_as_self: T.Optional[bool] = NOTHING,
    call_as_delegated_admin: T.Optional[bool] = NOTHING,
    page_size: int = 20,
    max_results: int = 1000,
) -> StackInstanceIterProxy:
    """
    Ref:

    - list_stack_instances: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/list_stack_instances.html

    :return: :class:`StackInstanceIterProxy`
    """
    return StackInstanceIterProxy(
        _list_stack_instances(
            bsm=bsm,
            stack_set_name=stack_set_name,
            filters=filters,
            stack_instance_account=stack_instance_account,
            stack_instance_region=stack_instance_region,
            call_as_self=call_as_self,
            call_as_delegated_admin=call_as_delegated_admin,
            page_size=page_size,
            max_results=max_results,
        )
    )


def wait_deploy_stack_instances_to_stop(
    bsm: BotoSesManager,
    stack_set_name: str,
    raise_errror_until_exec_stopped: bool,
    delays: T.Union[int, float],
    timeout: T.Union[int, float],
    verbose: bool,
    call_as_self: T.Optional[bool] = NOTHING,
    call_as_delegated_admin: T.Optional[bool] = NOTHING,
) -> T.List[StackInstance]:
    """
    This function can be called after you did a ``create_stack_instances``,
    ``update_stack_instances``, ``delete_stack_instances`` or ``update_stack_set``.
    It waits until all changes to stack instances finished. If the deployment
    failed, then it will error.

    TODO: add test and doc

    :param bsm:
    :param stack_set_name:
    :param raise_errror_until_exec_stopped:
    :param delays:
    :param timeout:
    :param verbose:
    :param call_as_self:
    :param call_as_delegated_admin:
    :return:
    """
    aws_console = AWSConsole(aws_region=bsm.aws_region, bsm=bsm)

    for _ in Waiter(
        delays=delays,
        timeout=timeout,
        indent=4,
        verbose=verbose,
    ):
        stack_instances = list_stack_instances(
            bsm=bsm,
            stack_set_name=stack_set_name,
            call_as_self=call_as_self,
            call_as_delegated_admin=call_as_delegated_admin,
        ).all()

        is_stopped = False
        error: T.Optional[exc.DeployStackInstanceFailedError] = None
        for stack_instance in stack_instances:
            if stack_instance.is_logical_failed():
                console_url = get_stack_set_instances_console_url(
                    aws_console=aws_console,
                    name_or_id_or_arn=stack_instance.stack_set_id,
                    call_as_self=call_as_self,
                    call_as_delegated_admin=call_as_delegated_admin,
                )
                if error is None:
                    error = exc.DeployStackInstanceFailedError(
                        f"stack instance on {stack_instance.aws_account_id} {stack_instance.aws_region} "
                        f"is failed. reason: {stack_instance.status_reason}, "
                        f"and it may have more stack instances also failed, "
                        f"please check in the console: {console_url}."
                    )
                if raise_errror_until_exec_stopped is True:
                    raise error

            if stack_instance.is_logical_stopped():
                is_stopped = True
                break

        if error is not None:
            raise error

        if is_stopped:
            return stack_instances
