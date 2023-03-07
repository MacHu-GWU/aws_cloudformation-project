# -*- coding: utf-8 -*-

"""
AWS CloudFormation StackSet related operations.
"""

import typing as T

from boto_session_manager import BotoSesManager, AwsServiceEnum
from func_args import NOTHING, resolve_kwargs

from .stacks import (
    _resolve_capabilities_kwargs,
    Parameter,
)
from ..stack_set import (
    StackSetStatusEnum,
    StackSetPermissionModelEnum,
    StackSetCallAsEnum,
    StackSet,
    StackInstanceStatusEnum,
    DetailedStackInstanceStatusEnum,
    StackInstanceDriftStatusEnum,
    StackInstance,
)


def from_describe_stack_set(data: dict) -> StackSet:
    """
    Create a :class:`~aws_cottonformation.stack_set.StackSet` object from the
    ``describe_stack_set`` API response.

    :param data:
    :return:
    """
    return StackSet(
        id=data["StackSetId"],
        name=data["StackSetName"],
        arn=data["StackSetARN"],
        description=data.get("Description"),
        status=data.get("Status"),
        template_body=data.get("TemplateBody"),
        params={
            dct["ParameterKey"]: Parameter(
                key=dct["ParameterKey"],
                value=dct["ParameterValue"],
                use_previous_value=dct.get("UsePreviousValue"),
                resolved_value=dct.get("ResolvedValue"),
            )
            for dct in data.get("Parameters", [])
        },
        admin_role_arn=data.get("AdministrationRoleARN"),
        execution_role_name=data.get("ExecutionRoleName"),
        permission_model=StackSetPermissionModelEnum.get_by_name(
            data.get("PermissionModel")
        ),
        org_unit_ids=data.get("OrganizationalUnitIds", []),
        auto_deployment=data.get("AutoDeployment", {}),
        managed_execution=data.get("ManagedExecution"),
        regions=data.get("Regions", []),
    )


def _resolve_callas_kwargs(
    kwargs: dict,
    call_as_self: bool,
    call_as_delegated_admin: bool,
):
    if call_as_self:
        kwargs["CallAs"] = StackSetCallAsEnum.SELF.value
    elif call_as_delegated_admin:
        kwargs["CallAs"] = StackSetCallAsEnum.DELEGATED_ADMIN.value
    else:
        kwargs["CallAs"] = StackSetCallAsEnum.SELF.value


def describe_stack_set(
    bsm: BotoSesManager,
    name: str,
    call_as_self: bool = False,
    call_as_delegated_admin: bool = False,
) -> T.Optional[StackSet]:
    """
    Ref:

    - describe_stack_set: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/describe_stack_set.html#describe_stack_set

    :param bsm:
    :param name:
    :param call_as_self:
    :param call_as_delegated_admin:
    :return:
    """
    kwargs = dict(StackSetName=name)
    _resolve_callas_kwargs(
        kwargs,
        call_as_self=call_as_self,
        call_as_delegated_admin=call_as_delegated_admin,
    )
    try:
        res = bsm.cloudformation_client.describe_stack_set(**kwargs)
        return from_describe_stack_set(res["StackSet"])
    except Exception as e:
        if "StackSetNotFoundException" in str(e):
            return None
        else:  # pragma: no cover
            raise e


def _resolve_parameters(
    kwargs: dict,
    parameters: T.Optional[T.List[Parameter]] = NOTHING,
):
    if parameters is not NOTHING:
        kwargs["Parameters"] = [param.to_kwargs() for param in parameters]


def _resolve_tags(
    kwargs: dict,
    tags: T.Optional[T.Dict[str, str]] = NOTHING,
):
    if tags is not NOTHING:
        kwargs["Tags"] = [dict(Key=key, Value=value) for key, value in tags.items()]


def _resolve_permission_model(
    kwargs: dict,
    permission_model_is_self_managed: bool,
    permission_model_is_service_managed: bool,
):
    if permission_model_is_self_managed:
        kwargs["PermissionModel"] = StackSetPermissionModelEnum.SELF_MANAGED.value
    elif permission_model_is_service_managed:
        kwargs["PermissionModel"] = StackSetPermissionModelEnum.SERVICE_MANAGED.value
    else:
        kwargs["PermissionModel"] = StackSetPermissionModelEnum.SELF_MANAGED.value


def _resolve_auto_deployment(
    kwargs: dict,
    auto_deployment_is_enabled: T.Optional[bool] = NOTHING,
    auto_deployment_retain_stacks_on_account_removal: T.Optional[bool] = NOTHING,
):
    auto_deployment = {}
    if auto_deployment_is_enabled is not NOTHING:
        auto_deployment["Enabled"] = auto_deployment_is_enabled
    if auto_deployment_retain_stacks_on_account_removal is not NOTHING:
        auto_deployment[
            "RetainStacksOnAccountRemoval"
        ] = auto_deployment_retain_stacks_on_account_removal
    if len(auto_deployment) > 0:
        kwargs["AutoDeployment"] = auto_deployment


def _resolve_managed_execution(
    kwargs: dict,
    managed_execution_active: T.Optional[bool] = NOTHING,
):
    if managed_execution_active is not NOTHING:
        kwargs["ManagedExecution"] = dict(Active=managed_execution_active)


