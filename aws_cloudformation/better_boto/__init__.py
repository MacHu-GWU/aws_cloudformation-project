# -*- coding: utf-8 -*-

"""
function in this module is to provide a more user-friendly boto3 API call
without changing the behavior and avoid adding additional feature.
"""

from .stacks import (
    describe_stacks,
    describe_live_stack,
    DEFAULT_S3_PREFIX_FOR_TEMPLATE,
    DEFAULT_S3_PREFIX_FOR_STACK_POLICY,
    TEMPLATE_BODY_SIZE_LIMIT,
    STACK_POLICY_SIZE_LIMIT,
    DEFAULT_CHANGE_SET_DELAYS,
    DEFAULT_CHANGE_SET_TIMEOUT,
    DEFAULT_UPDATE_DELAYS,
    DEFAULT_UPDATE_TIMEOUT,
    detect_template_type,
    upload_template_to_s3,
    create_stack,
    update_stack,
    change_set_name_suffix,
    create_change_set,
    describe_change_set,
    describe_change_set_with_paginator,
    execute_change_set,
    delete_stack,
    wait_create_or_update_stack_to_finish,
    wait_delete_stack_to_finish,
    wait_create_change_set_to_finish,
)

from .stacksets import (
    describe_stack_set,
    create_stack_set,
    update_stack_set,
    delete_stack_set,
    describe_stack_instance,
    create_stack_instances,
    update_stack_instances,
    delete_stack_instances,
    list_stack_instances,
)

from .taggings_helper import (
    to_tag_list,
    to_tag_dict,
)
