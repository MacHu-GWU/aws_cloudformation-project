# -*- coding: utf-8 -*-

"""
function in this module is to provide a more user-friendly boto3 API call
without changing the behavior and avoid adding additional feature.
It is the low level api for the :mod:`aws_cloudformation.deploy` module.

Design Principle:

- native boto3 API should NOT have verbose argument
- custom waiter could have verbose argument
"""

from .stacks import StackIterProxy
from .stacks import describe_stacks
from .stacks import describe_live_stack
from .stacks import create_stack
from .stacks import update_stack
from .stacks import create_change_set
from .stacks import describe_change_set
from .stacks import describe_change_set_with_paginator
from .stacks import execute_change_set
from .stacks import delete_stack
from .stacks import wait_create_or_update_stack_to_finish
from .stacks import wait_delete_stack_to_finish
from .stacks import wait_create_change_set_to_finish
from .stacksets import describe_stack_set
from .stacksets import create_stack_set
from .stacksets import update_stack_set
from .stacksets import delete_stack_set
from .stacksets import describe_stack_instance
from .stacksets import create_stack_instances
from .stacksets import update_stack_instances
from .stacksets import delete_stack_instances
from .stacksets import StackInstanceIterProxy
from .stacksets import list_stack_instances
from .stacksets import wait_deploy_stack_instances_to_stop
