# -*- coding: utf-8 -*-

"""
Implement the fancy deployment and remove API with "terraform plan" liked feature.
"""

import typing as T
import dataclasses
from datetime import datetime

from boto_session_manager import BotoSesManager
from aws_console_url import AWSConsole
from colorama import Fore, Style
from func_args import NOTHING, resolve_kwargs

from . import (
    exc,
    better_boto,
)
from .stack import (
    Parameter,
    StackStatusEnum,
)
from .console import (
    get_stacks_view_console_url,
    get_stack_details_console_url,
    get_change_set_console_url,
)
from .change_set_visualizer import (
    print_header,
    visualize_change_set,
)
from .deploy_helpers import (
    DEFAULT_S3_PREFIX_FOR_TEMPLATE,
    DEFAULT_S3_PREFIX_FOR_STACK_POLICY,
    resolve_template_kwargs,
    resolve_stack_policy_kwargs,
    get_filter_stack_set_console_url,
)

DEFAULT_CHANGE_SET_DELAYS = 5
DEFAULT_CHANGE_SET_TIMEOUT = 120
DEFAULT_UPDATE_DELAYS = 5
DEFAULT_UPDATE_TIMEOUT = 120


def prompt_to_proceed() -> bool:  # pragma: no cover
    """
    Prompt to ask user to enter: "YES" or "NO"

    :return: True if user entered YES, otherwise returns False.
    """
    value = input("Type 'Y' or 'YES' to proceed: ")
    return value.strip() in ["Y", "YES"]


@dataclasses.dataclass
class DeployStackResponse:
    is_deploy_happened: bool = dataclasses.field(default=False)
    is_create: T.Optional[bool] = dataclasses.field(default=None)
    stack_id: T.Optional[str] = dataclasses.field(default=None)
    change_set_id: T.Optional[str] = dataclasses.field(default=None)


