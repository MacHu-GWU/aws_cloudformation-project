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


def get_change_set_console_url(
    stack_id: str,
    change_set_id: str
) -> str:
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