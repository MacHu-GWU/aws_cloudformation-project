# -*- coding: utf-8 -*-

"""
Expose public API.
"""


from ._version import __version__

__short_description__ = "A user-friendly AWS CloudFormation API"
__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__github_username__ = "MacHu-GWU"

try:
    from .deploy import (
        deploy_stack,
        remove_stack,
    )
except ImportError:  # pragma: no cover
    pass