def _deploy_stack_without_change_set(
    bsm: "BotoSesManager",
    stack_name: str,
    template: T.Optional[str] = NOTHING,
    use_previous_template: T.Optional[bool] = NOTHING,
    bucket: T.Optional[str] = None,
    prefix: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_TEMPLATE,
    parameters: T.Optional[T.List[Parameter]] = NOTHING,
    tags: T.Optional[T.Dict[str, str]] = NOTHING,
    execution_role_arn: T.Optional[str] = NOTHING,
    include_iam: T.Optional[bool] = NOTHING,
    include_named_iam: T.Optional[bool] = NOTHING,
    include_macro: T.Optional[bool] = NOTHING,
    stack_policy: T.Optional[str] = NOTHING,
    prefix_stack_policy: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_STACK_POLICY,
    resource_types: T.Optional[T.List[str]] = NOTHING,
    client_request_token: T.Optional[str] = NOTHING,
    enable_termination_protection: T.Optional[bool] = NOTHING,
    disable_rollback: T.Optional[bool] = NOTHING,
    rollback_configuration: T.Optional[dict] = NOTHING,
    notification_arns: T.Optional[T.List[str]] = NOTHING,
    on_failure_do_nothing: T.Optional[bool] = NOTHING,
    on_failure_rollback: T.Optional[bool] = NOTHING,
    on_failure_delete: T.Optional[bool] = NOTHING,
    wait: bool = True,
    delays: T.Union[int, float] = DEFAULT_UPDATE_DELAYS,
    timeout: T.Union[int, float] = DEFAULT_UPDATE_TIMEOUT,
    wait_until_exec_stopped_on_failure: bool = False,
    skip_prompt: bool = False,
    verbose: bool = True,
) -> DeployStackResponse:
    stack = better_boto.describe_live_stack(
        bsm=bsm,
        name=stack_name,
    )

    # doesn't exist, do create
    if stack is None:
        is_create = True
        if skip_prompt is False:  # pragma: no cover
            if prompt_to_proceed() is False:
                print("Do nothing.")
                return DeployStackResponse()
        kwargs = dict(
            bsm=bsm,
            stack_name=stack_name,
            parameters=parameters,
            tags=tags,
            execution_role_arn=execution_role_arn,
            include_iam=include_iam,
            include_named_iam=include_named_iam,
            include_macro=include_macro,
            resource_types=resource_types,
            client_request_token=client_request_token,
            enable_termination_protection=enable_termination_protection,
            disable_rollback=disable_rollback,
            rollback_configuration=rollback_configuration,
            notification_arns=notification_arns,
            on_failure_do_nothing=on_failure_do_nothing,
            on_failure_rollback=on_failure_rollback,
            on_failure_delete=on_failure_delete,
            verbose=verbose,
        )
        resolve_template_kwargs(
            kwargs=kwargs,
            bsm=bsm,
            template=template,
            bucket=bucket,
            prefix=prefix,
            verbose=verbose,
        )
        resolve_stack_policy_kwargs(
            kwargs=kwargs,
            bsm=bsm,
            stack_policy=stack_policy,
            bucket=bucket,
            prefix=prefix_stack_policy,
            verbose=verbose,
        )
        stack_id = better_boto.create_stack(**resolve_kwargs(**kwargs))
        if verbose:
            console_url = get_stack_details_console_url(stack_id=stack_id)
            print(
                f"  📋 preview {Fore.CYAN}create stack progress{Style.RESET_ALL} at: {console_url}"
            )
    # already exists, do update
    else:
        is_create = False
        if verbose:
            console_url = get_stack_details_console_url(stack_id=stack.id)
            print(
                f"  📋 preview {Fore.CYAN}update stack progress{Style.RESET_ALL} at: {console_url}"
            )

        if stack.status == StackStatusEnum.REVIEW_IN_PROGRESS:  # pragma: no cover
            raise ValueError(
                f"You cannot update a stack when status is {StackStatusEnum.REVIEW_IN_PROGRESS.value}! "
                f"It could be because you created the stack using change set, "
                f"but never take action to approve or deny it. "
                f"You can delete it and retry."
            )

        if skip_prompt is False:  # pragma: no cover
            if prompt_to_proceed() is False:
                print("Do nothing.")
                return DeployStackResponse()

        try:
            kwargs = dict(
                bsm=bsm,
                stack_name=stack_name,
                use_previous_template=use_previous_template,
                parameters=parameters,
                tags=tags,
                execution_role_arn=execution_role_arn,
                include_iam=include_iam,
                include_named_iam=include_named_iam,
                include_macro=include_macro,
                resource_types=resource_types,
                client_request_token=client_request_token,
                disable_rollback=disable_rollback,
                rollback_configuration=rollback_configuration,
                notification_arns=notification_arns,
                verbose=verbose,
            )
            resolve_template_kwargs(
                kwargs=kwargs,
                bsm=bsm,
                template=template,
                bucket=bucket,
                prefix=prefix,
                verbose=verbose,
            )
            resolve_stack_policy_kwargs(
                kwargs=kwargs,
                bsm=bsm,
                stack_policy=stack_policy,
                bucket=bucket,
                prefix=prefix_stack_policy,
                verbose=verbose,
            )
            stack_id = better_boto.update_stack(**resolve_kwargs(**kwargs))
        except Exception as e:
            if "No updates are to be performed" in str(e):
                if verbose:
                    print("  🟡 no updates are to be performed.")
                return DeployStackResponse()
            else:  # pragma: no cover
                raise e

    # wait until the stack is finished
    if wait:
        better_boto.wait_create_or_update_stack_to_finish(
            bsm=bsm,
            stack_name=stack_id,
            wait_until_exec_stopped=wait_until_exec_stopped_on_failure,
            delays=delays,
            timeout=timeout,
            verbose=verbose,
        )
    return DeployStackResponse(
        is_deploy_happened=True,
        is_create=is_create,
        stack_id=stack_id,
    )


def change_set_name_suffix() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3]


