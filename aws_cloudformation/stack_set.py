# -*- coding: utf-8 -*-

"""
Data model for AWS CloudFormation StackSet.
"""

import typing as T
import enum
import dataclasses
from datetime import datetime

import aws_console_url

from .helper import get_enum_by_name
from .stack import (
    Parameter,
)


class StackSetStatusEnum(str, enum.Enum):
    """ """

    ACTIVE = "ACTIVE"
    DELETED = "DELETED"

    @classmethod
    def get_by_name(cls, name: T.Optional[str]) -> T.Optional["StackSetStatusEnum"]:
        return get_enum_by_name(cls, name)


class StackSetPermissionModelEnum(str, enum.Enum):
    """ """

    SERVICE_MANAGED = "SERVICE_MANAGED"
    SELF_MANAGED = "SELF_MANAGED"

    @classmethod
    def get_by_name(
        cls, name: T.Optional[str]
    ) -> T.Optional["StackSetPermissionModelEnum"]:
        return get_enum_by_name(cls, name)


class StackSetCallAsEnum(str, enum.Enum):
    """ """

    SELF = "SELF"
    DELEGATED_ADMIN = "DELEGATED_ADMIN"

    @classmethod
    def get_by_name(cls, name: T.Optional[str]) -> T.Optional["StackSetCallAsEnum"]:
        return get_enum_by_name(cls, name)


@dataclasses.dataclass
class StackSet:
    """ """

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
    def is_status_active(self) -> bool:  # pragma: no cover
        """ """
        return self.status == StackSetStatusEnum.ACTIVE.value

    @property
    def is_status_deleted(self) -> bool:  # pragma: no cover
        """ """
        return self.status == StackSetStatusEnum.DELETED.value

    @property
    def is_self_managed(self) -> bool:  # pragma: no cover
        """ """
        return self.permission_model == StackSetPermissionModelEnum.SELF_MANAGED.value

    @property
    def is_service_managed(self) -> bool:  # pragma: no cover
        """ """
        return (
            self.permission_model == StackSetPermissionModelEnum.SERVICE_MANAGED.value
        )

    @classmethod
    def from_arn(cls, arn: str) -> "StackSet":
        """ """
        stack_set = aws_console_url.aws_resource.CloudFormationStackSet.from_arn(arn)
        return cls(
            id=stack_set.stack_set_id,
            name=stack_set.name,
            arn=stack_set.arn
        )

    @classmethod
    def from_describe_stack_set_response(cls, data: dict) -> "StackSet":
        """
        Create a :class:`~aws_cottonformation.stack_set.StackSet` object from the
        ``describe_stack_set()`` or ``list_stack_sets()`` API response.

        Ref:

        - describe_stack_set: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/describe_stack_set.html
        - list_stack_sets: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/list_stack_sets.html
        """
        return cls(
            id=data["StackSetId"],
            name=data["StackSetName"],
            arn=data["StackSetARN"],
            description=data.get("Description"),
            status=StackSetStatusEnum.get_by_name(data.get("Status")),
            template_body=data.get("TemplateBody"),
            params={
                dct["ParameterKey"]: Parameter(
                    key=dct["ParameterKey"],
                    value=dct["ParameterValue"],
                    use_previous_value=dct.get("UsePreviousValue"),
                    resolved_value=dct.get("ResolvedValue"),
                )
                for dct in data.get("Parameters", [])
            },
            admin_role_arn=data.get("AdministrationRoleARN"),
            execution_role_name=data.get("ExecutionRoleName"),
            permission_model=StackSetPermissionModelEnum.get_by_name(
                data.get("PermissionModel")
            ),
            org_unit_ids=data.get("OrganizationalUnitIds", []),
            auto_deployment=data.get("AutoDeployment", {}),
            managed_execution=data.get("ManagedExecution"),
            regions=data.get("Regions", []),
        )

    @property
    def aws_region(self) -> str:
        return self.arn.split(":")[3]

    @property
    def aws_account_id(self) -> str:
        return self.arn.split(":")[4]

    @property
    def console_url(self) -> str:
        aws_console = aws_console_url.AWSConsole(aws_region=self.aws_region)
        return aws_console.cloudformation.get_stack_set_info(
            name_or_id_or_arn=self.arn,
            is_self_managed=self.is_self_managed,
            is_service_managed=self.is_service_managed,
        )


