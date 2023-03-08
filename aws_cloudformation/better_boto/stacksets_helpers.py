# -*- coding: utf-8 -*-

import typing as T

from func_args import NOTHING

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
    StackInstanceDriftStatusEnum,
    StackInstance,
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


def parse_describe_stack_set_response(data: dict) -> StackSet:
    """
    Create a :class:`~aws_cottonformation.stack_set.StackSet` object from the
    ``describe_stack_set()`` or ``list_stack_sets()`` API response.

    Ref:

    - describe_stack_set: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/describe_stack_set.html
    - list_stack_sets: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/list_stack_sets.html
    :param data:
    :return:
    """
    return StackSet(
        id=data["StackSetId"],
        name=data["StackSetName"],
        arn=data["StackSetARN"],
        description=data.get("Description"),
        status=StackSetStatusEnum.get_by_name(data.get("Status")),
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


def parse_describe_stack_instance_response(data: dict) -> StackInstance:
    """
    Create a :class:`~aws_cottonformation.stack_set.StackInstance` object from the
    ``describe_stack_instance()`` or ``list_stack_instances()`` API response.

    Ref:

    - describe_stack_instance: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/describe_stack_instance.html
    - list_stack_instances: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/list_stack_instances.html
    :param data:
    :return:
    """
    return StackInstance(
        stack_set_id=data["StackSetId"],
        stack_id=data["StackId"],
        aws_region=data["Region"],
        aws_account_id=data["Account"],
        param_overrides={
            dct["ParameterKey"]: Parameter(
                key=dct["ParameterKey"],
                value=dct["ParameterValue"],
                use_previous_value=dct.get("UsePreviousValue"),
                resolved_value=dct.get("ResolvedValue"),
            )
            for dct in data.get("ParameterOverrides", [])
        },
        status=StackInstanceStatusEnum.get_by_name(data.get("Status")),
        statck_instance_status=data.get("StackInstanceStatus", {}),
        status_reason=data.get("StatusReason"),
        org_unit_id=data.get("OrganizationalUnitId"),
        drift_status=StackInstanceDriftStatusEnum.get_by_name(data.get("DriftStatus")),
        last_drift_check_timestamp=data.get("LastDriftCheckTimestamp"),
        last_operation_id=data.get("LastOperationId"),
    )