def _deploy_stack_using_change_set(
    bsm: "BotoSesManager",
    stack_name: str,
    template: T.Optional[str] = NOTHING,
    use_previous_template: T.Optional[bool] = NOTHING,
    bucket: T.Optional[str] = NOTHING,
    prefix: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_TEMPLATE,
    parameters: T.Optional[T.List[Parameter]] = NOTHING,
    tags: T.Optional[T.Dict[str, str]] = NOTHING,
    execution_role_arn: T.Optional[str] = NOTHING,
    include_iam: T.Optional[bool] = NOTHING,
    include_named_iam: T.Optional[bool] = NOTHING,
    include_macro: T.Optional[bool] = NOTHING,
    stack_policy: T.Optional[str] = NOTHING,
    prefix_stack_policy: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_STACK_POLICY,
    resource_types: T.Optional[T.List[str]] = NOTHING,
    client_request_token: T.Optional[str] = NOTHING,
    disable_rollback: T.Optional[bool] = NOTHING,
    rollback_configuration: T.Optional[dict] = NOTHING,
    notification_arns: T.Optional[T.List[str]] = NOTHING,
    plan_nested_stack: bool = True,
    wait: bool = True,
    delays: T.Union[int, float] = DEFAULT_UPDATE_DELAYS,
    timeout: T.Union[int, float] = DEFAULT_UPDATE_TIMEOUT,
    wait_until_exec_stopped_on_failure: bool = False,
    change_set_delays: T.Union[int, float] = DEFAULT_CHANGE_SET_DELAYS,
    change_set_timeout: T.Union[int, float] = DEFAULT_CHANGE_SET_TIMEOUT,
    skip_prompt: bool = False,
    verbose: bool = True,
) -> DeployStackResponse:
    stack = better_boto.describe_live_stack(bsm, stack_name)
    change_set_name = f"{stack_name}-{change_set_name_suffix()}"
    create_change_set_kwargs = dict(
        bsm=bsm,
        stack_name=stack_name,
        change_set_name=change_set_name,
        use_previous_template=use_previous_template,
        parameters=parameters,
        tags=tags,
        execution_role_arn=execution_role_arn,
        include_iam=include_iam,
        include_named_iam=include_named_iam,
        include_macro=include_macro,
        resource_types=resource_types,
        rollback_configuration=rollback_configuration,
        notification_arns=notification_arns,
        client_request_token=client_request_token,
        include_nested_stack=plan_nested_stack,
        verbose=verbose,
    )
    resolve_template_kwargs(
        kwargs=create_change_set_kwargs,
        bsm=bsm,
        template=template,
        bucket=bucket,
        prefix=prefix,
        verbose=verbose,
    )
    resolve_stack_policy_kwargs(
        kwargs=create_change_set_kwargs,
        bsm=bsm,
        stack_policy=stack_policy,
        bucket=bucket,
        prefix=prefix_stack_policy,
        verbose=verbose,
    )

    # doesn't exist, do create
    if stack is None:
        is_create = True
        execute_message = "+ create stack progress"
        create_change_set_kwargs["change_set_type_is_create"] = True
    # already exist, do update
    else:
        if stack.status == StackStatusEnum.REVIEW_IN_PROGRESS:  # pragma: no cover
            raise ValueError(
                f"You cannot update a stack when status is {StackStatusEnum.REVIEW_IN_PROGRESS.value}! "
                f"It could be because you created the stack using change set, "
                f"but never take action to approve or deny it. "
                f"You can delete it and retry."
            )
        is_create = False
        execute_message = "+/- update stack progress"
        create_change_set_kwargs["change_set_type_is_update"] = True

    stack_id, change_set_id = better_boto.create_change_set(
        **resolve_kwargs(**create_change_set_kwargs)
    )

    if verbose:
        console_url = get_change_set_console_url(
            stack_id=stack_id,
            change_set_id=change_set_id,
        )
        print(
            f"  🔎 preview {Fore.CYAN}change set details{Style.RESET_ALL} at: {console_url}"
        )

    try:
        change_set = better_boto.wait_create_change_set_to_finish(
            bsm=bsm,
            stack_name=stack_name,
            change_set_id=change_set_id,
            delays=change_set_delays,
            timeout=change_set_timeout,
            verbose=verbose,
        )
        if verbose:
            visualize_change_set(
                change_set=change_set,
                bsm=bsm,
                include_nested_stack=plan_nested_stack,
            )
    except TimeoutError as e:  # pragma: no cover
        raise e
    except exc.CreateStackChangeSetButNotChangeError as e:
        print(
            f"    🟡 the submitted information didn't contain changes. "
            f"Submit different information to create a change set."
        )
        return DeployStackResponse()
    except exc.CreateStackChangeSetFailedError as e:  # pragma: no cover
        raise e

    print("    need to execute the change set to apply those changes.")

    if skip_prompt is False:  # pragma: no cover
        if prompt_to_proceed() is False:
            # create logic branch
            if stack is None:
                print("  cancel creation.")
                better_boto.delete_stack(
                    bsm=bsm,
                    stack_name=stack_id,
                )
            else:
                print("  cancel update.")
            return DeployStackResponse()

    if verbose:
        console_url = get_stack_details_console_url(stack_id=stack_id)
        print(
            f"  📋 preview {Fore.CYAN}{execute_message}{Style.RESET_ALL} at: {console_url}"
        )

    better_boto.execute_change_set(
        bsm=bsm,
        change_set_name=change_set_name,
        stack_name=stack_name,
        disable_rollback=disable_rollback,
    )

    # wait until the stack is finished
    if wait:
        better_boto.wait_create_or_update_stack_to_finish(
            bsm=bsm,
            stack_name=stack_id,
            wait_until_exec_stopped=wait_until_exec_stopped_on_failure,
            delays=delays,
            timeout=timeout,
            verbose=verbose,
        )

    return DeployStackResponse(
        is_deploy_happened=True,
        is_create=is_create,
        stack_id=stack_id,
        change_set_id=change_set_id,
    )


