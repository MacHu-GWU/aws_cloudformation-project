# -*- coding: utf-8 -*-

"""
Implement the fancy deployment and remove API with "terraform plan" liked feature.
"""

import typing as T

from boto_session_manager import BotoSesManager

from . import exc
from .better_boto import (
    Parameter,
    DEFAULT_S3_PREFIX_FOR_TEMPLATE,
    DEFAULT_S3_PREFIX_FOR_STACK_POLICY,
    DEFAULT_UPDATE_DELAYS,
    DEFAULT_UPDATE_TIMEOUT,
    DEFAULT_CHANGE_SET_DELAYS,
    DEFAULT_CHANGE_SET_TIMEOUT,
    describe_live_stack,
    create_stack,
    update_stack,
    create_change_set,
    execute_change_set,
    delete_stack,
    wait_create_or_update_stack_to_finish,
    wait_delete_stack_to_finish,
    wait_create_change_set_to_finish,
    ChangeSetTypeEnum,
)
from .console import (
    get_stacks_view_console_url,
    get_stack_details_console_url,
    get_change_set_console_url,
)
from .change_set_visualizer import print_header, visualize_change_set


def prompt_to_proceed() -> bool:
    """
    Prompt to ask user to enter: "YES" or "NO"

    :return: True if user entered YES, otherwise returns False.
    """
    value = input("Type 'Y' or 'YES' to proceed: ")
    return value.strip() in ["Y", "YES"]


def _deploy_stack_without_change_set(
    bsm: "BotoSesManager",
    stack_name: str,
    template: T.Optional[str],
    use_previous_template: T.Optional[bool] = None,
    bucket: T.Optional[str] = None,
    prefix: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_TEMPLATE,
    parameters: T.List[Parameter] = None,
    tags: dict = None,
    execution_role_arn: T.Optional[str] = None,
    include_iam: bool = False,
    include_named_iam: bool = False,
    include_macro: bool = False,
    stack_policy: T.Optional[str] = None,
    prefix_stack_policy: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_STACK_POLICY,
    resource_types: T.Optional[T.List[str]] = None,
    client_request_token: T.Optional[str] = None,
    enable_termination_protection: T.Optional[bool] = None,
    disable_rollback: T.Optional[bool] = None,
    wait: bool = True,
    delays: T.Union[int, float] = DEFAULT_UPDATE_DELAYS,
    timeout: T.Union[int, float] = DEFAULT_UPDATE_TIMEOUT,
    skip_prompt: bool = False,
    verbose: bool = True,
):
    stack = describe_live_stack(bsm, stack_name)

    # doesn't exist, do create
    if stack is None:
        if skip_prompt is False:
            if prompt_to_proceed() is False:
                print("Do nothing.")
                return

        stack_id = create_stack(
            bsm=bsm,
            stack_name=stack_name,
            template=template,
            bucket=bucket,
            prefix=prefix,
            parameters=parameters,
            tags=tags,
            execution_role_arn=execution_role_arn,
            include_iam=include_iam,
            include_named_iam=include_named_iam,
            include_macro=include_macro,
            stack_policy=stack_policy,
            prefix_stack_policy=prefix_stack_policy,
            resource_types=resource_types,
            client_request_token=client_request_token,
            enable_termination_protection=enable_termination_protection,
        )
        if verbose:
            console_url = get_stack_details_console_url(stack_id=stack_id)
            print(f"  preview **create stack progress** at: {console_url}")
    # already exists, do update
    else:
        if verbose:
            console_url = get_stack_details_console_url(stack_id=stack.id)
            print(f"  preview **update stack progress** at: {console_url}")

        if skip_prompt is False:
            if prompt_to_proceed() is False:
                print("Do nothing.")
                return

        try:
            stack_id = update_stack(
                bsm=bsm,
                stack_name=stack_name,
                template=template,
                use_previous_template=use_previous_template,
                bucket=bucket,
                prefix=prefix,
                parameters=parameters,
                tags=tags,
                execution_role_arn=execution_role_arn,
                include_iam=include_iam,
                include_named_iam=include_named_iam,
                include_macro=include_macro,
                stack_policy=stack_policy,
                prefix_stack_policy=prefix_stack_policy,
                resource_types=resource_types,
                client_request_token=client_request_token,
                disable_rollback=disable_rollback,
            )
        except Exception as e:
            if "No updates are to be performed" in str(e):
                if verbose:
                    print("  No updates are to be performed.")
                return None
            else:
                raise e

    # wait until the stack is finished
    if wait:
        wait_create_or_update_stack_to_finish(
            bsm=bsm,
            stack_name=stack_id,
            delays=delays,
            timeout=timeout,
            verbose=verbose,
        )


