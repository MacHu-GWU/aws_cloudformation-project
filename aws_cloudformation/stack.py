# -*- coding: utf-8 -*-

"""
Data model for AWS CloudFormation Stack.
"""

import typing as T
import enum
import dataclasses
from datetime import datetime

from .helper import get_enum_by_name
from .taggings import to_tag_dict


class StackStatusEnum(str, enum.Enum):
    """ """

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
        """ """
        return self in _SUCCESS_STATUS

    def is_failed(self) -> bool:
        """ """
        return self in _FAILED_STATUS

    def is_in_progress(self) -> bool:
        """ """
        return self in _IN_PROGRESS_STATUS

    def is_complete(self) -> bool:
        """ """
        return self in _COMPLETE_STATUS

    def is_stopped(self) -> bool:
        """ """
        return self in _STOPPED_STATUS

    def is_live(self) -> bool:
        """ """
        return not (self in _NOT_LIVE_STATUS)

    @classmethod
    def get_by_name(cls, name: T.Optional[str]) -> T.Optional["StackStatusEnum"]:
        return get_enum_by_name(cls, name)


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


class DriftStatusEnum(str, enum.Enum):
    """ """

    DRIFTED = "DRIFTED"
    IN_SYNC = "IN_SYNC"
    UNKNOWN = "UNKNOWN"
    NOT_CHECKED = "NOT_CHECKED"

    @classmethod
    def get_by_name(cls, name: T.Optional[str]) -> T.Optional["DriftStatusEnum"]:
        return get_enum_by_name(cls, name)


@dataclasses.dataclass
class Stack:
    """ """

    id: str = dataclasses.field()
    name: str = dataclasses.field()
    change_set_id: T.Optional[str] = dataclasses.field(default=None)
    status: T.Optional[StackStatusEnum] = dataclasses.field(default=None)
    description: T.Optional[str] = dataclasses.field(default=None)
    role_arn: T.Optional[str] = dataclasses.field(default=None)
    creation_time: T.Optional[datetime] = dataclasses.field(default=None)
    last_updated_time: T.Optional[datetime] = dataclasses.field(default=None)
    deletion_time: T.Optional[datetime] = dataclasses.field(default=None)
    outputs: T.Dict[str, Output] = dataclasses.field(default_factory=dict)
    params: T.Dict[str, Parameter] = dataclasses.field(default_factory=dict)
    tags: dict = dataclasses.field(default_factory=dict)
    enable_termination_protection: bool = dataclasses.field(default=False)
    parent_id: T.Optional[str] = dataclasses.field(default=None)
    root_id: T.Optional[str] = dataclasses.field(default=None)

    drift_status: T.Optional[DriftStatusEnum] = dataclasses.field(default=None)
    drift_last_check_time: T.Optional[datetime] = dataclasses.field(default=None)

    def is_success(self) -> bool:  # pragma: no cover
        """ """
        return self.status in _SUCCESS_STATUS

    def is_failed(self) -> bool:  # pragma: no cover
        """ """
        return self.status in _FAILED_STATUS

    def is_in_progress(self) -> bool:  # pragma: no cover
        """ """
        return self.status in _IN_PROGRESS_STATUS

    def is_complete(self) -> bool:  # pragma: no cover
        """ """
        return self.status in _COMPLETE_STATUS

    def is_stopped(self) -> bool:  # pragma: no cover
        """ """
        return self.status in _STOPPED_STATUS

    def is_live(self) -> bool:  # pragma: no cover
        """ """
        return not (self.status in _NOT_LIVE_STATUS)

    @classmethod
    def from_describe_stacks_response(cls, data: dict) -> "Stack":
        """
        Create a :class:`~aws_cottonformation.stack.Stack` object from the
        ``describe_stacks`` API response.

        Ref:

        - describe_stacks: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/describe_stacks.html
        """
        drift_status = data.get("DriftInformation", dict()).get("StackDriftStatus")
        if drift_status is not None:
            drift_status = DriftStatusEnum.get_by_name(drift_status)
        return cls(
            id=data["StackId"],
            name=data["StackName"],
            change_set_id=data.get("ChangeSetId"),
            status=StackStatusEnum.get_by_name(data["StackStatus"]),
            description=data.get("Description"),
            role_arn=data.get("RoleARN"),
            creation_time=data.get("CreationTime"),
            last_updated_time=data.get("LastUpdatedTime"),
            deletion_time=data.get("DeletionTime"),
            outputs={
                dct["OutputKey"]: Output(
                    key=dct["OutputKey"],
                    value=dct["OutputValue"],
                    description=dct.get("Description"),
                    export_name=dct.get("ExportName"),
                )
                for dct in data.get("Outputs", [])
            },
            params={
                dct["ParameterKey"]: Parameter(
                    key=dct["ParameterKey"],
                    value=dct["ParameterValue"],
                    use_previous_value=dct.get("UsePreviousValue"),
                    resolved_value=dct.get("ResolvedValue"),
                )
                for dct in data.get("Parameters", [])
            },
            tags={dct["Key"]: dct["Value"] for dct in data.get("Tags", [])},
            enable_termination_protection=data.get("EnableTerminationProtection"),
            parent_id=data.get("ParentId"),
            root_id=data.get("RootId"),
            drift_status=drift_status,
            drift_last_check_time=data.get("DriftInformation", dict()).get(
                "LastCheckTimestamp"
            ),
        )


