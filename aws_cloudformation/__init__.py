# -*- coding: utf-8 -*-

"""
Expose public API.
"""


from ._version import __version__

__short_description__ = "⭐ AWS CloudFormation deployment for human, Enable terraform plan, terraform apply styled deployment."
__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__github_username__ = "MacHu-GWU"

try:
    from . import better_boto
    from .deploy import (
        deploy_stack,
        remove_stack,
        deploy_stack_set,
    )
    from .stack import (
        StackStatusEnum,
        DriftStatusEnum,
        Parameter,
        Output,
        Stack,
    )
    from .stack_set import (
        StackSetStatusEnum,
        StackSetPermissionModelEnum,
        StackSetCallAsEnum,
        StackSet,
        StackInstanceStatusEnum,
        StackInstanceDetailedStatusEnum,
        StackInstanceDriftStatusEnum,
        StackInstance,
    )
    from .change_set_visualizer import (
        TargetAttributeEnum,
        Target,
        Detail,
        ChangeActionEnum,
        ResourceChange,
        ChangeSet,
    )
except ImportError:  # pragma: no cover
    pass