def _resolve_create_update_stack_set_common_kwargs(
    kwargs: dict,
    parameters: T.List[Parameter] = NOTHING,
    tags: T.Dict[str, str] = NOTHING,
    include_iam: bool = False,
    include_named_iam: bool = False,
    include_macro: bool = False,
    permission_model_is_self_managed: bool = False,
    permission_model_is_service_managed: bool = False,
    auto_deployment_is_enabled: T.Optional[bool] = NOTHING,
    auto_deployment_retain_stacks_on_account_removal: T.Optional[bool] = NOTHING,
    call_as_self: bool = False,
    call_as_delegated_admin: bool = False,
    managed_execution_active: T.Optional[bool] = NOTHING,
):
    _resolve_parameters(
        kwargs,
        parameters=parameters,
    )
    _resolve_tags(
        kwargs,
        tags=tags,
    )
    _resolve_capabilities_kwargs(
        kwargs,
        include_iam=include_iam,
        include_named_iam=include_named_iam,
        include_macro=include_macro,
    )
    _resolve_permission_model(
        kwargs,
        permission_model_is_self_managed=permission_model_is_self_managed,
        permission_model_is_service_managed=permission_model_is_service_managed,
    )
    _resolve_callas_kwargs(
        kwargs,
        call_as_self=call_as_self,
        call_as_delegated_admin=call_as_delegated_admin,
    )
    _resolve_auto_deployment(
        kwargs,
        auto_deployment_is_enabled=auto_deployment_is_enabled,
        auto_deployment_retain_stacks_on_account_removal=auto_deployment_retain_stacks_on_account_removal,
    )
    _resolve_managed_execution(
        kwargs,
        managed_execution_active=managed_execution_active,
    )


def create_stack_set(
    bsm: BotoSesManager,
    stack_set_name: str,
    description: T.Optional[str] = NOTHING,
    template_body: T.Optional[str] = NOTHING,
    template_url: T.Optional[str] = NOTHING,
    stack_id: T.Optional[str] = NOTHING,
    parameters: T.List[Parameter] = NOTHING,
    tags: T.Dict[str, str] = NOTHING,
    include_iam: bool = False,
    include_named_iam: bool = False,
    include_macro: bool = False,
    admin_role_arn: T.Optional[str] = NOTHING,
    execution_role_name: T.Optional[str] = NOTHING,
    permission_model_is_self_managed: bool = False,
    permission_model_is_service_managed: bool = False,
    auto_deployment_is_enabled: T.Optional[bool] = NOTHING,
    auto_deployment_retain_stacks_on_account_removal: T.Optional[bool] = NOTHING,
    call_as_self: bool = False,
    call_as_delegated_admin: bool = False,
    client_request_token: T.Optional[str] = NOTHING,
    managed_execution_active: T.Optional[bool] = NOTHING,
    verbose: bool = True,
):
    """
    Ref:

    - create_stack_set: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/create_stack_set.html

    :param bsm:
    :param stack_set_name:
    :param description:
    :param template_body:
    :param template_url:
    :param stack_id:
    :param parameters:
    :param tags:
    :param include_iam:
    :param include_named_iam:
    :param include_macro:
    :param admin_role_arn:
    :param execution_role_name:
    :param permission_model_is_self_managed:
    :param permission_model_is_service_managed:
    :param auto_deployment_is_enabled:
    :param auto_deployment_retain_stacks_on_account_removal:
    :param call_as_self:
    :param call_as_delegated_admin:
    :param client_request_token:
    :param managed_execution_active:
    :param verbose:
    :return:
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

    _resolve_create_update_stack_set_common_kwargs(
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
    res = bsm.cloudformation_client.create_stack_set(**resolve_kwargs(**kwargs))


def update_stack_set(
    bsm: BotoSesManager,
    stack_set_name: str,
    description: T.Optional[str] = NOTHING,
    template_body: T.Optional[str] = NOTHING,
    template_url: T.Optional[str] = NOTHING,
    use_previous_template: T.Optional[bool] = NOTHING,
    parameters: T.List[Parameter] = NOTHING,
    tags: T.Dict[str, str] = NOTHING,
    include_iam: bool = False,
    include_named_iam: bool = False,
    include_macro: bool = False,
    operation_preferences: T.Optional[dict] = NOTHING,
    admin_role_arn: T.Optional[str] = NOTHING,
    execution_role_name: T.Optional[str] = NOTHING,
    deployment_target: T.Optional[dict] = NOTHING,
    permission_model_is_self_managed: bool = False,
    permission_model_is_service_managed: bool = False,
    auto_deployment_is_enabled: T.Optional[bool] = NOTHING,
    auto_deployment_retain_stacks_on_account_removal: T.Optional[bool] = NOTHING,
    operation_id: T.Optional[str] = NOTHING,
    accounts: T.Optional[T.List[str]] = NOTHING,
    regions: T.Optional[T.List[str]] = NOTHING,
    call_as_self: bool = False,
    call_as_delegated_admin: bool = False,
    managed_execution_active: T.Optional[bool] = NOTHING,
    verbose: bool = True,
):
    """
    Ref:

    - update_stack_set: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/update_stack_set.html

    :param bsm:
    :param stack_set_name:
    :param description:
    :param template_body:
    :param template_url:
    :param use_previous_template:
    :param parameters:
    :param tags:
    :param include_iam:
    :param include_named_iam:
    :param include_macro:
    :param operation_preferences:
    :param admin_role_arn:
    :param execution_role_name:
    :param deployment_target:
    :param permission_model_is_self_managed:
    :param permission_model_is_service_managed:
    :param auto_deployment_is_enabled:
    :param auto_deployment_retain_stacks_on_account_removal:
    :param operation_id:
    :param accounts:
    :param regions:
    :param call_as_self:
    :param call_as_delegated_admin:
    :param client_request_token:
    :param managed_execution_active:
    :param verbose:
    :return:
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
    _resolve_create_update_stack_set_common_kwargs(
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
