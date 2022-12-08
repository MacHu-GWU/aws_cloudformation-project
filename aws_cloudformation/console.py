# -*- coding: utf-8 -*-

import enum
import typing as T


def parse_stack_id(stack_id) -> T.Tuple[str, str, str, str]:
    """

    :param stack_id: full ARN

    :return: aws_account_id, aws_region, stack_name, uuid
    """
    chunks = stack_id.split(":")
    aws_account_id = chunks[4]
    aws_region = chunks[3]
    chunks = stack_id.split("/")
    stack_name = chunks[1]
    uuid = chunks[2]
    return aws_account_id, aws_region, stack_name, uuid


def get_stacks_view_console_url(
    stack_name: T.Optional[str] = None,
    aws_region: T.Optional[str] = None,
) -> str:
    """

    :param stack_name:
    :param aws_region:
    :return:
    """
    if stack_name is None:
        filtering_text = ""
    else:
        filtering_text = stack_name

    if aws_region is None:
        token1 = ""
        token2 = ""
    else:
        token1 = f"{aws_region}."
        token2 = f"region={aws_region}"

    return (
        f"https://{token1}console.aws.amazon.com/cloudformation/home?{token2}#/stacks?"
        f"filteringStatus=active"
        f"&filteringText={filtering_text}"
        f"&viewNested=true"
        f"&hideStacks=false"
    )


class ConsoleHrefEnum(enum.Enum):
    stack_info = "stackinfo"
    events = "events"
    resources = "resources"
    outputs = "outputs"
    parameters = "parameters"
    template = "template"
    changesets = "changesets"


def get_stack_details_console_url(
    stack_id: str = None,
    active_only: bool = False,
    deleted_only: bool = False,
    href: T.Optional[str] = None,
) -> str:
    """

    :param stack_id: full ARN
    :param active_only:
    :param deleted_only:
    :param href:

    :return:
    """
    flag_count = sum([active_only, deleted_only])
    if flag_count == 0:
        active_only = True
    elif flag_count != 1:  # pragma: no cover
        raise ValueError
    if active_only:
        filtering_status = "active"
    elif deleted_only:  # pragma: no cover
        filtering_status = "deleted"
    else:  # pragma: no cover
        raise NotImplementedError

    if href is None:
        href = ConsoleHrefEnum.stack_info.value

    aws_account_id, aws_region, stack_name, uuid = parse_stack_id(stack_id)
    return (
        f"https://{aws_region}.console.aws.amazon.com/cloudformation/home?"
        f"region={aws_region}#/stacks/{href}?"
        f"filteringText={stack_name}"
        f"&viewNested=true"
        f"&hideStacks=false"
        f"&stackId={stack_id}"
        f"&filteringStatus={filtering_status}"
    )


def get_change_set_console_url(stack_id: str, change_set_id: str) -> str:
    """

    :param stack_id:
    :param change_set_id:
    :return:
    """
    _, aws_region, _, _ = parse_stack_id(stack_id)
    return (
        f"https://{aws_region}.console.aws.amazon.com/cloudformation/home?"
        f"region={aws_region}#/stacks/changesets/changes?"
        f"stackId={stack_id}"
        f"&changeSetId={change_set_id}"
    )


def split_s3_uri(
    s3_uri: str,
) -> T.Tuple[str, str]:  # pragma: no cover
    """
    Split AWS S3 URI, returns bucket and key.

    :param s3_uri: example, ``"s3://my-bucket/my-folder/data.json"``
    """
    parts = s3_uri.split("/")
    bucket = parts[2]
    key = "/".join(parts[3:])
    return bucket, key


def get_s3_console_url(
    bucket: T.Optional[str] = None,
    prefix: T.Optional[str] = None,
    s3_uri: T.Optional[str] = None,
    is_us_gov_cloud: bool = False,
) -> str:  # pragma: no cover
    """
    Return an AWS Console url that you can use to open it in your browser.

    :param bucket: example, ``"my-bucket"``
    :param prefix: example, ``"my-folder/"``
    :param s3_uri: example, ``"s3://my-bucket/my-folder/data.json"``
    :param is_us_gov_cloud: whether it is a gov cloud

    Example::
        >>> get_s3_console_url(s3_uri="s3://my-bucket/my-folder/data.json")
        https://s3.console.aws.amazon.com/s3/object/my-bucket?prefix=my-folder/data.json
    """
    if s3_uri is None:
        if not ((bucket is not None) and (prefix is not None)):
            raise ValueError
    else:
        if not ((bucket is None) and (prefix is None)):
            raise ValueError
        bucket, prefix = split_s3_uri(s3_uri)

    if len(prefix) == 0:
        return "https://console.aws.amazon.com/s3/buckets/{}?tab=objects".format(
            bucket,
        )
    elif prefix.endswith("/"):
        s3_type = "buckets"
    else:
        s3_type = "object"

    if is_us_gov_cloud:
        endpoint = "console.amazonaws-us-gov.com"
    else:
        endpoint = "console.aws.amazon.com"

    return "https://{endpoint}/s3/{s3_type}/{bucket}?prefix={prefix}".format(
        endpoint=endpoint, s3_type=s3_type, bucket=bucket, prefix=prefix
    )
