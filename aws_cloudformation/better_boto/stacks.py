# -*- coding: utf-8 -*-

"""
AWS CloudFormation Stack related operations.
"""

import typing as T

from boto_session_manager import BotoSesManager, AwsServiceEnum
from iterproxy import IterProxy
from func_args import NOTHING, resolve_kwargs
from colorama import Fore, Style

from .. import exc
from ..waiter import Waiter
from ..stack import (
    Parameter,
    Stack,
    ChangeSetStatusEnum,
    ChangeSet,
)

from .stacks_helpers import (
    resolve_on_failure,
    resolve_create_update_stack_common_kwargs,
    resolve_change_set_type,
)


def _describe_stacks(
    bsm: BotoSesManager,
    name: str,
) -> T.Iterable[Stack]:
    cf_client = bsm.get_client(AwsServiceEnum.CloudFormation)
    paginator = cf_client.get_paginator("describe_stacks")
    response_iterator = paginator.paginate(
        StackName=name,
    )
    try:
        for response in response_iterator:
            for data in response.get("Stacks", []):
                yield Stack.from_describe_stacks_response(data)
    except Exception as e:
        if "does not exist" in str(e):
            return []
        else:
            raise e


class StackIterProxy(IterProxy[Stack]):
    """ """


def describe_stacks(
    bsm: BotoSesManager,
    name: str,
) -> StackIterProxy:
    """
    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stacks
    """
    return StackIterProxy(
        _describe_stacks(bsm=bsm, name=name),
    )


def describe_live_stack(
    bsm: BotoSesManager,
    name: str,
) -> T.Optional[Stack]:
    """
    Get the detail of given stack (by name), if it not exists, or the existing
    one is a "DELETED" stack, returns None.
    """
    stacks = describe_stacks(bsm, name).all()
    found = False
    live_stack = None
    for stack in stacks:
        if stack.status.is_live():
            found = True
            live_stack = stack
            break
    if found:
        return live_stack
    else:
        return None


def create_stack(
    bsm: BotoSesManager,
    stack_name: str,
    template_body: T.Optional[str] = NOTHING,
    template_url: T.Optional[str] = NOTHING,
    parameters: T.Optional[T.List[Parameter]] = NOTHING,
    disable_rollback: T.Optional[bool] = NOTHING,
    rollback_configuration: T.Optional[dict] = NOTHING,
    timeout_in_minutes: T.Optional[int] = NOTHING,
    notification_arns: T.Optional[T.List[str]] = NOTHING,
    include_iam: bool = False,
    include_named_iam: bool = False,
    include_macro: bool = False,
    resource_types: T.Optional[T.List[str]] = NOTHING,
    execution_role_arn: T.Optional[str] = NOTHING,
    on_failure_do_nothing: T.Optional[bool] = False,
    on_failure_rollback: T.Optional[bool] = False,
    on_failure_delete: T.Optional[bool] = False,
    stack_policy_body: T.Optional[str] = NOTHING,
    stack_policy_url: T.Optional[str] = NOTHING,
    tags: T.Optional[T.Dict[str, str]] = NOTHING,
    client_request_token: T.Optional[str] = NOTHING,
    enable_termination_protection: T.Optional[bool] = NOTHING,
    verbose: bool = True,
) -> str:
    """
    A wrapper provider more user-friendly API and type hint for
    cloudformation client ``create_stack`` method.

    Ref:

    - create_stack: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.create_stack

    :return: stack_id
    """
    kwargs = dict(
        StackName=stack_name,
        TemplateBody=template_body,
        TemplateURL=template_url,
        DisableRollback=disable_rollback,
        RollbackConfiguration=rollback_configuration,
        TimeoutInMinutes=timeout_in_minutes,
        NotificationARNs=notification_arns,
        ResourceTypes=resource_types,
        RoleARN=execution_role_arn,
        StackPolicyBody=stack_policy_body,
        StackPolicyURL=stack_policy_url,
        ClientRequestToken=client_request_token,
        EnableTerminationProtection=enable_termination_protection,
    )
    resolve_on_failure(
        kwargs,
        on_failure_do_nothing=on_failure_do_nothing,
        on_failure_rollback=on_failure_rollback,
        on_failure_delete=on_failure_delete,
    )
    resolve_create_update_stack_common_kwargs(
        kwargs=kwargs,
        parameters=parameters,
        tags=tags,
        include_iam=include_iam,
        include_named_iam=include_named_iam,
        include_macro=include_macro,
    )
    response = bsm.cloudformation_client.create_stack(**resolve_kwargs(**kwargs))
    stack_id = response["StackId"]
    return stack_id