def _find_ruler_length(
    name: str,
    padding_length: int,
) -> int:
    if len(name) <= (80 - padding_length):
        return 80
    elif len(name) <= (120 - padding_length):
        return 120
    else:  # pragma: no cover
        return 172


def deploy_stack(
    bsm: "BotoSesManager",
    stack_name: str,
    template: T.Optional[str] = NOTHING,
    use_previous_template: T.Optional[bool] = NOTHING,
    bucket: T.Optional[str] = NOTHING,
    prefix: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_TEMPLATE,
    parameters: T.Optional[T.List[Parameter]] = NOTHING,
    tags: T.Optional[T.Dict[str, str]] = NOTHING,
    execution_role_arn: T.Optional[str] = NOTHING,
    include_iam: T.Optional[bool] = NOTHING,
    include_named_iam: T.Optional[bool] = NOTHING,
    include_macro: T.Optional[bool] = NOTHING,
    stack_policy: T.Optional[str] = NOTHING,
    prefix_stack_policy: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_STACK_POLICY,
    resource_types: T.Optional[T.List[str]] = NOTHING,
    client_request_token: T.Optional[str] = NOTHING,
    enable_termination_protection: T.Optional[bool] = NOTHING,
    disable_rollback: T.Optional[bool] = NOTHING,
    rollback_configuration: T.Optional[dict] = NOTHING,
    notification_arns: T.Optional[T.List[str]] = NOTHING,
    on_failure_do_nothing: T.Optional[bool] = NOTHING,
    on_failure_rollback: T.Optional[bool] = NOTHING,
    on_failure_delete: T.Optional[bool] = NOTHING,
    wait: bool = True,
    delays: T.Union[int, float] = DEFAULT_UPDATE_DELAYS,
    timeout: T.Union[int, float] = DEFAULT_UPDATE_TIMEOUT,
    wait_until_exec_stopped_on_failure: bool = False,
    plan_nested_stack: bool = True,
    skip_plan: bool = False,
    skip_prompt: bool = False,
    change_set_delays: T.Union[int, float] = DEFAULT_CHANGE_SET_DELAYS,
    change_set_timeout: T.Union[int, float] = DEFAULT_CHANGE_SET_TIMEOUT,
    verbose: bool = True,
) -> DeployStackResponse:
    """
    Deploy (create or update) an AWS CloudFormation stack. But more powerful
    than the original boto3 API.

    Deploy Stack related boto3 API:

    - Create Stack Boto3 API: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.create_stack
    - Deploy Stack related boto3 API: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.update_stack

    :param bsm: ``boto_session_manager.BotoSesManager`` object
    :param stack_name: the stack name or unique stack id
    :param template: CloudFormation template JSON or Yaml body in text, or the
        s3 uri pointing to a CloudFormation template file.
    :param use_previous_template: see "Deploy Stack related boto3 API" link
    :param bucket: default None; if given, automatically upload template to S3
        before deployment. see :func:`~aws_cloudformation.better_boto.upload_template_to_s3`
        for more details.
    :param prefix: the s3 prefix where you want to upload the template to
    :param parameters: list of :class:`aws_cloudformation.stack.Parameter` object
    :param tags: key value dictionary for tags
    :param execution_role_arn: see "Deploy Stack related boto3 API" link
    :param include_iam: see "Capacities" part in "Deploy Stack related boto3 API" link
    :param include_named_iam: see "Capacities" part in "Deploy Stack related boto3 API" link
    :param include_macro: see "Capacities" part in "Deploy Stack related boto3 API" link
    :param stack_policy: Stack Policy JSON or Yaml body in text, or the
        s3 uri pointing to a Stack Policy JSON template file.
    :param prefix_stack_policy: see "Deploy Stack related boto3 API" link
    :param resource_types: see "Deploy Stack related boto3 API" link
    :param client_request_token: see "Deploy Stack related boto3 API" link
    :param enable_termination_protection: see "Create Stack Boto3 API" link
    :param disable_rollback: see "Create Stack Boto3 API" link
    :param rollback_configuration: see "Create Stack Boto3 API" link
    :param notification_arns: see "Create Stack Boto3 API" link
    :param on_failure_do_nothing: only used when you create stack directly,
        not using change set. If you set skip_plan = True, then this parameter
        will be ignored.
    :param on_failure_rollback: only used when you create stack directly,
        not using change set.only used when you create stack directly,
        not using change set. If you set skip_plan = True, then this parameter
        will be ignored.
    :param on_failure_delete: only used when you create stack directly,
        not using change set. If you set skip_plan = True, then this parameter
        will be ignored.
    :param wait: default True; if True, then wait the create / update action
        to success or fail; if False, then it is an async call and return immediately;
        note that if you have skip_plan is False (using change set), you always
        have to wait the change set creation to finish.
    :param delays: how long it waits (in seconds) between two
        "describe_stacks" api call to get the stack status
    :param timeout: how long it will raise timeout error
    :param wait_until_exec_stopped_on_failure: if False, it will raise an
        :class:`~aws_cloudformation.exc.DeployStackFailedError` exception immediately
        when there is an error and the stack starting to roll back. Note that
        the stack will take some time to reach stopped status after it failed,
        you may not to run another deploy immediately. if True, it will raise
        the exception after the stack reaching ``stopped`` status.
    :param plan_nested_stack: do you want to plan change set for nested stack?
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
        length = _find_ruler_length(stack_name, 48)
        print_header(
            f"🚀 {Fore.CYAN}Deploy{Style.RESET_ALL} stack: {Fore.CYAN}{stack_name}{Style.RESET_ALL}",
            "=",
            length,
        )
        console_url = get_stacks_view_console_url(stack_name=stack_name)
        print(f"  📋 preview stack in AWS CloudFormation console: {console_url}")

    if skip_plan is True:
        deploy_stack_response = _deploy_stack_without_change_set(
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
            rollback_configuration=rollback_configuration,
            notification_arns=notification_arns,
            on_failure_do_nothing=on_failure_do_nothing,
            on_failure_rollback=on_failure_rollback,
            on_failure_delete=on_failure_delete,
            wait=wait,
            delays=delays,
            timeout=timeout,
            wait_until_exec_stopped_on_failure=wait_until_exec_stopped_on_failure,
            skip_prompt=skip_prompt,
            verbose=verbose,
        )
    else:
        deploy_stack_response = _deploy_stack_using_change_set(
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
            plan_nested_stack=plan_nested_stack,
            wait=wait,
            delays=delays,
            timeout=timeout,
            wait_until_exec_stopped_on_failure=wait_until_exec_stopped_on_failure,
            change_set_delays=change_set_delays,
            change_set_timeout=change_set_timeout,
            skip_prompt=skip_prompt,
            verbose=verbose,
        )

    if verbose:
        print("  done")

    return deploy_stack_response


def remove_stack(
    bsm: "BotoSesManager",
    stack_name: str,
    retain_resources: T.Optional[T.List[str]] = NOTHING,
    role_arn: T.Optional[str] = NOTHING,
    client_request_token: T.Optional[str] = NOTHING,
    wait: bool = True,
    delays: T.Union[int, float] = DEFAULT_UPDATE_DELAYS,
    timeout: T.Union[int, float] = DEFAULT_UPDATE_TIMEOUT,
    wait_until_exec_stopped_on_failure: bool = False,
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
    :param wait_until_exec_stopped_on_failure: if False, it will raise an
        :class:`~aws_cloudformation.exc.DeleteStackFailedError` exception immediately
        when there is an error and the stack starting to roll back. Note that
        the stack will take some time to reach stopped status after it failed,
        you may not to run another deploy immediately. if True, it will raise
        the exception after the stack reaching ``stopped`` status.
    :param skip_prompt: default False; if False, you have to enter "Yes"
        in prompt to do deletion; if True, then execute the deletion directly.
    :param verbose: whether you want to log information to console

    :return: None

    .. versionadded:: 0.1.1
    """
    if verbose:
        length = _find_ruler_length(stack_name, 48)
        print_header(
            f"🗑 {Fore.CYAN}Remove{Style.RESET_ALL} stack {Fore.CYAN}{stack_name}{Style.RESET_ALL}",
            "=",
            length,
        )

        console_url = get_stacks_view_console_url(stack_name)
        print(f"  📋 preview stack in AWS CloudFormation console: {console_url}")

    stack = better_boto.describe_live_stack(bsm, stack_name)

    if stack is None:
        print("  stack doesn't exists!")
        print("  done!")
        return

    if skip_prompt is False:  # pragma: no cover
        if prompt_to_proceed() is False:
            print("Do nothing.")
            return

    better_boto.delete_stack(
        bsm=bsm,
        stack_name=stack_name,
        retain_resources=retain_resources,
        role_arn=role_arn,
        client_request_token=client_request_token,
    )

    if wait:
        better_boto.wait_delete_stack_to_finish(
            bsm=bsm,
            stack_id=stack.id,
            wait_until_exec_stopped=wait_until_exec_stopped_on_failure,
            delays=delays,
            timeout=timeout,
            verbose=verbose,
        )

    if verbose:
        print("  done")


