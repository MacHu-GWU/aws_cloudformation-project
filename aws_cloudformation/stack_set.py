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
    """
    """
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"

    @classmethod
    def get_by_name(cls, name: T.Optional[str]) -> T.Optional["StackSetStatusEnum"]:
        return get_enum_by_name(cls, name)


class StackSetPermissionModelEnum(str, enum.Enum):
    """
    """
    SERVICE_MANAGED = "SERVICE_MANAGED"
    SELF_MANAGED = "SELF_MANAGED"

    @classmethod
    def get_by_name(
        cls, name: T.Optional[str]
    ) -> T.Optional["StackSetPermissionModelEnum"]:
        return get_enum_by_name(cls, name)


class StackSetCallAsEnum(str, enum.Enum):
    """
    """
    SELF = "SELF"
    DELEGATED_ADMIN = "DELEGATED_ADMIN"

    @classmethod
    def get_by_name(cls, name: T.Optional[str]) -> T.Optional["StackSetCallAsEnum"]:
        return get_enum_by_name(cls, name)


@dataclasses.dataclass
class StackSet:
    """
    """
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

    @property
    def is_status_active(self) -> bool:
        """
        """
        return self.status == StackSetStatusEnum.ACTIVE.value

    @property
    def is_status_deleted(self) -> bool:
        """
        """
        return self.status == StackSetStatusEnum.DELETED.value

    @property
    def is_self_managed(self) -> bool:
        """
        """
        return self.permission_model == StackSetPermissionModelEnum.SELF_MANAGED.value

    @property
    def is_service_managed(self) -> bool:
        """
        """
        return (
            self.permission_model == StackSetPermissionModelEnum.SERVICE_MANAGED.value
        )


class StackInstanceStatusEnum(str, enum.Enum):
    """
    """
    CURRENT = "CURRENT"
    OUTDATED = "OUTDATED"
    INOPERABLE = "INOPERABLE"

    @classmethod
    def get_by_name(
        cls, name: T.Optional[str]
    ) -> T.Optional["StackInstanceStatusEnum"]:
        return get_enum_by_name(cls, name)


class StackInstanceDetailedStatusEnum(str, enum.Enum):
    """
    """
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    INOPERABLE = "INOPERABLE"

    @classmethod
    def get_by_name(
        cls, name: T.Optional[str]
    ) -> T.Optional["StackInstanceDetailedStatusEnum"]:
        return get_enum_by_name(cls, name)


class StackInstanceDriftStatusEnum(str, enum.Enum):
    """
    """
    DRIFTED = "DRIFTED"
    IN_SYNC = "IN_SYNC"
    UNKNOWN = "UNKNOWN"
    NOT_CHECKED = "NOT_CHECKED"

    @classmethod
    def get_by_name(
        cls, name: T.Optional[str]
    ) -> T.Optional["StackInstanceDriftStatusEnum"]:
        return get_enum_by_name(cls, name)


@dataclasses.dataclass
class StackInstance:
    """
    """
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

    def is_status_current(self) -> bool:
        """
        """
        return self.status == StackInstanceStatusEnum.CURRENT.value

    def is_status_outdated(self) -> bool:
        """
        """
        return self.status == StackInstanceStatusEnum.OUTDATED.value

    def is_status_inoperable(self) -> bool:
        """
        """
        return self.status == StackInstanceStatusEnum.INOPERABLE.value

    @property
    def detailed_status(self) -> T.Optional[StackInstanceDetailedStatusEnum]:
        """
        """
        return StackInstanceDetailedStatusEnum.get_by_name(
            self.statck_instance_status.get("DetailedStatus")
        )

    def is_detailed_status_pending(self) -> bool:
        """
        """
        return self.detailed_status == StackInstanceDetailedStatusEnum.PENDING.value

    def is_detailed_status_running(self) -> bool:
        """
        """
        return self.detailed_status == StackInstanceDetailedStatusEnum.RUNNING.value

    def is_detailed_status_succeeded(self) -> bool:
        """
        """
        return self.detailed_status == StackInstanceDetailedStatusEnum.SUCCEEDED.value

    def is_detailed_status_failed(self) -> bool:
        """
        """
        return self.detailed_status == StackInstanceDetailedStatusEnum.FAILED.value

    def is_detailed_status_cancelled(self) -> bool:
        """
        """
        return self.detailed_status == StackInstanceDetailedStatusEnum.CANCELLED.value

    def is_detailed_status_inoperable(self) -> bool:
        """
        """
        return self.detailed_status == StackInstanceDetailedStatusEnum.INOPERABLE.value