def _deploy_stack_using_change_set(
    bsm: "BotoSesManager",
    stack_name: str,
    template: T.Optional[str],
    use_previous_template: T.Optional[bool] = None,
    bucket: T.Optional[str] = None,
    prefix: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_TEMPLATE,
    parameters: T.List[Parameter] = None,
    tags: dict = None,
    execution_role_arn: T.Optional[str] = None,
    include_iam: bool = False,
    include_named_iam: bool = False,
    include_macro: bool = False,
    stack_policy: T.Optional[str] = None,
    prefix_stack_policy: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_STACK_POLICY,
    resource_types: T.Optional[T.List[str]] = None,
    client_request_token: T.Optional[str] = None,
    disable_rollback: T.Optional[bool] = None,
    wait: bool = True,
    delays: T.Union[int, float] = DEFAULT_UPDATE_DELAYS,
    timeout: T.Union[int, float] = DEFAULT_UPDATE_TIMEOUT,
    change_set_delays: T.Union[int, float] = DEFAULT_CHANGE_SET_DELAYS,
    change_set_timeout: T.Union[int, float] = DEFAULT_CHANGE_SET_TIMEOUT,
    skip_prompt: bool = False,
    verbose: bool = True,
):
    stack = describe_live_stack(bsm, stack_name)

    create_change_set_kwargs = dict(
        bsm=bsm,
        stack_name=stack_name,
        template=template,
        use_previous_template=use_previous_template,
        bucket=bucket,
        prefix=prefix,
        parameters=parameters,
        tags=tags,
        execution_role_arn=execution_role_arn,
        include_iam=include_iam,
        include_named_iam=include_named_iam,
        include_macro=include_macro,
        stack_policy=stack_policy,
        prefix_stack_policy=prefix_stack_policy,
        resource_types=resource_types,
        change_set_type=ChangeSetTypeEnum.CREATE.value,
        client_request_token=client_request_token,
        disable_rollback=disable_rollback,
    )

    # doesn't exist, do create
    if stack is None:
        action = "create"
        create_change_set_kwargs["change_set_type"] = ChangeSetTypeEnum.CREATE.value
    # already exist, do update
    else:
        action = "update"
        create_change_set_kwargs["change_set_type"] = ChangeSetTypeEnum.UPDATE.value

    stack_id, change_set_id, change_set_name = create_change_set(
        **create_change_set_kwargs
    )

    if verbose:
        console_url = get_change_set_console_url(
            stack_id=stack_id,
            change_set_id=change_set_id,
        )
        print(f"  preview **change set details** at: {console_url}")

    try:
        response = wait_create_change_set_to_finish(
            bsm=bsm,
            stack_name=stack_name,
            change_set_id=change_set_id,
            delays=change_set_delays,
            timeout=change_set_timeout,
            verbose=verbose,
        )
        if verbose:
            visualize_change_set(response["Changes"])
    except TimeoutError as e:
        raise e
    except exc.CreateStackChangeSetButNotChangeError as e:
        print(f"    The submitted information didn't contain changes. Submit different information to create a change set.")
        return
    except exc.CreateStackChangeSetFailedError as e:
        raise e

    print("    need to execute the change set to apply those changes.")

    if skip_prompt is False:
        if prompt_to_proceed() is False:
            # create logic branch
            if stack is None:
                print("  cancel creation.")
                delete_stack(
                    bsm=bsm,
                    stack_name=stack_id,
                )
            else:
                print("  cancel update.")
            return

    if verbose:
        console_url = get_stack_details_console_url(stack_id=stack_id)
        print(f"  preview **{action} stack progress** at: {console_url}")

    response = execute_change_set(
        bsm=bsm,
        change_set_name=change_set_name,
        stack_name=stack_name,
        disable_rollback=disable_rollback,
    )

    # wait until the stack is finished
    if wait:
        wait_create_or_update_stack_to_finish(
            bsm=bsm,
            stack_name=stack_id,
            delays=delays,
            timeout=timeout,
            verbose=verbose,
        )