def update_stack(
    bsm: BotoSesManager,
    stack_name: str,
    template_body: T.Optional[str] = NOTHING,
    template_url: T.Optional[str] = NOTHING,
    use_previous_template: T.Optional[bool] = NOTHING,
    parameters: T.Optional[T.List[Parameter]] = NOTHING,
    disable_rollback: T.Optional[bool] = NOTHING,
    rollback_configuration: T.Optional[dict] = NOTHING,
    notification_arns: T.Optional[T.List[str]] = NOTHING,
    include_iam: bool = False,
    include_named_iam: bool = False,
    include_macro: bool = False,
    resource_types: T.Optional[T.List[str]] = NOTHING,
    execution_role_arn: T.Optional[str] = NOTHING,
    stack_policy_body: T.Optional[str] = NOTHING,
    stack_policy_url: T.Optional[str] = NOTHING,
    stack_policy_during_update_body: T.Optional[str] = NOTHING,
    stack_policy_during_update_url: T.Optional[str] = NOTHING,
    tags: T.Optional[T.Dict[str, str]] = NOTHING,
    client_request_token: T.Optional[str] = NOTHING,
    verbose: bool = True,
) -> str:
    """
    A wrapper provider more user-friendly API and type hint for
    cloudformation client ``update_stack`` method.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.update_stack

    :return: stack_id
    """
    kwargs = dict(
        StackName=stack_name,
        TemplateBody=template_body,
        TemplateURL=template_url,
        UsePreviousTemplate=use_previous_template,
        DisableRollback=disable_rollback,
        RollbackConfiguration=rollback_configuration,
        NotificationARNs=notification_arns,
        ResourceTypes=resource_types,
        RoleARN=execution_role_arn,
        StackPolicyBody=stack_policy_body,
        StackPolicyURL=stack_policy_url,
        StackPolicyDuringUpdateBody=stack_policy_during_update_body,
        StackPolicyDuringUpdateURL=stack_policy_during_update_url,
        ClientRequestToken=client_request_token,
    )
    resolve_create_update_stack_common_kwargs(
        kwargs=kwargs,
        parameters=parameters,
        tags=tags,
        include_iam=include_iam,
        include_named_iam=include_named_iam,
        include_macro=include_macro,
    )
    response = bsm.cloudformation_client.update_stack(**resolve_kwargs(**kwargs))
    stack_id = response["StackId"]
    return stack_id


def create_change_set(
    bsm: BotoSesManager,
    stack_name: str,
    change_set_name: str,
    template_body: T.Optional[str] = NOTHING,
    template_url: T.Optional[str] = NOTHING,
    use_previous_template: T.Optional[bool] = NOTHING,
    parameters: T.Optional[T.List[Parameter]] = NOTHING,
    include_iam: bool = False,
    include_named_iam: bool = False,
    include_macro: bool = False,
    resource_types: T.Optional[T.List[str]] = NOTHING,
    execution_role_arn: T.Optional[str] = NOTHING,
    rollback_configuration: T.Optional[dict] = NOTHING,
    notification_arns: T.Optional[T.List[str]] = NOTHING,
    tags: T.Optional[T.Dict[str, str]] = NOTHING,
    client_request_token: T.Optional[str] = NOTHING,
    description: T.Optional[str] = NOTHING,
    change_set_type_is_create: T.Optional[bool] = False,
    change_set_type_is_update: T.Optional[bool] = False,
    change_set_type_is_import: T.Optional[bool] = False,
    resources_to_import: T.Optional[T.List[dict]] = NOTHING,
    include_nested_stack: T.Optional[bool] = NOTHING,
    verbose: bool = True,
) -> T.Tuple[str, str]:
    """
    A wrapper provider more user-friendly API and type hint for
    cloudformation client ``create_change_set`` method.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.create_change_set

    :return: stack_id and change_set_id
    """
    kwargs = dict(
        StackName=stack_name,
        TemplateBody=template_body,
        TemplateURL=template_url,
        UsePreviousTemplate=use_previous_template,
        ResourceTypes=resource_types,
        RoleARN=execution_role_arn,
        RollbackConfiguration=rollback_configuration,
        NotificationARNs=notification_arns,
        ChangeSetName=change_set_name,
        ClientToken=client_request_token,
        Description=description,
        ResourcesToImport=resources_to_import,
        IncludeNestedStacks=include_nested_stack,
    )
    resolve_change_set_type(
        kwargs=kwargs,
        change_set_type_is_create=change_set_type_is_create,
        change_set_type_is_update=change_set_type_is_update,
        change_set_type_is_import=change_set_type_is_import,
    )
    resolve_create_update_stack_common_kwargs(
        kwargs=kwargs,
        parameters=parameters,
        tags=tags,
        include_iam=include_iam,
        include_named_iam=include_named_iam,
        include_macro=include_macro,
    )
    response = bsm.cloudformation_client.create_change_set(**resolve_kwargs(**kwargs))
    stack_id = response["StackId"]
    change_set_id = response["Id"]
    return stack_id, change_set_id


