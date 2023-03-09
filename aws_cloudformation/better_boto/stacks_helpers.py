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
    true_flag_count = sum(
        [
            on_failure_do_nothing,
            on_failure_rollback,
            on_failure_delete,
        ]
    )
    if true_flag_count == 0:
        return
    elif true_flag_count == 1: # pragma: no cover
        if on_failure_do_nothing:
            kwargs["OnFailure"] = "DO_NOTHING"
        elif on_failure_rollback:
            kwargs["OnFailure"] = "ROLLBACK"
        elif on_failure_delete:
            kwargs["OnFailure"] = "DELETE"
        else:  # pragma: no cover
            raise NotImplementedError
    else: # pragma: no cover
        raise ValueError(
            "You can only set one of "
            "on_failure_do_nothing, on_failure_rollback, on_failure_delete to True!"
        )


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
