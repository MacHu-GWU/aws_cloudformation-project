# -*- coding: utf-8 -*-

"""
function in this module is to provide a more user-friendly boto3 API call
without changing the behavior and avoid adding additional feature.
"""

import typing as T
import sys
from datetime import datetime

from boto_session_manager import BotoSesManager, AwsServiceEnum

from . import exc
from . import helper
from .waiter import Waiter
from .stack import (
    StackStatusEnum,
    Parameter,
    Output,
    Stack,
    DriftStatusEnum,
    ChangeSetStatusEnum,
    ChangeSetTypeEnum,
)


def from_describe_stacks(data: dict) -> Stack:
    """
    Create a :class:`~aws_cottonformation.stack.Stack` object from the
    ``describe_stacks`` API response.

    :param data:
    :return:
    """
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
        drift_status=DriftStatusEnum.get_by_name(
            data.get("DriftInformation", dict()).get("StackDriftStatus")
        ),
        drift_last_check_time=data.get("DriftInformation", dict()).get(
            "LastCheckTimestamp"
        ),
    )


def describe_stacks(
    bsm: BotoSesManager,
    name: str,
) -> T.List[Stack]:
    """


    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stacks
    """
    cf_client = bsm.get_client(AwsServiceEnum.CloudFormation)
    paginator = cf_client.get_paginator("describe_stacks")
    response_iterator = paginator.paginate(
        StackName=name,
    )
    try:
        stacks = list()
        for response in response_iterator:
            for data in response.get("Stacks", []):
                stack = from_describe_stacks(data)
                stacks.append(stack)
        return stacks

    except Exception as e:
        if "does not exist" in str(e):
            return []
        else:
            raise e


def describe_live_stack(
    bsm: BotoSesManager,
    name: str,
) -> T.Optional[Stack]:
    """
    Get the detail of given stack (by name), if it not exists, or the existing
    one is a "DELETED" stack, returns None.
    """
    stacks = describe_stacks(bsm, name)
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


DEFAULT_S3_PREFIX_FOR_TEMPLATE = "cloudformation/template"
DEFAULT_S3_PREFIX_FOR_STACK_POLICY = "cloudformation/policy"

# See: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.update_stack
TEMPLATE_BODY_SIZE_LIMIT = 51200
STACK_POLICY_SIZE_LIMIT = 16384

DEFAULT_CHANGE_SET_DELAYS = 5
DEFAULT_CHANGE_SET_TIMEOUT = 60
DEFAULT_UPDATE_DELAYS = 5
DEFAULT_UPDATE_TIMEOUT = 60


def detect_template_type(template: str) -> str:
    """

    :return: "json" or "yaml"
    """
    if template.strip().startswith("{"):
        return "json"
    else:
        return "yaml"


def upload_template_to_s3(
    bsm: BotoSesManager,
    template: str,
    bucket: str,
    prefix: T.Optional[str] = None,
):
    s3_client = bsm.get_client(AwsServiceEnum.S3)
    template_type = detect_template_type(template)
    md5 = helper.md5_of_text(template)
    if prefix:
        if not prefix.endswith("/"):
            prefix = prefix + "/"
    else:
        prefix = ""
    key = f"{prefix}{md5}.{template_type}"
    s3_uri = f"s3://{bucket}/{key}"
    s3_client.put_object(
        Bucket=bucket,
        Key=f"{prefix}{md5}",
        Body=template,
    )
    return s3_uri


def _resolve_template_in_kwargs(
    kwargs: dict,
    bsm: BotoSesManager,
    template: T.Optional[str],
    bucket: T.Optional[str] = None,
    prefix: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_TEMPLATE,
):
    if template.startswith("s3://"):
        kwargs["TemplateURL"] = template

    if bucket is not None:
        s3_uri = upload_template_to_s3(
            bsm,
            template,
            bucket=bucket,
            prefix=prefix,
        )
        kwargs["TemplateURL"] = s3_uri
    elif sys.getsizeof(template) > TEMPLATE_BODY_SIZE_LIMIT:
        raise ValueError(
            f"Template size is larger than {TEMPLATE_BODY_SIZE_LIMIT}B, "
            "You have to upload to s3 bucket first!"
        )
    else:
        kwargs["TemplateBody"] = template