def deploy_stack(
    bsm: "BotoSesManager",
    stack_name: str,
    template: T.Optional[str],
    use_previous_template: T.Optional[bool] = None,
    bucket: T.Optional[str] = None,
    prefix: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_TEMPLATE,
    parameters: T.List[Parameter] = None,
    tags: dict = None,
    execution_role_arn: T.Optional[str] = None,
    include_iam: bool = False,
    include_named_iam: bool = False,
    include_macro: bool = False,
    stack_policy: T.Optional[str] = None,
    prefix_stack_policy: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_STACK_POLICY,
    resource_types: T.Optional[T.List[str]] = None,
    client_request_token: T.Optional[str] = None,
    enable_termination_protection: T.Optional[bool] = None,
    disable_rollback: T.Optional[bool] = None,
    wait: bool = True,
    delays: T.Union[int, float] = DEFAULT_UPDATE_DELAYS,
    timeout: T.Union[int, float] = DEFAULT_UPDATE_TIMEOUT,
    skip_plan: bool = False,
    skip_prompt: bool = False,
    change_set_delays: T.Union[int, float] = DEFAULT_CHANGE_SET_DELAYS,
    change_set_timeout: T.Union[int, float] = DEFAULT_CHANGE_SET_TIMEOUT,
    verbose: bool = True,
):
    """
    Deploy an AWS CloudFormation stack. But way more powerful than the original
    boto3 API.

    :param bsm:
    :param stack_name:
    :param template:
    :param use_previous_template:
    :param bucket:
    :param prefix:
    :param parameters:
    :param tags:
    :param execution_role_arn:
    :param include_iam:
    :param include_named_iam:
    :param include_macro:
    :param stack_policy:
    :param prefix_stack_policy:
    :param resource_types:
    :param client_request_token:
    :param enable_termination_protection:
    :param disable_rollback:
    :param wait:
    :param delays:
    :param timeout:
    :param skip_plan:
    :param skip_prompt:
    :param change_set_delays:
    :param change_set_timeout:
    :param verbose:
    :return:

    .. versionadded:: 0.1.1
    """
    if verbose:
        print_header(f"Deploy stack: {stack_name!r}", "=", 80)
        console_url = get_stacks_view_console_url(stack_name=stack_name)
        print(f"  preview stack in AWS CloudFormation console: {console_url}")

    if skip_plan is True:
        _deploy_stack_without_change_set(
            bsm=bsm,
            stack_name=stack_name,
            template=template,
            use_previous_template=use_previous_template,
            bucket=bucket,
            prefix=prefix,
            parameters=parameters,
            tags=tags,
            execution_role_arn=execution_role_arn,
            include_iam=include_iam,
            include_named_iam=include_named_iam,
            include_macro=include_macro,
            stack_policy=stack_policy,
            prefix_stack_policy=prefix_stack_policy,
            resource_types=resource_types,
            client_request_token=client_request_token,
            enable_termination_protection=enable_termination_protection,
            disable_rollback=disable_rollback,
            wait=wait,
            delays=delays,
            timeout=timeout,
            skip_prompt=skip_prompt,
            verbose=verbose,
        )
    else:
        _deploy_stack_using_change_set(
            bsm=bsm,
            stack_name=stack_name,
            template=template,
            use_previous_template=use_previous_template,
            bucket=bucket,
            prefix=prefix,
            parameters=parameters,
            tags=tags,
            execution_role_arn=execution_role_arn,
            include_iam=include_iam,
            include_named_iam=include_named_iam,
            include_macro=include_macro,
            stack_policy=stack_policy,
            prefix_stack_policy=prefix_stack_policy,
            resource_types=resource_types,
            client_request_token=client_request_token,
            disable_rollback=disable_rollback,
            wait=wait,
            delays=delays,
            timeout=timeout,
            change_set_delays=change_set_delays,
            change_set_timeout=change_set_timeout,
            skip_prompt=skip_prompt,
            verbose=verbose,
        )

    if verbose:
        print("  done")


def remove_stack(
    bsm: "BotoSesManager",
    stack_name: T.Optional[str] = None,
    retain_resources: T.Optional[T.List[str]] = None,
    role_arn: T.Optional[bool] = None,
    client_request_token: T.Optional[str] = None,
    wait: bool = True,
    delays: T.Union[int, float] = DEFAULT_UPDATE_DELAYS,
    timeout: T.Union[int, float] = DEFAULT_UPDATE_TIMEOUT,
    skip_prompt: bool = False,
    verbose: bool = True,
):
    """
    Remove an AWS CloudFormation Stack.

    :param bsm:
    :param stack_name:
    :param retain_resources:
    :param role_arn:
    :param client_request_token:
    :param wait:
    :param delays:
    :param timeout:
    :param skip_prompt:
    :param verbose:
    :return:
    
    .. versionadded:: 0.1.1
    """
    print_header(f"Remove stack {stack_name!r}", "=", 80)

    if verbose:
        console_url = get_stacks_view_console_url(stack_name)
        print(f"  preview stack in AWS CloudFormation console: {console_url}")

    stack = describe_live_stack(bsm, stack_name)

    if stack is None:
        print("  stack doesn't exists!")
        print("  done!")
        return

    if skip_prompt is False:
        if prompt_to_proceed() is False:
            print("Do nothing.")
            return

    delete_stack(
        bsm=bsm,
        stack_name=stack_name,
        retain_resources=retain_resources,
        role_arn=role_arn,
        client_request_token=client_request_token,
    )

    if wait:
        wait_delete_stack_to_finish(
            bsm=bsm,
            stack_id=stack.id,
            delays=delays,
            timeout=timeout,
            verbose=verbose,
        )

    if verbose:
        print("  done")