class ChangeSetStatusEnum(str, enum.Enum):
    """ """

    CREATE_PENDING = "CREATE_PENDING"
    CREATE_IN_PROGRESS = "CREATE_IN_PROGRESS"
    CREATE_COMPLETE = "CREATE_COMPLETE"
    DELETE_PENDING = "DELETE_PENDING"
    DELETE_IN_PROGRESS = "DELETE_IN_PROGRESS"
    DELETE_COMPLETE = "DELETE_COMPLETE"
    DELETE_FAILED = "DELETE_FAILED"
    FAILED = "FAILED"

    @classmethod
    def get_by_name(cls, name: T.Optional[str]) -> T.Optional["ChangeSetStatusEnum"]:
        return get_enum_by_name(cls, name)


class ChangeSetTypeEnum(str, enum.Enum):
    """ """

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    IMPORT = "IMPORT"

    @classmethod
    def get_by_name(cls, name: T.Optional[str]) -> T.Optional["ChangeSetTypeEnum"]:
        return get_enum_by_name(cls, name)


class ChangeSetExecutionStatusEnum(str, enum.Enum):
    """ """

    UNAVAILABLE = "UNAVAILABLE"
    AVAILABLE = "AVAILABLE"
    EXECUTE_IN_PROGRESS = "EXECUTE_IN_PROGRESS"
    EXECUTE_COMPLETE = "EXECUTE_COMPLETE"
    EXECUTE_FAILED = "EXECUTE_FAILED"
    OBSOLETE = "OBSOLETE"

    @classmethod
    def get_by_name(
        cls, name: T.Optional[str]
    ) -> T.Optional["ChangeSetExecutionStatusEnum"]:
        return get_enum_by_name(cls, name)