def _resolve_stack_policy(
    kwargs: dict,
    bsm: BotoSesManager,
    stack_policy: str,
    bucket: str,
    prefix: T.Optional[str] = None,
):
    if bucket is not None:
        s3_uri = upload_template_to_s3(
            bsm,
            stack_policy,
            bucket=bucket,
            prefix=prefix,
        )
        kwargs["StackPolicyURL"] = s3_uri
    elif sys.getsizeof(stack_policy) > STACK_POLICY_SIZE_LIMIT:
        raise ValueError(
            f"Stack policy size is larger than {STACK_POLICY_SIZE_LIMIT}B, "
            "You have to upload to s3 bucket first!"
        )
    else:
        kwargs["StackPolicyBody"] = stack_policy


def _resolve_capabilities_kwargs(
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


def _resolve_create_update_common_kwargs(
    kwargs: dict,
    bsm: BotoSesManager,
    execution_role_arn: T.Optional[str] = None,
    parameters: T.List[Parameter] = None,
    tags: dict = None,
    stack_policy: T.Optional[str] = None,
    bucket: T.Optional[str] = None,
    prefix_stack_policy: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_STACK_POLICY,
    include_iam: bool = False,
    include_named_iam: bool = False,
    include_macro: bool = False,
    resource_types: T.Optional[T.List[str]] = None,
    client_request_token: T.Optional[str] = None,
):
    # RoleARN
    if execution_role_arn:
        kwargs["RoleARN"] = execution_role_arn

    # Capabilities
    _resolve_capabilities_kwargs(kwargs, include_iam, include_named_iam, include_macro)

    # StackPolicy
    if stack_policy:
        _resolve_template_in_kwargs(
            kwargs, bsm, stack_policy, bucket, prefix_stack_policy
        )

    # Parameters
    if parameters:
        kwargs["Parameters"] = [param.to_kwargs() for param in parameters]

    # Tags
    if tags:
        kwargs["Tags"] = [dict(Key=key, Value=value) for key, value in tags.items()]

    # ResourceTypes
    if resource_types:
        kwargs["ResourceTypes"] = resource_types

    # ClientRequestToken
    if client_request_token:
        kwargs["ClientRequestToken"] = client_request_token


def create_stack(
    bsm: BotoSesManager,
    stack_name: str,
    template: T.Optional[str],
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
) -> str:
    """
    A wrapper provider more user-friendly API and type hint for
    cloudformation client ``create_stack`` method.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.create_stack

    :param bsm:
    :param stack_name:
    :param template:
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

    :return: stack_id
    """
    kwargs = dict(StackName=stack_name)

    _resolve_create_update_common_kwargs(
        kwargs=kwargs,
        bsm=bsm,
        execution_role_arn=execution_role_arn,
        parameters=parameters,
        tags=tags,
        stack_policy=stack_policy,
        bucket=bucket,
        prefix_stack_policy=prefix_stack_policy,
        include_iam=include_iam,
        include_named_iam=include_named_iam,
        include_macro=include_macro,
        resource_types=resource_types,
        client_request_token=client_request_token,
    )

    # Template
    _resolve_template_in_kwargs(kwargs, bsm, template, bucket, prefix)

    # EnableTerminationProtection
    if enable_termination_protection is not None:
        kwargs["EnableTerminationProtection"] = enable_termination_protection

    cf_client = bsm.get_client(AwsServiceEnum.CloudFormation)
    response = cf_client.create_stack(**kwargs)
    stack_id = response["StackId"]
    return stack_id


def update_stack(
    bsm: BotoSesManager,
    stack_name: str,
    template: T.Optional[str] = None,
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
) -> str:
    """
    A wrapper provider more user-friendly API and type hint for
    cloudformation client ``update_stack`` method.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.update_stack

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
    :param disable_roll_back:

    :return: stack_id
    """
    if (use_previous_template is True) and (template is not None):
        raise ValueError

    kwargs = dict(StackName=stack_name)

    _resolve_create_update_common_kwargs(
        kwargs=kwargs,
        bsm=bsm,
        execution_role_arn=execution_role_arn,
        parameters=parameters,
        tags=tags,
        stack_policy=stack_policy,
        bucket=bucket,
        prefix_stack_policy=prefix_stack_policy,
        include_iam=include_iam,
        include_named_iam=include_named_iam,
        include_macro=include_macro,
        resource_types=resource_types,
        client_request_token=client_request_token,
    )

    # Template
    if use_previous_template is True:
        kwargs["UsePreviousTemplate"] = use_previous_template
    else:
        _resolve_template_in_kwargs(kwargs, bsm, template, bucket, prefix)

    # DisableRollback
    if disable_rollback is not None:
        kwargs["DisableRollback"] = disable_rollback

    cf_client = bsm.get_client(AwsServiceEnum.CloudFormation)
    response = cf_client.update_stack(**kwargs)
    stack_id = response["StackId"]
    return stack_id


def change_set_name_suffix() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3]


