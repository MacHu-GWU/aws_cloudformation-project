# -*- coding: utf-8 -*-

import typing as T
import sys
import dataclasses

from boto_session_manager import BotoSesManager
from func_args import NOTHING
from aws_console_url import AWSConsole

from .console import get_s3_console_url
from .helper import md5_of_text

DEFAULT_S3_PREFIX_FOR_TEMPLATE = "cloudformation/template"
DEFAULT_S3_PREFIX_FOR_STACK_POLICY = "cloudformation/policy"

# See: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.update_stack
TEMPLATE_BODY_SIZE_LIMIT = 51200
STACK_POLICY_SIZE_LIMIT = 16384


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
    verbose: bool = True,
) -> str:
    """
    Upload the CloudFormation template body to S3 before deployment.
    The target location is: s3://${bucket}/${prefix}/${md5_of_template_body}.${json_or_yaml}.

    :param bsm: ``boto_session_manager.BotoSesManager`` object
    :param template: template Body in string
    :param bucket: s3 bucket name
    :param prefix: s3 prefix

    :return: the template url (NOT s3 uri) for the template uploads.
    """
    template_type = detect_template_type(template)
    md5 = md5_of_text(template)
    if prefix:
        if not prefix.endswith("/"):
            prefix = prefix + "/"
    else:
        prefix = ""
    key = f"{prefix}{md5}.{template_type}"
    s3_uri = f"s3://{bucket}/{key}"
    template_url = f"https://s3.amazonaws.com/{bucket}/{key}"
    if verbose:  # pragma: no cover
        print(f"  🪣 upload template to {s3_uri} ...")
        console_url = get_s3_console_url(bucket=bucket, prefix=key)
        print(f"    preview template in AWS S3 console: {console_url}")
    bsm.s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=template,
    )
    return template_url


def resolve_template_kwargs(
    kwargs: dict,
    bsm: BotoSesManager,
    template: T.Optional[str] = NOTHING,
    bucket: T.Optional[str] = NOTHING,
    prefix: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_TEMPLATE,
    verbose: bool = True,
):
    if template is NOTHING:
        return

    if template.startswith("s3://"):
        kwargs["template_url"] = template

    if bucket is not NOTHING:
        template_url = upload_template_to_s3(
            bsm,
            template,
            bucket=bucket,
            prefix=prefix,
            verbose=verbose,
        )
        kwargs["template_url"] = template_url
    elif sys.getsizeof(template) > TEMPLATE_BODY_SIZE_LIMIT:
        raise ValueError(
            f"Template size is larger than {TEMPLATE_BODY_SIZE_LIMIT}B, "
            "You have to upload to s3 bucket first!"
        )
    else:
        kwargs["template_body"] = template


def resolve_stack_policy_kwargs(
    kwargs: dict,
    bsm: BotoSesManager,
    stack_policy: T.Optional[str] = NOTHING,
    bucket: T.Optional[str] = None,
    prefix: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_STACK_POLICY,
    verbose: bool = True,
):
    if stack_policy is NOTHING:
        return

    if bucket is not NOTHING:
        policy_url = upload_template_to_s3(
            bsm,
            stack_policy,
            bucket=bucket,
            prefix=prefix,
            verbose=verbose,
        )
        kwargs["stack_policy_url"] = policy_url
    elif sys.getsizeof(stack_policy) > STACK_POLICY_SIZE_LIMIT:
        raise ValueError(
            f"Stack policy size is larger than {STACK_POLICY_SIZE_LIMIT}B, "
            "You have to upload to s3 bucket first!"
        )
    else:
        kwargs["stack_policy_body"] = stack_policy