@dataclasses.dataclass
class ChangeSet:
    """
    Ref:

    - describe_change_set: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/describe_change_set.html
    - list_change_sets: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/list_change_sets.html
    """

    change_set_id: str = dataclasses.field()
    change_set_name: str = dataclasses.field()
    stack_id: str = dataclasses.field()
    stack_name: str = dataclasses.field()
    description: T.Optional[str] = dataclasses.field(default=None)
    params: T.Dict[str, Parameter] = dataclasses.field(default_factory=dict)
    creation_time: T.Optional[datetime] = dataclasses.field(default=None)
    execution_status: T.Optional[ChangeSetExecutionStatusEnum] = dataclasses.field(
        default=None
    )
    status: T.Optional[ChangeSetStatusEnum] = dataclasses.field(default=None)
    status_reason: T.Optional[str] = dataclasses.field(default=None)
    notification_arns: T.Optional[T.List[str]] = dataclasses.field(default=None)
    rollback_configuration: T.Optional[dict] = dataclasses.field(default=None)
    capabilities: T.Optional[T.List[str]] = dataclasses.field(default=None)
    tags: T.Optional[T.Dict[str, str]] = dataclasses.field(default_factory=dict)
    changes: T.Optional[T.List[dict]] = dataclasses.field(default_factory=list)
    include_nested_stacks: T.Optional[bool] = dataclasses.field(default=None)
    next_token: T.Optional[str] = dataclasses.field(default=None)
    parent_change_set_id: T.Optional[str] = dataclasses.field(default=None)
    root_change_set_id: T.Optional[str] = dataclasses.field(default=None)

    def is_status_create_pending(self) -> bool:  # pragma: no cover
        """ """
        return self.status == ChangeSetStatusEnum.CREATE_PENDING.value

    def is_status_create_in_progress(self) -> bool:  # pragma: no cover
        """ """
        return self.status == ChangeSetStatusEnum.CREATE_IN_PROGRESS.value

    def is_status_create_complete(self) -> bool:  # pragma: no cover
        """ """
        return self.status == ChangeSetStatusEnum.CREATE_COMPLETE.value

    def is_status_delete_pending(self) -> bool:  # pragma: no cover
        """ """
        return self.status == ChangeSetStatusEnum.DELETE_PENDING.value

    def is_status_delete_in_progress(self) -> bool:  # pragma: no cover
        """ """
        return self.status == ChangeSetStatusEnum.DELETE_IN_PROGRESS.value

    def is_status_delete_complete(self) -> bool:  # pragma: no cover
        """ """
        return self.status == ChangeSetStatusEnum.DELETE_COMPLETE.value

    def is_status_delete_failed(self) -> bool:  # pragma: no cover
        """ """
        return self.status == ChangeSetStatusEnum.DELETE_FAILED.value

    def is_status_failed(self) -> bool:  # pragma: no cover
        """ """
        return self.status == ChangeSetStatusEnum.FAILED.value

    def is_exec_status_unavailable(self) -> bool:  # pragma: no cover
        """ """
        return self.execution_status == ChangeSetExecutionStatusEnum.UNAVAILABLE.value

    def is_exec_status_available(self) -> bool:  # pragma: no cover
        """ """
        return self.execution_status == ChangeSetExecutionStatusEnum.AVAILABLE.value

    def is_exec_status_execute_in_progress(self) -> bool:  # pragma: no cover
        """ """
        return (
            self.execution_status
            == ChangeSetExecutionStatusEnum.EXECUTE_IN_PROGRESS.value
        )

    def is_exec_status_execute_complete(self) -> bool:  # pragma: no cover
        """ """
        return (
            self.execution_status == ChangeSetExecutionStatusEnum.EXECUTE_COMPLETE.value
        )

    def is_exec_status_execute_failed(self) -> bool:  # pragma: no cover
        """ """
        return (
            self.execution_status == ChangeSetExecutionStatusEnum.EXECUTE_FAILED.value
        )

    def is_exec_status_obsolete(self) -> bool:  # pragma: no cover
        """ """
        return self.execution_status == ChangeSetExecutionStatusEnum.OBSOLETE.value

    @classmethod
    def from_describe_change_set_response(cls, data: dict) -> "ChangeSet":
        """
        Create a :class:`~aws_cottonformation.stack.ChangeSet` object from the
        ``describe_change_set`` API response.

        Ref:

        - describe_change_set: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/describe_change_set.html
        """
        return cls(
            change_set_id=data["ChangeSetId"],
            change_set_name=data["ChangeSetName"],
            stack_id=data["StackId"],
            stack_name=data["StackName"],
            description=data.get("Description"),
            params={
                dct["ParameterKey"]: Parameter(
                    key=dct["ParameterKey"],
                    value=dct["ParameterValue"],
                    use_previous_value=dct.get("UsePreviousValue"),
                    resolved_value=dct.get("ResolvedValue"),
                )
                for dct in data.get("Parameters", [])
            },
            creation_time=data.get("CreationTime"),
            execution_status=ChangeSetExecutionStatusEnum.get_by_name(
                data.get("ExecutionStatus")
            ),
            status=ChangeSetStatusEnum.get_by_name(data.get("Status")),
            status_reason=data.get("StatusReason"),
            notification_arns=data.get("NotificationARNs"),
            rollback_configuration=data.get("RollbackConfiguration"),
            capabilities=data.get("Capabilities"),
            tags=to_tag_dict(data.get("Tags", [])),
            changes=data.get("Changes", []),
            include_nested_stacks=data.get("IncludeNestedStacks"),
        )
