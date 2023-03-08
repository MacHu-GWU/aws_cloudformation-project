# -*- coding: utf-8 -*-

import typing as T


def to_tag_list(tags: T.Dict[str, str]) -> T.List[T.Dict[str, str]]:
    """
    Example:

        >>> to_tag_list({"foo": "bar"})
        [{'Key': 'foo', 'Value': 'bar'}]
    """
    return [dict(Key=k, Value=v) for k, v in tags.items()]


def to_tag_dict(tags: T.List[T.Dict[str, str]]) -> T.Dict[str, str]:
    """
    Example:

        >>> to_tag_dict([{"Key": "foo", "Value": 'bar'}])
        {'foo': 'bar'}
    """
    return {dct["Key"]: dct["Value"] for dct in tags}
