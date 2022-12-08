# -*- coding: utf-8 -*-

import typing as T
import enum
import dataclasses
from datetime import datetime


class StackStatusEnum(enum.Enum):
    CREATE_IN_PROGRESS = "CREATE_IN_PROGRESS"
    CREATE_FAILED = "CREATE_FAILED"
    CREATE_COMPLETE = "CREATE_COMPLETE"
    ROLLBACK_IN_PROGRESS = "ROLLBACK_IN_PROGRESS"
    ROLLBACK_FAILED = "ROLLBACK_FAILED"
    ROLLBACK_COMPLETE = "ROLLBACK_COMPLETE"
    DELETE_IN_PROGRESS = "DELETE_IN_PROGRESS"
    DELETE_FAILED = "DELETE_FAILED"
    DELETE_COMPLETE = "DELETE_COMPLETE"
    UPDATE_IN_PROGRESS = "UPDATE_IN_PROGRESS"
    UPDATE_COMPLETE_CLEANUP_IN_PROGRESS = "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS"
    UPDATE_COMPLETE = "UPDATE_COMPLETE"
    UPDATE_FAILED = "UPDATE_FAILED"
    UPDATE_ROLLBACK_IN_PROGRESS = "UPDATE_ROLLBACK_IN_PROGRESS"
    UPDATE_ROLLBACK_FAILED = "UPDATE_ROLLBACK_FAILED"
    UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS = (
        "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS"
    )
    UPDATE_ROLLBACK_COMPLETE = "UPDATE_ROLLBACK_COMPLETE"
    REVIEW_IN_PROGRESS = "REVIEW_IN_PROGRESS"
    IMPORT_IN_PROGRESS = "IMPORT_IN_PROGRESS"
    IMPORT_COMPLETE = "IMPORT_COMPLETE"
    IMPORT_ROLLBACK_IN_PROGRESS = "IMPORT_ROLLBACK_IN_PROGRESS"
    IMPORT_ROLLBACK_FAILED = "IMPORT_ROLLBACK_FAILED"
    IMPORT_ROLLBACK_COMPLETE = "IMPORT_ROLLBACK_COMPLETE"

    def is_success(self) -> bool:
        return self in _SUCCESS_STATUS

    def is_failed(self) -> bool:
        return self in _FAILED_STATUS

    def is_in_progress(self) -> bool:
        return self in _IN_PROGRESS_STATUS

    def is_complete(self) -> bool:
        return self in _COMPLETE_STATUS

    def is_stopped(self) -> bool:
        return self in _STOPPED_STATUS

    def is_live(self) -> bool:
        return not (self in _NOT_LIVE_STATUS)

    @classmethod
    def get_by_name(cls, name: str) -> "StackStatusEnum":
        return cls[name]


_SUCCESS_STATUS: T.Set[StackStatusEnum] = {
    StackStatusEnum.CREATE_COMPLETE,
    StackStatusEnum.DELETE_COMPLETE,
    StackStatusEnum.UPDATE_COMPLETE,
    StackStatusEnum.IMPORT_COMPLETE,
}

_FAILED_STATUS: T.Set[StackStatusEnum] = {
    StackStatusEnum.CREATE_FAILED,
    StackStatusEnum.ROLLBACK_IN_PROGRESS,
    StackStatusEnum.ROLLBACK_FAILED,
    StackStatusEnum.ROLLBACK_COMPLETE,
    StackStatusEnum.DELETE_FAILED,
    StackStatusEnum.UPDATE_FAILED,
    StackStatusEnum.UPDATE_ROLLBACK_IN_PROGRESS,
    StackStatusEnum.UPDATE_ROLLBACK_FAILED,
    StackStatusEnum.UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS,
    StackStatusEnum.UPDATE_ROLLBACK_COMPLETE,
    StackStatusEnum.IMPORT_ROLLBACK_IN_PROGRESS,
    StackStatusEnum.IMPORT_ROLLBACK_FAILED,
    StackStatusEnum.IMPORT_ROLLBACK_COMPLETE,
}

_IN_PROGRESS_STATUS: T.Set[StackStatusEnum] = {
    StackStatusEnum.CREATE_IN_PROGRESS,
    StackStatusEnum.ROLLBACK_IN_PROGRESS,
    StackStatusEnum.DELETE_IN_PROGRESS,
    StackStatusEnum.UPDATE_IN_PROGRESS,
    StackStatusEnum.UPDATE_COMPLETE_CLEANUP_IN_PROGRESS,
    StackStatusEnum.UPDATE_ROLLBACK_IN_PROGRESS,
    StackStatusEnum.UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS,
    StackStatusEnum.REVIEW_IN_PROGRESS,
    StackStatusEnum.IMPORT_IN_PROGRESS,
    StackStatusEnum.IMPORT_ROLLBACK_IN_PROGRESS,
}

