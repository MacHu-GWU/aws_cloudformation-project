# -*- coding: utf-8 -*-

"""
Implement the fancy deployment and remove API with "terraform plan" liked feature.
"""

import typing as T

from boto_session_manager import BotoSesManager
from colorama import Fore, Style

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
    StackStatusEnum,
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
            verbose=verbose,
        )
        if verbose:
            console_url = get_stack_details_console_url(stack_id=stack_id)
            print(
                f"  preview {Fore.CYAN}create stack progress{Style.RESET_ALL} at: {console_url}"
            )
    # already exists, do update
    else:
        if verbose:
            console_url = get_stack_details_console_url(stack_id=stack.id)
            print(
                f"  preview {Fore.CYAN}update stack progress{Style.RESET_ALL} at: {console_url}"
            )

        if stack.status == StackStatusEnum.REVIEW_IN_PROGRESS:
            raise ValueError(
                f"You cannot update a stack when status is {StackStatusEnum.REVIEW_IN_PROGRESS.value}! "
                f"It could be because you created the stack using change set, "
                f"but never take action to approve or deny it. "
                f"You can delete it and retry."
            )

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
                verbose=verbose,
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
        verbose=verbose,
    )

    # doesn't exist, do create
    if stack is None:
        action = "create"
        create_change_set_kwargs["change_set_type"] = ChangeSetTypeEnum.CREATE.value
    # already exist, do update
    else:
        if stack.status == StackStatusEnum.REVIEW_IN_PROGRESS:
            raise ValueError(
                f"You cannot update a stack when status is {StackStatusEnum.REVIEW_IN_PROGRESS.value}! "
                f"It could be because you created the stack using change set, "
                f"but never take action to approve or deny it. "
                f"You can delete it and retry."
            )

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
        print(
            f"  preview {Fore.CYAN}change set details{Style.RESET_ALL} at: {console_url}"
        )

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
        print(
            f"    The submitted information didn't contain changes. Submit different information to create a change set."
        )
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
        print(
            f"  preview {Fore.CYAN}{action} stack progress{Style.RESET_ALL} at: {console_url}"
        )

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
    Deploy (create or update) an AWS CloudFormation stack. But way more powerful
    than the original boto3 API.

    Reference:

    - Create Stack Boto3 API: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.create_stack
    - Update Stack Boto3 API: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.update_stack

    :param bsm: ``boto_session_manager.BotoSesManager`` object
    :param stack_name: the stack name or unique stack id
    :param template: CloudFormation template JSON or Yaml body in text, or the
        s3 uri pointing to a CloudFormation template file.
    :param use_previous_template: see "Update Stack Boto3 API" link
    :param bucket: default None; if given, automatically upload template to S3
        before deployment. see :func:`~aws_cloudformation.better_boto.upload_template_to_s3`
        for more details.
    :param prefix: the s3 prefix where you want to upload the template to
    :param parameters: see "Update Stack Boto3 API" link
    :param tags: see "Update Stack Boto3 API" link
    :param execution_role_arn: see "Update Stack Boto3 API" link
    :param include_iam: see "Capacities" part in "Update Stack Boto3 API" link
    :param include_named_iam: see "Capacities" part in "Update Stack Boto3 API" link
    :param include_macro: see "Capacities" part in "Update Stack Boto3 API" link
    :param stack_policy: Stack Policy JSON or Yaml body in text, or the
        s3 uri pointing to a Stack Policy JSON template file.
    :param prefix_stack_policy: see "Update Stack Boto3 API" link
    :param resource_types: see "Update Stack Boto3 API" link
    :param client_request_token: see "Update Stack Boto3 API" link
    :param enable_termination_protection: see "Create Stack Boto3 API" link
    :param disable_rollback: see "Update Stack Boto3 API" link
    :param wait: default True; if True, then wait the create / update action
        to success or fail; if False, then it is an async call and return immediately;
        note that if you have skip_plan is False (using change set), you always
        have to wait the change set creation to finish.
    :param delays: how long it waits (in seconds) between two
        "describe_stacks" api call to get the stack status
    :param timeout: how long it will raise timeout error
    :param skip_plan: default False; if False, force to use change set to
        create / update; if True, then do create / update without change set.
    :param skip_prompt: default False; if False, you have to enter "Yes"
        in prompt to do deployment; if True, then execute the deployment directly.
    :param change_set_delays: how long it waits (in seconds) between two
        "describe_change_set" api call to get the change set status
    :param change_set_timeout: how long it will raise timeout error
    :param verbose: whether you want to log information to console

    :return: Nothing

    .. versionadded:: 0.1.1
    """
    if verbose:
        print_header(
            f"{Fore.CYAN}Deploy{Style.RESET_ALL} stack: {Fore.CYAN}{stack_name}{Style.RESET_ALL}",
            "=",
            80,
        )
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

    Reference:

    - Delete Stack Boto3 API: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.delete_stack

    :param bsm: ``boto_session_manager.BotoSesManager`` object
    :param stack_name: the stack name or unique stack id
    :param retain_resources: see "Delete Stack Boto3 API" link
    :param role_arn: see "Delete Stack Boto3 API" link
    :param client_request_token: see "Delete Stack Boto3 API" link
    :param wait: default True; if True, then wait the delete action
        to success or fail; if False, then it is an async call and return immediately.
    :param delays: how long it waits (in seconds) between two
        "describe_stacks" api call to get the stack status
    :param timeout: how long it will raise timeout error
    :param skip_prompt: default False; if False, you have to enter "Yes"
        in prompt to do deletion; if True, then execute the deletion directly.
    :param verbose: whether you want to log information to console

    :return: Nothing

    .. versionadded:: 0.1.1
    """
    print_header(
        f"{Fore.CYAN}Remove{Style.RESET_ALL} stack {Fore.CYAN}{stack_name}{Style.RESET_ALL}",
        "=",
        80,
    )

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
