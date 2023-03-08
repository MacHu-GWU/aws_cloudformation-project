# -*- coding: utf-8 -*-

import typing as T
import sys
from datetime import datetime

from boto_session_manager import BotoSesManager, AwsServiceEnum
from func_args import NOTHING
from colorama import Fore, Style

from .. import exc
from .. import helper
from ..console import get_s3_console_url
from ..waiter import Waiter
from ..stack import (
    StackStatusEnum,
    Parameter,
    Output,
    Stack,
    DriftStatusEnum,
    ChangeSetStatusEnum,
    ChangeSetExecutionStatusEnum,
    ChangeSetTypeEnum,
    ChangeSet,
)

from .taggings_helper import to_tag_dict

# def resolve_template_in_kwargs(
#     kwargs: dict,
#     bsm: BotoSesManager,
#     template: T.Optional[str],
#     bucket: T.Optional[str] = None,
#     prefix: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_TEMPLATE,
#     verbose: bool = True,
# ):
#     if template.startswith("s3://"):
#         kwargs["TemplateURL"] = template
#
#     if bucket is not None:
#         template_url = upload_template_to_s3(
#             bsm,
#             template,
#             bucket=bucket,
#             prefix=prefix,
#             verbose=verbose,
#         )
#         kwargs["TemplateURL"] = template_url
#     elif sys.getsizeof(template) > TEMPLATE_BODY_SIZE_LIMIT:
#         raise ValueError(
#             f"Template size is larger than {TEMPLATE_BODY_SIZE_LIMIT}B, "
#             "You have to upload to s3 bucket first!"
#         )
#     else:
#         kwargs["TemplateBody"] = template


# def resolve_stack_policy(
#     kwargs: dict,
#     bsm: BotoSesManager,
#     stack_policy: str,
#     bucket: str,
#     prefix: T.Optional[str] = None,
#     verbose: bool = True,
# ):
#     if bucket is not None:
#         policy_url = upload_template_to_s3(
#             bsm,
#             stack_policy,
#             bucket=bucket,
#             prefix=prefix,
#             verbose=verbose,
#         )
#         kwargs["StackPolicyURL"] = policy_url
#     elif sys.getsizeof(stack_policy) > STACK_POLICY_SIZE_LIMIT:
#         raise ValueError(
#             f"Stack policy size is larger than {STACK_POLICY_SIZE_LIMIT}B, "
#             "You have to upload to s3 bucket first!"
#         )
#     else:
#         kwargs["StackPolicyBody"] = stack_policy


def resolve_capabilities_kwargs(
    kwargs: dict,
    include_iam: bool = False,
    include_named_iam: bool = False,
    include_macro: bool = False,
):
    capabilities = list()
    if include_iam:
        capabilities.append("CAPABILITY_IAM")
    if include_named_iam:
        capabilities.append("CAPABILITY_NAMED_IAM")
    if include_macro:
        capabilities.append("CAPABILITY_AUTO_EXPAND")
    if capabilities:
        kwargs["Capabilities"] = capabilities


def resolve_parameters(
    kwargs: dict,
    parameters: T.Optional[T.List[Parameter]] = NOTHING,
):
    if parameters is not NOTHING:
        kwargs["Parameters"] = [param.to_kwargs() for param in parameters]


def resolve_tags(
    kwargs: dict,
    tags: T.Optional[T.Dict[str, str]] = NOTHING,
):
    if tags is not NOTHING:
        kwargs["Tags"] = [dict(Key=key, Value=value) for key, value in tags.items()]


def resolve_on_failure(
    kwargs: dict,
    on_failure_do_nothing: T.Optional[bool] = False,
    on_failure_rollback: T.Optional[bool] = False,
    on_failure_delete: T.Optional[bool] = False,
):
    if (
        sum(
            [
                on_failure_do_nothing,
                on_failure_rollback,
                on_failure_delete,
            ]
        )
        > 1
    ):  # pragma: no cover
        raise ValueError(
            "You can only set one of "
            "on_failure_do_nothing, on_failure_rollback, on_failure_delete to True!"
        )
    if on_failure_do_nothing:
        kwargs["OnFailure"] = "DO_NOTHING"
    elif on_failure_rollback:
        kwargs["OnFailure"] = "ROLLBACK"
    elif on_failure_delete:
        kwargs["OnFailure"] = "DELETE"
    else:  # pragma: no cover
        raise NotImplementedError


