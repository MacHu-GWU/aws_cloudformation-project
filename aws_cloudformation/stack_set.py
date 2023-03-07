# -*- coding: utf-8 -*-

"""
Data model for AWS CloudFormation StackSet.
"""

import typing as T
import enum
import dataclasses
from datetime import datetime


from .helper import get_enum_by_name
from .stack import (
    Parameter,
)


class StackSetStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"

    @classmethod
    def get_by_name(cls, name: T.Optional[str]) -> "StackSetStatusEnum":
        return get_enum_by_name(cls, name)


class StackSetPermissionModelEnum(str, enum.Enum):
    SERVICE_MANAGED = "SERVICE_MANAGED"
    SELF_MANAGED = "SELF_MANAGED"

    @classmethod
    def get_by_name(cls, name: T.Optional[str]) -> "StackSetPermissionModelEnum":
        return get_enum_by_name(cls, name)


class StackSetCallAsEnum(str, enum.Enum):
    SELF = "SELF"
    DELEGATED_ADMIN = "DELEGATED_ADMIN"

    @classmethod
    def get_by_name(cls, name: T.Optional[str]) -> "StackSetCallAsEnum":
        return get_enum_by_name(cls, name)


@dataclasses.dataclass
class StackSet:
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    arn: str = dataclasses.field()
    description: T.Optional[str] = dataclasses.field(default=None)
    status: T.Optional[StackSetStatusEnum] = dataclasses.field(default=None)
    template_body: T.Optional[str] = dataclasses.field(default=None)
    params: T.Dict[str, Parameter] = dataclasses.field(default_factory=dict)
    admin_role_arn: T.Optional[str] = dataclasses.field(default=None)
    execution_role_name: T.Optional[str] = dataclasses.field(default=None)
    permission_model: T.Optional[str] = dataclasses.field(default=None)
    org_unit_ids: T.List[str] = dataclasses.field(default_factory=list)
    auto_deployment: dict = dataclasses.field(default_factory=dict)
    managed_execution: dict = dataclasses.field(default_factory=dict)
    regions: T.List[str] = dataclasses.field(default_factory=list)


class StackInstanceStatusEnum(str, enum.Enum):
    CURRENT = "CURRENT"
    OUTDATED = "OUTDATED"
    INOPERABLE = "INOPERABLE"

    @classmethod
    def get_by_name(cls, name: T.Optional[str]) -> "StackInstanceStatusEnum":
        return get_enum_by_name(cls, name)


class DetailedStackInstanceStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    INOPERABLE = "INOPERABLE"

    @classmethod
    def get_by_name(cls, name: T.Optional[str]) -> "DetailedStackInstanceStatusEnum":
        return get_enum_by_name(cls, name)


class StackInstanceDriftStatusEnum(str, enum.Enum):
    DRIFTED = "DRIFTED"
    IN_SYNC = "IN_SYNC"
    UNKNOWN = "UNKNOWN"
    NOT_CHECKED = "NOT_CHECKED"

    @classmethod
    def get_by_name(cls, name: T.Optional[str]) -> "StackInstanceDriftStatusEnum":
        return get_enum_by_name(cls, name)


@dataclasses.dataclass
class StackInstance:
    stack_set_id: str = dataclasses.field()
    stack_id: str = dataclasses.field()
    aws_region: str = dataclasses.field()
    aws_account_id: str = dataclasses.field()
    param_overrides: T.Dict[str, Parameter] = dataclasses.field(default_factory=dict)
    status: T.Optional[StackInstanceStatusEnum] = dataclasses.field(default=None)
    statck_instance_status: dict = dataclasses.field(default_factory=dict)
    status_reason: T.Optional[str] = dataclasses.field(default=None)
    org_unit_id: T.Optional[str] = dataclasses.field(default=None)
    drift_status: T.Optional[StackInstanceDriftStatusEnum] = dataclasses.field(
        default=None
    )
    last_drift_check_timestamp: T.Optional[datetime] = dataclasses.field(default=None)
    last_operation_id: T.Optional[str] = dataclasses.field(default=None)