def create_change_set(
    bsm: BotoSesManager,
    stack_name: str,
    change_set_name: T.Optional[str] = None,
    template: T.Optional[str] = None,
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
    change_set_type: T.Optional[ChangeSetTypeEnum] = None,
    client_request_token: T.Optional[str] = None,
    disable_rollback: T.Optional[bool] = None,
) -> T.Tuple[str, str, str]:
    """
    A wrapper provider more user-friendly API and type hint for
    cloudformation client ``create_change_set`` method.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.create_change_set

    TODO: add nested stack support

    :param bsm:
    :param stack_name:
    :param change_set_name:
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
    :param change_set_type:
    :param client_request_token:
    :param disable_roll_back:

    :return: stack_id and change_set_id
    """
    if (use_previous_template is True) and (template is not None):
        raise ValueError

    kwargs = dict(
        StackName=stack_name,
    )
    if change_set_name is None:
        change_set_name = f"{stack_name}-{change_set_name_suffix()}"
    kwargs["ChangeSetName"] = change_set_name

    _resolve_create_update_common_kwargs(
        kwargs=kwargs,
        bsm=bsm,
        execution_role_arn=execution_role_arn,
        parameters=parameters,
        tags=tags,
        stack_policy=stack_policy,
        bucket=bucket,
        prefix_stack_policy=prefix_stack_policy,
        include_iam=include_iam,
        include_named_iam=include_named_iam,
        include_macro=include_macro,
        resource_types=resource_types,
        client_request_token=client_request_token,
    )

    # Template
    if use_previous_template is True:
        kwargs["UsePreviousTemplate"] = use_previous_template
    else:
        _resolve_template_in_kwargs(kwargs, bsm, template, bucket, prefix)

    # ChangeSetType
    if change_set_type is not None:
        kwargs["ChangeSetType"] = change_set_type

    # DisableRollback
    if disable_rollback is not None:
        kwargs["DisableRollback"] = disable_rollback

    cf_client = bsm.get_client(AwsServiceEnum.CloudFormation)
    response = cf_client.create_change_set(**kwargs)
    stack_id = response["StackId"]
    change_set_id = response["Id"]
    return stack_id, change_set_id, change_set_name


def describe_change_set(
    bsm: "BotoSesManager",
    change_set_name: str,
    stack_name: T.Optional[str] = None,
) -> dict:
    """
    A wrapper provider more user-friendly API and type hint for
    cloudformation client ``describe_change_set`` method.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_change_set

    :param bsm:
    :param change_set_name:
    :param stack_name:
    :return:
    """
    kwargs = dict(
        ChangeSetName=change_set_name,
    )
    if stack_name is not None:
        kwargs["StackName"] = stack_name
    cf_client = bsm.get_client(AwsServiceEnum.CloudFormation)
    return cf_client.describe_change_set(**kwargs)


def describe_change_set_with_paginator(
    bsm: "BotoSesManager",
    change_set_name: str,
    stack_name: T.Optional[str] = None,
) -> T.Iterable[dict]:
    kwargs = dict(
        ChangeSetName=change_set_name,
    )
    if stack_name is not None:
        kwargs["StackName"] = stack_name
    cf_client = bsm.get_client(AwsServiceEnum.CloudFormation)
    paginator = cf_client.get_paginator("describe_change_set")
    response_iterator = paginator.paginate(**kwargs)
    for response in response_iterator:
        yield response


