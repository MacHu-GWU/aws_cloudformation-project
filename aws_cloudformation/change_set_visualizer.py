# -*- coding: utf-8 -*-

import typing as T
import enum
import dataclasses
from collections import Counter


class TargetAttributeEnum(enum.Enum):
    PROPERTIES = "Properties"
    METADATA = "Metadata"
    CREATION_POLICY = "CreationPolicy"
    UPDATE_POLICY = "UpdatePolicy"
    DELETION_POLICY = "DeletionPolicy"
    TAGS = "Tags"


target_attribute_sort_key_mapper = {
    TargetAttributeEnum.PROPERTIES.value: 1,
    TargetAttributeEnum.METADATA.value: 2,
    TargetAttributeEnum.CREATION_POLICY.value: 3,
    TargetAttributeEnum.UPDATE_POLICY.value: 4,
    TargetAttributeEnum.DELETION_POLICY.value: 5,
    TargetAttributeEnum.TAGS.value: 6,
}


@dataclasses.dataclass
class Target:
    attribute: str = dataclasses.field(default=None)
    name: str = dataclasses.field(default=None)
    requires_recreation: str = dataclasses.field(default=None)

    @classmethod
    def from_dict(cls, dct: dict) -> "Target":
        return cls(
            attribute=dct.get("Attribute"),
            name=dct.get("Name"),
            requires_recreation=dct.get("RequiresRecreation"),
        )

    def line(self) -> str:
        return f"{self.attribute}({self.name})"


@dataclasses.dataclass
class Detail:
    target: Target = dataclasses.field()
    evaluation: str = dataclasses.field(default=None)
    change_source: str = dataclasses.field(default=None)
    causing_entity: str = dataclasses.field(default=None)

    @classmethod
    def from_dict(cls, dct: dict) -> "Detail":
        return cls(
            target=Target.from_dict(dct["Target"]),
            evaluation=dct.get("Evaluation"),
            change_source=dct.get("ChangeSource"),
            causing_entity=dct.get("CausingEntity"),
        )


def sort_details(details: T.Iterable[Detail]) -> T.Iterable[Detail]:
    return sorted(
        details,
        key=lambda detail: target_attribute_sort_key_mapper[detail.target.attribute],
    )


class ChangeActionEnum(enum.Enum):
    ADD = "Add"
    MODIFY = "Modify"
    REMOVE = "Remove"
    IMPORT = "Import"
    DYNAMIC = "Dynamic"


@dataclasses.dataclass
class ResourceChange:
    action: str = dataclasses.field()
    resource_type: str = dataclasses.field()
    logical_resource_id: str = dataclasses.field()
    physical_resource_id: str = dataclasses.field(default=None)
    replacement: str = dataclasses.field(default=None)
    details: T.List[Detail] = dataclasses.field(default_factory=list)

    @classmethod
    def from_dict(cls, dct: dict) -> "ResourceChange":
        return cls(
            action=dct["Action"],
            resource_type=dct["ResourceType"],
            logical_resource_id=dct["LogicalResourceId"],
            physical_resource_id=dct.get("PhysicalResourceId"),
            replacement=dct.get("Replacement"),
            details=list(
                sort_details([Detail.from_dict(d) for d in dct.get("Details", [])])
            ),
        )


action_sort_key_mapper = {
    ChangeActionEnum.ADD.value: 1,
    ChangeActionEnum.MODIFY.value: 2,
    ChangeActionEnum.REMOVE.value: 3,
    ChangeActionEnum.IMPORT.value: 4,
    ChangeActionEnum.DYNAMIC.value: 5,
}


def sort_changes(changes: T.Iterable[ResourceChange]) -> T.Iterable[ResourceChange]:
    return sorted(
        changes,
        key=lambda rc: action_sort_key_mapper[rc.action],
    )


@dataclasses.dataclass
class ChangeSet:
    change_set_id: str = dataclasses.field()
    change_set_name: str = dataclasses.field()
    stack_id: str = dataclasses.field()
    stack_name: str = dataclasses.field()
    changes: T.List[ResourceChange] = dataclasses.field(default_factory=list)

    @classmethod
    def from_dict(cls, dct: dict) -> "ChangeSet":
        return cls(
            change_set_id=dct["ChangeSetId"],
            change_set_name=dct["ChangeSetName"],
            stack_id=dct["StackId"],
            stack_name=dct["StackName"],
            changes=[ResourceChange.from_dict(d) for d in dct.get("Changes", [])],
        )


ICON_ADD = "🟢"
ICON_MODIFY = "🔵"
ICON_REMOVE = "🔴"
ICON_IMPORT = "🟣"
ICON_DYNAMIC = "🟡"

icon_mapper = {
    ChangeActionEnum.ADD.value: ICON_ADD,
    ChangeActionEnum.MODIFY.value: ICON_MODIFY,
    ChangeActionEnum.REMOVE.value: ICON_REMOVE,
    ChangeActionEnum.IMPORT.value: ICON_IMPORT,
    ChangeActionEnum.DYNAMIC.value: ICON_DYNAMIC,
}


def print_header(msg: str, char: str, length: int, corner_char=""):
    msg = f" {msg} "
    template = "{corner_char}{{msg:{char}^{length}}}".format(
        char=char,
        length=length,
        corner_char=corner_char,
    )
    print(template.format(msg=msg))


def visualize_change_set(
    changes: T.List[dict],
    _verbose: bool = True,
):
    """
    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_change_set
    """
    resource_change_list: T.List[ResourceChange] = [
        ResourceChange.from_dict(change["ResourceChange"]) for change in changes
    ]
    resource_change_list = list(sort_changes(resource_change_list))
    action_counter = Counter(
        [resource_change.action for resource_change in resource_change_list]
    )
    if _verbose:  # pragma: no cover
        print_header("Change Set Statistics", "-", 80, "+")
    for change_action in ChangeActionEnum:
        if change_action.value in action_counter:
            icon = icon_mapper[change_action.value]
            count = action_counter[change_action.value]
            if count > 1:
                res_ = "Resources"
            else:
                res_ = "Resource"
            if _verbose:  # pragma: no cover
                print(f"| {icon} {change_action.value:<10} {count} {res_}")
    if _verbose:  # pragma: no cover
        print("|")
        print("+" + "-" * 80)

    if _verbose:  # pragma: no cover
        print_header("Changes", "-", 80, "+")


    if len(resource_change_list):
        max_logic_resource_id_length = max([
            len(resource_change.logical_resource_id)
            for resource_change in resource_change_list
        ])

    for resource_change in resource_change_list:
        action = resource_change.action
        icon = icon_mapper[action]
        logical_resource_id = resource_change.logical_resource_id
        resource_type = resource_change.resource_type
        if _verbose:  # pragma: no cover
            action_ = f"{action} Resource:"
            print(
                f"| {icon} 📦 {action_:<21}{logical_resource_id:<{max_logic_resource_id_length+4}}{resource_type}"
            )
        for detail in resource_change.details:
            attribute = detail.target.attribute
            name = detail.target.name
            if _verbose:
                key = attribute + ":"
                if name:
                    identifier = f"{resource_type}.{name}"
                else:
                    identifier = resource_type
                print(f"|     {icon} 💡 {key:<17}{logical_resource_id:<{max_logic_resource_id_length+4}}{identifier}")
    if _verbose:  # pragma: no cover
        print("|")
        print("+" + "-" * 80)