def deploy_stack_set(
    bsm: "BotoSesManager",
    stack_set_name: str,
    template: T.Optional[str] = NOTHING,
    use_previous_template: T.Optional[bool] = NOTHING,
    bucket: T.Optional[str] = NOTHING,
    prefix: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_TEMPLATE,
    description: T.Optional[str] = NOTHING,
    stack_id: T.Optional[str] = NOTHING,
    parameters: T.Optional[T.List[Parameter]] = NOTHING,
    include_iam: T.Optional[bool] = NOTHING,
    include_named_iam: T.Optional[bool] = NOTHING,
    include_macro: T.Optional[bool] = NOTHING,
    tags: T.Optional[T.Dict[str, str]] = NOTHING,
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
    client_request_token: T.Optional[str] = NOTHING,
    managed_execution_active: T.Optional[bool] = NOTHING,
    verbose: bool = True,
) -> T.Tuple[bool, str]:  # pragma: no cover
    """
    Deploy (create or update) an AWS CloudFormation stack set. But more powerful
    than the original boto3 API.

    Deploy StackSet related boto3 API:

    - create_stack_set: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/create_stack_set.html
    - update_stack_set: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/update_stack_set.html

    :param bsm: ``boto_session_manager.BotoSesManager`` object
    :param stack_set_name: the stack set name
    :param template: CloudFormation template JSON or Yaml body in text, or the
        s3 uri pointing to a CloudFormation template file.
    :param use_previous_template:
    :param bucket: default None; if given, automatically upload template to S3
        before deployment. see :func:`~aws_cloudformation.better_boto.upload_template_to_s3`
        for more details.
    :param prefix: the s3 prefix where you want to upload the template to
    :param description: stack set description
    :param stack_id: the stack id you want to import
    :param parameters: list of :class:`aws_cloudformation.stack.Parameter` object
    :param include_iam: see "Capacities" part in "Deploy Stack related boto3 API" link
    :param include_named_iam: see "Capacities" part in "Deploy Stack related boto3 API" link
    :param include_macro: see "Capacities" part in "Deploy Stack related boto3 API" link
    :param tags: key value dictionary for tags
    :param operation_preferences: see "Deploy StackSet related boto3 API" link
    :param admin_role_arn: see "Deploy StackSet related boto3 API" link
    :param execution_role_arn: see "Deploy StackSet related boto3 API" link
    :param deployment_target: see "Deploy StackSet related boto3 API" link
    :param permission_model_is_self_managed: see "Deploy StackSet related boto3 API" link
    :param permission_model_is_service_managed: see "Deploy StackSet related boto3 API" link
    :param auto_deployment_is_enabled: see "Deploy StackSet related boto3 API" link
    :param auto_deployment_retain_stacks_on_account_removal: see "Deploy StackSet related boto3 API" link
    :param operation_id: see "Deploy StackSet related boto3 API" link
    :param accounts: see "Deploy StackSet related boto3 API" link
    :param regions: see "Deploy StackSet related boto3 API" link
    :param call_as_self: see "Deploy StackSet related boto3 API" link
    :param call_as_delegated_admin: see "Deploy StackSet related boto3 API" link
    :param client_request_token: see "Deploy StackSet related boto3 API" link
    :param managed_execution_active: see "Deploy StackSet related boto3 API" link
    :param verbose: whether you want to log information to console

    :return: (is_create, stack_set_id_or_operation_id)
    """
    aws_console = AWSConsole(
        aws_region=bsm.aws_region,
        bsm=bsm,
    )
    if verbose:
        length = _find_ruler_length(stack_set_name, 52)
        print_header(
            f"🚀 {Fore.CYAN}Deploy{Style.RESET_ALL} stack set: {Fore.CYAN}{stack_set_name}{Style.RESET_ALL}",
            "=",
            length,
        )
        console_url = get_filter_stack_set_console_url(
            aws_console=aws_console,
            stack_set_name=stack_set_name,
            call_as_self=call_as_self,
            call_as_delegated_admin=call_as_delegated_admin,
        )
        print(f"  📋 preview stack set in AWS CloudFormation console: {console_url}")

    stack_set = better_boto.describe_stack_set(
        bsm=bsm,
        name=stack_set_name,
        call_as_self=call_as_self,
        call_as_delegated_admin=call_as_delegated_admin,
    )
    if stack_set is None:
        is_create = True
        if verbose:
            print(f"  {Fore.CYAN}+{Style.RESET_ALL} create stack set ...")
        kwargs = dict(
            bsm=bsm,
            stack_set_name=stack_set_name,
            description=description,
            stack_id=stack_id,
            parameters=parameters,
            include_iam=include_iam,
            include_named_iam=include_named_iam,
            include_macro=include_macro,
            tags=tags,
            admin_role_arn=admin_role_arn,
            execution_role_name=execution_role_name,
            permission_model_is_self_managed=permission_model_is_self_managed,
            permission_model_is_service_managed=permission_model_is_service_managed,
            auto_deployment_is_enabled=auto_deployment_is_enabled,
            auto_deployment_retain_stacks_on_account_removal=auto_deployment_retain_stacks_on_account_removal,
            call_as_self=call_as_self,
            call_as_delegated_admin=call_as_delegated_admin,
            client_request_token=client_request_token,
            managed_execution_active=managed_execution_active,
            verbose=verbose,
        )
        resolve_template_kwargs(
            kwargs=kwargs,
            bsm=bsm,
            template=template,
            bucket=bucket,
            prefix=prefix,
            verbose=verbose,
        )
        stack_set_id_or_operation_id = better_boto.create_stack_set(
            **resolve_kwargs(**kwargs)
        )
    else:
        is_create = False
        if verbose:
            print(f"  {Fore.CYAN}+/-{Style.RESET_ALL} update stack set ...")
        kwargs = dict(
            bsm=bsm,
            stack_set_name=stack_set_name,
            description=description,
            use_previous_template=use_previous_template,
            parameters=parameters,
            tags=tags,
            include_iam=include_iam,
            include_named_iam=include_named_iam,
            include_macro=include_macro,
            operation_preferences=operation_preferences,
            admin_role_arn=admin_role_arn,
            execution_role_name=execution_role_name,
            deployment_target=deployment_target,
            permission_model_is_self_managed=permission_model_is_self_managed,
            permission_model_is_service_managed=permission_model_is_service_managed,
            auto_deployment_is_enabled=auto_deployment_is_enabled,
            auto_deployment_retain_stacks_on_account_removal=auto_deployment_retain_stacks_on_account_removal,
            operation_id=operation_id,
            accounts=accounts,
            regions=regions,
            call_as_self=call_as_self,
            call_as_delegated_admin=call_as_delegated_admin,
            managed_execution_active=managed_execution_active,
            verbose=verbose,
        )
        resolve_template_kwargs(
            kwargs=kwargs,
            bsm=bsm,
            template=template,
            bucket=bucket,
            prefix=prefix,
            verbose=verbose,
        )
        stack_set_id_or_operation_id = better_boto.update_stack_set(
            **resolve_kwargs(**kwargs)
        )

    if verbose:
        print("  done")

    return is_create, stack_set_id_or_operation_id