def execute_change_set(
    bsm: "BotoSesManager",
    change_set_name: str,
    stack_name: T.Optional[str] = None,
    client_request_token: T.Optional[str] = None,
    disable_rollback: T.Optional[bool] = None,
):
    """
    A wrapper provider more user-friendly API and type hint for
    cloudformation client ``execute_change_set`` method.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.execute_change_set

    :param bsm:
    :param change_set_name:
    :param stack_name:
    :param client_request_token:
    :param disable_rollback:
    :return:
    """
    kwargs = dict(ChangeSetName=change_set_name)

    if stack_name is not None:
        kwargs["StackName"] = stack_name
    if client_request_token is not None:
        kwargs["ClientRequestToken"] = client_request_token
    if disable_rollback is not None:
        kwargs["DisableRollback"] = disable_rollback

    cf_client = bsm.get_client(AwsServiceEnum.CloudFormation)
    cf_client.execute_change_set(**kwargs)


def delete_stack(
    bsm: "BotoSesManager",
    stack_name: T.Optional[str] = None,
    retain_resources: T.Optional[T.List[str]] = None,
    role_arn: T.Optional[bool] = None,
    client_request_token: T.Optional[str] = None,
):
    """
    A wrapper provider more user-friendly API and type hint for
    cloudformation client ``delete_stack`` method.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.delete_stack

    :param bsm:
    :param stack_name:
    :param retain_resources:
    :param role_arn:
    :param client_request_token:
    :return:
    """
    kwargs = dict(StackName=stack_name)
    if retain_resources is not None:
        kwargs["RetainResources"] = retain_resources
    if role_arn is not None:
        kwargs["RoleARN"] = role_arn
    if client_request_token is not None:
        kwargs["ClientRequestToken"] = client_request_token
    cf_client = bsm.get_client(AwsServiceEnum.CloudFormation)
    cf_client.delete_stack(**kwargs)


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
    if verbose:
        print("  wait for deploy to finish ...")
    for _ in Waiter(
        delays=delays,
        timeout=timeout,
        indent=4,
        verbose=verbose,
    ):
        stack = describe_live_stack(bsm, stack_name)
        if stack.status.is_stopped():
            if verbose:
                if stack.status.is_success():
                    icon = "🟢"
                else:
                    icon = "🔴"
                print(f"\n    reached status {icon} {stack.status.value!r}")
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
    :param stack_id: the unique stack id
    :param delays: how long it waits (in seconds) between two "get status" api call
    :param timeout: how long it will raise timeout error
    :param verbose: whether you want to log information to console

    :return: Nothing
    """
    if verbose:
        print("  wait for delete to finish ...")
    for _ in Waiter(
        delays=delays,
        timeout=timeout,
        indent=4,
        verbose=verbose,
    ):
        stack = describe_live_stack(bsm, stack_id)
        if stack is None:
            if verbose:
                print(f"\n    already deleted.")
            return
        else:
            if stack.status.is_stopped():
                if verbose:
                    print(f"\n    reached status {stack.status.value}")
            return


def wait_create_change_set_to_finish(
    bsm: "BotoSesManager",
    stack_name: str,
    change_set_id: str,
    delays: T.Union[int, float],
    timeout: T.Union[int, float],
    verbose: bool,
) -> dict:
    """
    You can run this function after you run :func:`create_change_set`. It will
    wait until the change set creation success, fail, or timeout.

    :param bsm:
    :param stack_name:
    :param change_set_id:
    :param delays:
    :param timeout:
    :param verbose:
    :return:
    """
    if verbose:
        print("  wait for change set creation to finish ...")

    for _ in Waiter(
        delays=delays,
        timeout=timeout,
        indent=4,
        verbose=verbose,
    ):
        response = describe_change_set(
            bsm=bsm,
            change_set_name=change_set_id,
            stack_name=stack_name,
        )
        change_set_status = response["Status"]
        if change_set_status in [
            ChangeSetStatusEnum.CREATE_COMPLETE.value,
            ChangeSetStatusEnum.FAILED.value,
        ]:
            if verbose:
                print(f"\n    reached status {change_set_status}")

            if change_set_status == ChangeSetStatusEnum.FAILED.value:
                status_reason = response["StatusReason"]
                if "The submitted information didn't contain changes." in status_reason:
                    raise exc.CreateStackChangeSetButNotChangeError(status_reason)
                else:
                    raise exc.CreateStackChangeSetFailedError(status_reason)

            if bool(response.get("NextToken")) and (
                bool(len(response.get("Changes", [])))
            ):
                changes = list()
                for res in describe_change_set_with_paginator(
                    bsm=bsm,
                    change_set_name=change_set_id,
                    stack_name=stack_name,
                ):
                    changes.extend(res.get("Changes", []))
                res["Changes"] = changes
                return res
            else:
                return response