class StackInstanceStatusEnum(str, enum.Enum):
    """ """

    CURRENT = "CURRENT"
    OUTDATED = "OUTDATED"
    INOPERABLE = "INOPERABLE"

    @classmethod
    def get_by_name(
        cls, name: T.Optional[str]
    ) -> T.Optional["StackInstanceStatusEnum"]:
        return get_enum_by_name(cls, name)


class StackInstanceDetailedStatusEnum(str, enum.Enum):
    """ """

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
    """ """

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
    """ """

    stack_set_id: str = dataclasses.field()
    aws_region: str = dataclasses.field()
    aws_account_id: str = dataclasses.field()
    stack_id: T.Optional[str] = dataclasses.field(default=None)
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

    def is_status_current(self) -> bool:  # pragma: no cover
        """ """
        return self.status == StackInstanceStatusEnum.CURRENT.value

    def is_status_outdated(self) -> bool:  # pragma: no cover
        """ """
        return self.status == StackInstanceStatusEnum.OUTDATED.value

    def is_status_inoperable(self) -> bool:  # pragma: no cover
        """ """
        return self.status == StackInstanceStatusEnum.INOPERABLE.value

    @property
    def detailed_status(self) -> T.Optional[StackInstanceDetailedStatusEnum]:
        """ """
        return StackInstanceDetailedStatusEnum.get_by_name(
            self.statck_instance_status.get("DetailedStatus")
        )

    def is_detailed_status_pending(self) -> bool:  # pragma: no cover
        """ """
        return self.detailed_status == StackInstanceDetailedStatusEnum.PENDING.value

    def is_detailed_status_running(self) -> bool:  # pragma: no cover
        """ """
        return self.detailed_status == StackInstanceDetailedStatusEnum.RUNNING.value

    def is_detailed_status_succeeded(self) -> bool:  # pragma: no cover
        """ """
        return self.detailed_status == StackInstanceDetailedStatusEnum.SUCCEEDED.value

    def is_detailed_status_failed(self) -> bool:  # pragma: no cover
        """ """
        return self.detailed_status == StackInstanceDetailedStatusEnum.FAILED.value

    def is_detailed_status_cancelled(self) -> bool:  # pragma: no cover
        """ """
        return self.detailed_status == StackInstanceDetailedStatusEnum.CANCELLED.value

    def is_detailed_status_inoperable(self) -> bool:  # pragma: no cover
        """ """
        return self.detailed_status == StackInstanceDetailedStatusEnum.INOPERABLE.value

    @classmethod
    def from_describe_stack_instance_response(cls, data: dict) -> "StackInstance":
        """
        Create a :class:`~aws_cottonformation.stack_set.StackInstance` object from the
        ``describe_stack_instance()`` or ``list_stack_instances()`` API response.

        Ref:

        - describe_stack_instance: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/describe_stack_instance.html
        - list_stack_instances: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation/client/list_stack_instances.html
        """
        return cls(
            stack_set_id=data["StackSetId"],
            aws_region=data["Region"],
            aws_account_id=data["Account"],
            stack_id=data.get("StackId"),
            param_overrides={
                dct["ParameterKey"]: Parameter(
                    key=dct["ParameterKey"],
                    value=dct["ParameterValue"],
                    use_previous_value=dct.get("UsePreviousValue"),
                    resolved_value=dct.get("ResolvedValue"),
                )
                for dct in data.get("ParameterOverrides", [])
            },
            status=StackInstanceStatusEnum.get_by_name(data.get("Status")),
            statck_instance_status=data.get("StackInstanceStatus", {}),
            status_reason=data.get("StatusReason"),
            org_unit_id=data.get("OrganizationalUnitId"),
            drift_status=StackInstanceDriftStatusEnum.get_by_name(
                data.get("DriftStatus")
            ),
            last_drift_check_timestamp=data.get("LastDriftCheckTimestamp"),
            last_operation_id=data.get("LastOperationId"),
        )

    @property
    def acc_and_region(self) -> str:
        return f"{self.aws_account_id}/{self.aws_region}"

    @property
    def console_url(self) -> str:
        """
        The URL to the deployment target account CloudFormation stack.
        """
        aws_console = aws_console_url.AWSConsole(aws_region=self.aws_region)
        return aws_console.cloudformation.get_stack_info(
            name_or_arn=self.stack_id,
        )