def describe_change_set(
    bsm: "BotoSesManager",
    change_set_name: str,
    stack_name: T.Optional[str] = NOTHING,
    next_token: T.Optional[str] = NOTHING,
) -> T.Optional[ChangeSet]:
    """
    A wrapper provider more user-friendly API and type hint for
    cloudformation client ``describe_change_set`` method.

    Ref:

    - describe_change_set: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_change_set
    """
    kwargs = dict(
        ChangeSetName=change_set_name,
        StackName=stack_name,
        NextToken=next_token,
    )
    try:
        response = bsm.cloudformation_client.describe_change_set(
            **resolve_kwargs(**kwargs)
        )
        change_set = ChangeSet.from_describe_change_set_response(response)
        return change_set
    except Exception as e:
        if "does not exist" in str(e):
            return None
        else:
            raise e


def describe_change_set_with_paginator(
    bsm: "BotoSesManager",
    change_set_name: str,
    stack_name: T.Optional[str] = NOTHING,
    max_items: T.Optional[int] = 1000,
    starting_token: T.Optional[str] = NOTHING,
) -> T.Optional[ChangeSet]:
    """
    A wrapper provider more user-friendly API and type hint for
    cloudformation client ``Paginator.DescribeChangeSet`` API.

    Ref:

    - DescribeChangeSet: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/paginator/DescribeChangeSet.html
    """
    paginator = bsm.cloudformation_client.get_paginator("describe_change_set")
    pagination_config = dict()
    if max_items is not NOTHING:
        pagination_config["MaxItems"] = max_items
    if starting_token is not NOTHING:
        pagination_config["StartingToken"] = starting_token
    kwargs = dict(
        ChangeSetName=change_set_name,
        StackName=stack_name,
        PaginationConfig=pagination_config,
    )
    response_iterator = paginator.paginate(**resolve_kwargs(**kwargs))
    changes = list()
    found_change_set = False
    for response in response_iterator:
        change_set = ChangeSet.from_describe_change_set_response(response)
        changes.extend(change_set.changes)
        found_change_set = True
    if found_change_set:
        change_set.changes = changes
        return change_set
    else:
        return None


def execute_change_set(
    bsm: "BotoSesManager",
    change_set_name: str,
    stack_name: T.Optional[str] = NOTHING,
    client_request_token: T.Optional[str] = NOTHING,
    disable_rollback: T.Optional[bool] = NOTHING,
):
    """
    A wrapper provider more user-friendly API and type hint for
    cloudformation client ``execute_change_set`` method.

    Ref:

    - execute_change_set: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.execute_change_set
    """
    kwargs = dict(
        ChangeSetName=change_set_name,
        StackName=stack_name,
        ClientRequestToken=client_request_token,
        DisableRollback=disable_rollback,
    )
    bsm.cloudformation_client.execute_change_set(**resolve_kwargs(**kwargs))


def delete_stack(
    bsm: "BotoSesManager",
    stack_name: str,
    retain_resources: T.Optional[T.List[str]] = NOTHING,
    role_arn: T.Optional[bool] = NOTHING,
    client_request_token: T.Optional[str] = NOTHING,
):
    """
    A wrapper provider more user-friendly API and type hint for
    cloudformation client ``delete_stack`` method.

    Ref:

    - delete_stack: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.delete_stack
    """
    kwargs = dict(
        StackName=stack_name,
        RetainResources=retain_resources,
        RoleARN=role_arn,
        ClientRequestToken=client_request_token,
    )
    bsm.cloudformation_client.delete_stack(**resolve_kwargs(**kwargs))


