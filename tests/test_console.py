# -*- coding: utf-8 -*-

from aws_cloudformation.console import (
    parse_stack_id,
    get_stacks_view_console_url,
    get_stack_details_console_url,
    get_change_set_console_url,
    ConsoleHrefEnum,
)


def test_parse_stack_id():
    stack_id = "arn:aws:cloudformation:us-east-1:111122223333:stack/cottonformation-stack/a517e0f0-750b-16ed-859b-1248b06dcab3"
    aws_account_id, aws_region, stack_name, uuid = parse_stack_id(stack_id)
    assert aws_account_id == "111122223333"
    assert aws_region == "us-east-1"
    assert stack_name == "cottonformation-stack"
    assert uuid == "a517e0f0-750b-16ed-859b-1248b06dcab3"


def test_get_stacks_view_console_url():
    console_url = get_stacks_view_console_url()
    # print(console_url)

    console_url = get_stacks_view_console_url(stack_name="CDKToolkit")
    # print(console_url)

    console_url = get_stacks_view_console_url(
        stack_name="CDKToolkit", aws_region="us-east-1"
    )
    # print(console_url)


def test_get_stack_details_console_url():
    console_url = get_stack_details_console_url(
        stack_id="arn:aws:cloudformation:us-east-1:669508176277:stack/CDKToolkit/b518e0f0-750b-11ed-859b-1208b06dceb3"
    )
    # print(console_url)

    console_url = get_stack_details_console_url(
        stack_id="arn:aws:cloudformation:us-east-1:669508176277:stack/CDKToolkit/b518e0f0-750b-11ed-859b-1208b06dceb3",
        href=ConsoleHrefEnum.resources.value,
    )
    # print(console_url)


def test_get_change_set_console_url():
    console_url = get_change_set_console_url(
        stack_id="arn:aws:cloudformation:us-east-1:669508176277:stack/cottonformation-deploy-stack-test/b6400b70-7682-11ed-962e-0a1f3286c49d",
        change_set_id="arn:aws:cloudformation:us-east-1:669508176277:changeSet/cottonformation-deploy-stack-test-2022-12-07-23-32-23-124/3b20fb80-3a95-400f-ae93-c357c16daf57",
    )
    # print(console_url)


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.console", preview=False)
