# -*- coding: utf-8 -*-

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


def get_stacks_detail_console_url(
    stack_name: T.Optional[str] = None,
    stack_id: T.Optional[str] = None,
    active_only: bool = False,
    deleted_only: bool = False,
) -> str:
    """

    :param stack_name:
    :param stack_id: full ARN
    :param active_only:
    :param deleted_only:
    :return:
    """
    flag_count = sum([stack_name is None, stack_id is None])
    if flag_count != 1:  # pragma: no cover
        raise ValueError

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

    if stack_name is not None:
        return f"https://console.aws.amazon.com/cloudformation/home?#/stacks?filteringText={stack_name}&viewNested=true&hideStacks=false&stackId=&filteringStatus={filtering_status}"
    elif stack_id is not None:
        aws_account_id, aws_region, stack_name, uuid = parse_stack_id(stack_id)
        return f"https://{aws_region}.console.aws.amazon.com/cloudformation/home?region={aws_region}#/stacks/stackinfo?filteringText={stack_name}&viewNested=true&hideStacks=false&stackId={stack_id}&filteringStatus={filtering_status}"
    else:  # pragma: no cover
        raise NotImplementedError