def resolve_create_update_stack_common_kwargs(
    kwargs: dict,
    parameters: T.List[Parameter] = None,
    tags: dict = None,
    include_iam: bool = False,
    include_named_iam: bool = False,
    include_macro: bool = False,
):
    resolve_capabilities_kwargs(
        kwargs,
        include_iam=include_iam,
        include_named_iam=include_named_iam,
        include_macro=include_macro,
    )
    resolve_parameters(
        kwargs,
        parameters=parameters,
    )
    resolve_tags(
        kwargs,
        tags=tags,
    )


def resolve_change_set_type(
    kwargs: dict,
    change_set_type_is_create: T.Optional[bool] = False,
    change_set_type_is_update: T.Optional[bool] = False,
    change_set_type_is_import: T.Optional[bool] = False,
):
    true_flag_count = sum([
        change_set_type_is_create,
        change_set_type_is_update,
        change_set_type_is_import,
    ])
    if true_flag_count == 0: # pragma: no cover
        return
    elif true_flag_count == 1:
        if change_set_type_is_create:
            kwargs["ChangeSetType"] = ChangeSetTypeEnum.CREATE.value
        elif change_set_type_is_update:
            kwargs["ChangeSetType"] = ChangeSetTypeEnum.UPDATE.value
        elif change_set_type_is_import:
            kwargs["ChangeSetType"] = ChangeSetTypeEnum.IMPORT.value
        else:  # pragma: no cover
            raise NotImplementedError


def parse_describe_stacks_response(data: dict) -> Stack:
    """
    Create a :class:`~aws_cottonformation.stack.Stack` object from the
    ``describe_stacks`` API response.
    """
    drift_status = data.get("DriftInformation", dict()).get("StackDriftStatus")
    if drift_status is not None:
        drift_status = DriftStatusEnum.get_by_name(drift_status)
    return Stack(
        id=data["StackId"],
        name=data["StackName"],
        change_set_id=data.get("ChangeSetId"),
        status=StackStatusEnum.get_by_name(data["StackStatus"]),
        description=data.get("Description"),
        role_arn=data.get("RoleARN"),
        creation_time=data.get("CreationTime"),
        last_updated_time=data.get("LastUpdatedTime"),
        deletion_time=data.get("DeletionTime"),
        outputs={
            dct["OutputKey"]: Output(
                key=dct["OutputKey"],
                value=dct["OutputValue"],
                description=dct.get("Description"),
                export_name=dct.get("ExportName"),
            )
            for dct in data.get("Outputs", [])
        },
        params={
            dct["ParameterKey"]: Parameter(
                key=dct["ParameterKey"],
                value=dct["ParameterValue"],
                use_previous_value=dct.get("UsePreviousValue"),
                resolved_value=dct.get("ResolvedValue"),
            )
            for dct in data.get("Parameters", [])
        },
        tags={dct["Key"]: dct["Value"] for dct in data.get("Tags", [])},
        enable_termination_protection=data.get("EnableTerminationProtection"),
        parent_id=data.get("ParentId"),
        root_id=data.get("RootId"),
        drift_status=drift_status,
        drift_last_check_time=data.get("DriftInformation", dict()).get(
            "LastCheckTimestamp"
        ),
    )


def parse_describe_change_set_response(data: dict) -> ChangeSet:
    """
    Create a :class:`~aws_cottonformation.stack.ChangeSet` object from the
    ``describe_change_set`` API response.
    """
    return ChangeSet(
        change_set_id=data["ChangeSetId"],
        change_set_name=data["ChangeSetName"],
        stack_id=data["StackId"],
        stack_name=data["StackName"],
        description=data.get("Description"),
        params={
            dct["ParameterKey"]: Parameter(
                key=dct["ParameterKey"],
                value=dct["ParameterValue"],
                use_previous_value=dct.get("UsePreviousValue"),
                resolved_value=dct.get("ResolvedValue"),
            )
            for dct in data.get("Parameters", [])
        },
        creation_time=data.get("CreationTime"),
        execution_status=ChangeSetExecutionStatusEnum.get_by_name(data.get("ExecutionStatus")),
        status=ChangeSetStatusEnum.get_by_name(data.get("Status")),
        status_reason=data.get("StatusReason"),
        notification_arns=data.get("NotificationARNs"),
        rollback_configuration=data.get("RollbackConfiguration"),
        capabilities=data.get("Capabilities"),
        tags=to_tag_dict(data.get("Tags", [])),
        changes=data.get("Changes", []),
        include_nested_stacks=data.get("IncludeNestedStacks"),
    )
