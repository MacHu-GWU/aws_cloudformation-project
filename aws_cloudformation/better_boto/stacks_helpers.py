# -*- coding: utf-8 -*-

import typing as T

from func_args import NOTHING

from ..helper import get_true_flag_count
from ..stack import (
    Parameter,
    ChangeSetTypeEnum,
)


def resolve_capabilities_kwargs(
    kwargs: dict,
    include_iam: T.Optional[bool] = NOTHING,
    include_named_iam: T.Optional[bool] = NOTHING,
    include_macro: T.Optional[bool] = NOTHING,
):
    true_flag_count = get_true_flag_count(
        [
            include_iam,
            include_named_iam,
            include_macro,
        ]
    )

    if true_flag_count == 0:
        return

    capabilities = list()
    if include_iam:
        capabilities.append("CAPABILITY_IAM")
    if include_named_iam:
        capabilities.append("CAPABILITY_NAMED_IAM")
    if include_macro:
        capabilities.append("CAPABILITY_AUTO_EXPAND")
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
    on_failure_do_nothing: T.Optional[bool] = NOTHING,
    on_failure_rollback: T.Optional[bool] = NOTHING,
    on_failure_delete: T.Optional[bool] = NOTHING,
):
    true_flag_count = get_true_flag_count(
        [
            on_failure_do_nothing,
            on_failure_rollback,
            on_failure_delete,
        ]
    )
    if true_flag_count == 0:
        return
    elif true_flag_count == 1:  # pragma: no cover
        if on_failure_do_nothing:
            kwargs["OnFailure"] = "DO_NOTHING"
        elif on_failure_rollback:
            kwargs["OnFailure"] = "ROLLBACK"
        elif on_failure_delete:
            kwargs["OnFailure"] = "DELETE"
        else:  # pragma: no cover
            raise NotImplementedError
    else:  # pragma: no cover
        raise ValueError(
            "You can only set one of "
            "on_failure_do_nothing, on_failure_rollback, on_failure_delete to True!"
        )


def resolve_create_update_stack_common_kwargs(
    kwargs: dict,
    parameters: T.Optional[T.List[Parameter]] = NOTHING,
    tags: T.Optional[T.Dict[str, str]] = NOTHING,
    include_iam: T.Optional[bool] = NOTHING,
    include_named_iam: T.Optional[bool] = NOTHING,
    include_macro: T.Optional[bool] = NOTHING,
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
    change_set_type_is_create: T.Optional[bool] = NOTHING,
    change_set_type_is_update: T.Optional[bool] = NOTHING,
    change_set_type_is_import: T.Optional[bool] = NOTHING,
):
    true_flag_count = get_true_flag_count(
        [
            change_set_type_is_create,
            change_set_type_is_update,
            change_set_type_is_import,
        ]
    )
    if true_flag_count == 0:  # pragma: no cover
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
    else:  # pragma: no cover
        raise ValueError(
            "You can only set one of "
            "change_set_type_is_create, "
            "change_set_type_is_update, "
            "change_set_type_is_import to True!"
        )