_COMPLETE_STATUS: T.Set[StackStatusEnum] = {
    StackStatusEnum.CREATE_COMPLETE,
    StackStatusEnum.ROLLBACK_COMPLETE,
    StackStatusEnum.DELETE_COMPLETE,
    StackStatusEnum.UPDATE_COMPLETE,
    StackStatusEnum.UPDATE_ROLLBACK_COMPLETE,
    StackStatusEnum.IMPORT_COMPLETE,
    StackStatusEnum.IMPORT_ROLLBACK_COMPLETE,
}

_STOPPED_STATUS: T.Set[StackStatusEnum] = {
    StackStatusEnum.CREATE_FAILED,
    StackStatusEnum.ROLLBACK_FAILED,
    StackStatusEnum.DELETE_FAILED,
    StackStatusEnum.UPDATE_FAILED,
    StackStatusEnum.UPDATE_ROLLBACK_FAILED,
    StackStatusEnum.IMPORT_ROLLBACK_FAILED,
    StackStatusEnum.CREATE_COMPLETE,
    StackStatusEnum.ROLLBACK_COMPLETE,
    StackStatusEnum.DELETE_COMPLETE,
    StackStatusEnum.UPDATE_COMPLETE,
    StackStatusEnum.UPDATE_ROLLBACK_COMPLETE,
    StackStatusEnum.IMPORT_COMPLETE,
    StackStatusEnum.IMPORT_ROLLBACK_COMPLETE,
}

_NOT_LIVE_STATUS: T.Set[StackStatusEnum] = {
    StackStatusEnum.DELETE_COMPLETE,
}


@dataclasses.dataclass
class Output:
    """
    Ref:

    - https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html
    """

    key: str = dataclasses.field()
    value: T.Any = dataclasses.field()
    description: T.Optional[str] = dataclasses.field(default=None)
    export_name: T.Optional[str] = dataclasses.field(default=None)


@dataclasses.dataclass
class Parameter:
    """
    Ref:

    - https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html
    """

    key: str = dataclasses.field()
    value: T.Optional[T.Any] = dataclasses.field(default=None)
    use_previous_value: T.Optional[bool] = dataclasses.field(default=None)
    resolved_value: T.Optional[T.Any] = dataclasses.field(default=None)

    def __post_init__(self):
        if (self.use_previous_value is True) and (self.value is not None):
            raise ValueError

    def to_kwargs(self) -> dict:
        dct = dict(ParameterKey=self.key)
        if self.use_previous_value is True:
            dct["UsePreviousValue"] = True
        else:
            dct["ParameterValue"] = self.value
        # todo, add support for SSM ResolvedValue
        return dct


class DriftStatusEnum(enum.Enum):
    DRIFTED = "DRIFTED"
    IN_SYNC = "IN_SYNC"
    UNKNOWN = "UNKNOWN"
    NOT_CHECKED = "NOT_CHECKED"

    @classmethod
    def get_by_name(cls, name: str) -> "DriftStatusEnum":
        return cls[name]


@dataclasses.dataclass
class Stack:
    id: str = dataclasses.field()
    name: str = dataclasses.field()
    change_set_id: T.Optional[str] = dataclasses.field(default=None)
    status: T.Optional[StackStatusEnum] = dataclasses.field(default=None)
    description: T.Optional[str] = dataclasses.field(default=None)
    role_arn: T.Optional[str] = dataclasses.field(default=None)
    creation_time: T.Optional[datetime] = dataclasses.field(default=None)
    last_updated_time: T.Optional[datetime] = dataclasses.field(default=None)
    deletion_time: T.Optional[datetime] = dataclasses.field(default=None)
    outputs: dict = dataclasses.field(default_factory=dict)
    params: dict = dataclasses.field(default_factory=dict)
    tags: dict = dataclasses.field(default_factory=dict)
    enable_termination_protection: bool = dataclasses.field(default=False)
    parent_id: T.Optional[str] = dataclasses.field(default=None)
    root_id: T.Optional[str] = dataclasses.field(default=None)

    drift_status: T.Optional[DriftStatusEnum] = dataclasses.field(default=None)
    drift_last_check_time: T.Optional[datetime] = dataclasses.field(default=None)


class ChangeSetStatusEnum(enum.Enum):
    CREATE_PENDING = "CREATE_PENDING"
    CREATE_IN_PROGRESS = "CREATE_IN_PROGRESS"
    CREATE_COMPLETE = "CREATE_COMPLETE"
    DELETE_PENDING = "DELETE_PENDING"
    DELETE_IN_PROGRESS = "DELETE_IN_PROGRESS"
    DELETE_COMPLETE = "DELETE_COMPLETE"
    DELETE_FAILED = "DELETE_FAILED"
    FAILED = "FAILED"


class ChangeSetTypeEnum(enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    IMPORT = "IMPORT"