def remove_stack_set(
    bsm: BotoSesManager,
    stack_set_name: str,
    call_as_self: T.Optional[bool] = NOTHING,
    call_as_delegated_admin: T.Optional[bool] = NOTHING,
    verbose: bool = True,
):
    """
    Remove an AWS CloudFormation stack set.

    Delete StackSet related boto3 API:

    - delete_stack_set: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/delete_stack_set.html

    :param bsm: ``boto_session_manager.BotoSesManager`` object
    :param stack_set_name: the stack set name
    :param call_as_self: see "Delete StackSet related boto3 API" link
    :param call_as_delegated_admin: see "Delete StackSet related boto3 API" link
    :param verbose: whether you want to log information to console

    :return: None
    """
    aws_console = AWSConsole(aws_region=bsm.aws_region, bsm=bsm)
    if verbose:
        length = _find_ruler_length(stack_set_name, 52)
        print_header(
            f"🗑 {Fore.CYAN}Remove{Style.RESET_ALL} stack set {Fore.CYAN}{stack_set_name}{Style.RESET_ALL}",
            "=",
            length,
        )
        console_url = get_filter_stack_set_console_url(
            aws_console=aws_console,
            stack_set_name=stack_set_name,
            call_as_self=call_as_self,
            call_as_delegated_admin=call_as_delegated_admin,
        )
        print(f"  📋 preview stack set in AWS CloudFormation console: {console_url}")

    better_boto.delete_stack_set(
        bsm=bsm,
        stack_set_name=stack_set_name,
        call_as_self=call_as_self,
        call_as_delegated_admin=call_as_delegated_admin,
        verbose=verbose,
    )

    if verbose:
        print("  done")