def wait_create_or_update_stack_to_finish(
    bsm: "BotoSesManager",
    stack_name: str,
    delays: T.Union[int, float],
    timeout: T.Union[int, float],
    verbose: bool,
) -> Stack:
    """
    You can run this function after you run :func:`create_stack` or
    :func:`update_stack`. It will wait until the stack change success, fail,
    or timeout.

    :param bsm: ``boto_session_manager.BotoSesManager`` object
    :param stack_name: the stack name or unique stack id
    :param delays: how long it waits (in seconds) between two "get status" api call
    :param timeout: how long it will raise timeout error
    :param verbose: whether you want to log information to console

    :return: a :class:`~aws_cottonformation.stack.Stack` object.
    """
    if verbose:  # pragma: no cover # pragma: no cover
        print(f" {Fore.CYAN}wait for deploy to finish{Style.RESET_ALL} ...")
    for _ in Waiter(
        delays=delays,
        timeout=timeout,
        indent=4,
        verbose=verbose,
    ):
        stack = describe_live_stack(bsm, stack_name)
        if stack.is_stopped():
            if verbose:  # pragma: no cover
                if stack.is_success():
                    icon = "🟢"
                else:
                    icon = "🔴"
                print(
                    f"\n    reached status {icon} {Fore.CYAN}{stack.status.value!r}{Style.RESET_ALL}"
                )
            return stack


def wait_delete_stack_to_finish(
    bsm: "BotoSesManager",
    stack_id: str,
    delays: T.Union[int, float],
    timeout: T.Union[int, float],
    verbose: bool,
):
    """
    You can run this function after you run :func:`delete_stack`. It will
    wait until the stack deletion success or fail.
    or timeout.

    :param bsm: ``boto_session_manager.BotoSesManager`` object
    :param stack_id: the unique stack id, you cannot use stack_name here
    :param delays: how long it waits (in seconds) between two "get status" api call
    :param timeout: how long it will raise timeout error
    :param verbose: whether you want to log information to console

    :return: Nothing
    """
    if verbose:  # pragma: no cover
        print(f"  {Fore.CYAN}wait for delete to finish{Style.RESET_ALL} ...")
    for _ in Waiter(
        delays=delays,
        timeout=timeout,
        indent=4,
        verbose=verbose,
    ):
        stacks = describe_stacks(bsm, name=stack_id).all()
        if len(stacks) == 0:
            if verbose:  # pragma: no cover
                print(f"\n    🟢 already deleted.")
            return
        else:
            stack = stacks[0]
            if stack.is_stopped():
                if verbose:  # pragma: no cover
                    if stack.is_success():
                        icon = "🟢"
                    else:
                        icon = "🔴"
                    print(
                        f"\n    reached status {icon} {Fore.CYAN}{stack.status.value}{Style.RESET_ALL}"
                    )
            return


def wait_create_change_set_to_finish(
    bsm: "BotoSesManager",
    stack_name: str,
    change_set_id: str,
    delays: T.Union[int, float],
    timeout: T.Union[int, float],
    verbose: bool,
) -> T.Optional[ChangeSet]:
    """
    You can run this function after you run :func:`create_change_set`. It will
    wait until the change set creation success, fail, or timeout.

    :param bsm:
    :param stack_name:
    :param change_set_id:
    :param delays:
    :param timeout:
    :param verbose:

    :return: ``ChangeSet`` object
    """
    if verbose:  # pragma: no cover
        print(
            f"  {Fore.CYAN}wait for change set creation to finish{Style.RESET_ALL} ..."
        )

    for _ in Waiter(
        delays=delays,
        timeout=timeout,
        indent=4,
        verbose=verbose,
    ):
        change_set = describe_change_set(
            bsm=bsm,
            change_set_name=change_set_id,
            stack_name=stack_name,
        )
        if change_set is None:
            return None

        if change_set.status in [
            ChangeSetStatusEnum.CREATE_COMPLETE.value,
            ChangeSetStatusEnum.FAILED.value,
        ]:
            if verbose:  # pragma: no cover
                print(
                    f"\n    reached status {Fore.CYAN}{change_set.status}{Style.RESET_ALL}"
                )

            if (
                change_set.status == ChangeSetStatusEnum.FAILED.value
            ):  # pragma: no cover
                if (
                    "The submitted information didn't contain changes."
                    in change_set.status_reason
                ):
                    raise exc.CreateStackChangeSetButNotChangeError(
                        change_set.status_reason
                    )
                else:
                    raise exc.CreateStackChangeSetFailedError(change_set.status_reason)

            if bool(change_set.next_token) and (
                bool(len(change_set.changes))
            ):  # pragma: no cover
                describe_change_set_with_paginator(
                    bsm=bsm,
                    change_set_name=change_set_id,
                    stack_name=stack_name,
                    max_items=1000,
                )
                rest_of_change_set = describe_change_set_with_paginator(
                    bsm=bsm,
                    change_set_name=change_set_id,
                    stack_name=stack_name,
                )
                change_set.changes.extend(rest_of_change_set.changes)

            return change_set
