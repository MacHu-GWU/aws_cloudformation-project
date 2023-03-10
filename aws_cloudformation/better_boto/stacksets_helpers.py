# -*- coding: utf-8 -*-

import typing as T

from func_args import NOTHING

from ..stack import Parameter
from ..stack_set import (
    StackSetPermissionModelEnum,
    StackSetCallAsEnum,
)

from .stacks_helpers import (
    resolve_capabilities_kwargs,
    resolve_parameters,
    resolve_tags,
)


def resolve_callas_kwargs(
    kwargs: dict,
    call_as_self: T.Optional[bool] = NOTHING,
    call_as_delegated_admin: T.Optional[bool] = NOTHING,
):
    if call_as_self:
        kwargs["CallAs"] = StackSetCallAsEnum.SELF.value
    elif call_as_delegated_admin:
        kwargs["CallAs"] = StackSetCallAsEnum.DELEGATED_ADMIN.value
    else:
        kwargs["CallAs"] = StackSetCallAsEnum.SELF.value


def resolve_parameters_overrides(
    kwargs: dict,
    parameter_overrides: T.Optional[T.List[Parameter]] = NOTHING,
):
    if parameter_overrides is not NOTHING:
        kwargs["ParameterOverrides"] = [
            param.to_kwargs() for param in parameter_overrides
        ]


def resolve_permission_model(
    kwargs: dict,
    permission_model_is_self_managed: T.Optional[bool] = NOTHING,
    permission_model_is_service_managed: T.Optional[bool] = NOTHING,
):
    if permission_model_is_self_managed:
        kwargs["PermissionModel"] = StackSetPermissionModelEnum.SELF_MANAGED.value
    elif permission_model_is_service_managed:
        kwargs["PermissionModel"] = StackSetPermissionModelEnum.SERVICE_MANAGED.value
    else:
        kwargs["PermissionModel"] = StackSetPermissionModelEnum.SELF_MANAGED.value


def resolve_auto_deployment(
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


def resolve_managed_execution(
    kwargs: dict,
    managed_execution_active: T.Optional[bool] = NOTHING,
):
    if managed_execution_active is not NOTHING:
        kwargs["ManagedExecution"] = dict(Active=managed_execution_active)


def resolve_create_update_stack_set_common_kwargs(
    kwargs: dict,
    parameters: T.List[Parameter] = NOTHING,
    tags: T.Dict[str, str] = NOTHING,
    include_iam: T.Optional[bool] = NOTHING,
    include_named_iam: T.Optional[bool] = NOTHING,
    include_macro: T.Optional[bool] = NOTHING,
    permission_model_is_self_managed: T.Optional[bool] = NOTHING,
    permission_model_is_service_managed: T.Optional[bool] = NOTHING,
    auto_deployment_is_enabled: T.Optional[bool] = NOTHING,
    auto_deployment_retain_stacks_on_account_removal: T.Optional[bool] = NOTHING,
    call_as_self: T.Optional[bool] = NOTHING,
    call_as_delegated_admin: T.Optional[bool] = NOTHING,
    managed_execution_active: T.Optional[bool] = NOTHING,
):
    resolve_parameters(
        kwargs,
        parameters=parameters,
    )
    resolve_tags(
        kwargs,
        tags=tags,
    )
    resolve_capabilities_kwargs(
        kwargs,
        include_iam=include_iam,
        include_named_iam=include_named_iam,
        include_macro=include_macro,
    )
    resolve_permission_model(
        kwargs,
        permission_model_is_self_managed=permission_model_is_self_managed,
        permission_model_is_service_managed=permission_model_is_service_managed,
    )
    resolve_callas_kwargs(
        kwargs,
        call_as_self=call_as_self,
        call_as_delegated_admin=call_as_delegated_admin,
    )
    resolve_auto_deployment(
        kwargs,
        auto_deployment_is_enabled=auto_deployment_is_enabled,
        auto_deployment_retain_stacks_on_account_removal=auto_deployment_retain_stacks_on_account_removal,
    )
    resolve_managed_execution(
        kwargs,
        managed_execution_active=managed_execution_active,
    )


def resolve_create_update_stack_instances_common_kwargs(
    kwargs: dict,
    parameter_overrides: T.Optional[T.List[Parameter]] = NOTHING,
    call_as_self: T.Optional[bool] = NOTHING,
    call_as_delegated_admin: T.Optional[bool] = NOTHING,
):
    resolve_parameters_overrides(
        kwargs,
        parameter_overrides=parameter_overrides,
    )
    resolve_callas_kwargs(
        kwargs,
        call_as_self=call_as_self,
        call_as_delegated_admin=call_as_delegated_admin,
    )