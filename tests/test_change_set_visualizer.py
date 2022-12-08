# -*- coding: utf-8 -*-

import pytest
from aws_cloudformation.change_set_visualizer import visualize_change_set


class TestWaiter:
    def test(self):
        changes = [
            {
                "Type": "Resource",
                "ResourceChange": {
                    "Action": "Modify",
                    "LogicalResourceId": "IamGroup1",
                    "PhysicalResourceId": "Group1",
                    "ResourceType": "AWS::IAM::Group",
                    "Replacement": "False",
                    "Scope": ["Properties"],
                    "Details": [
                        {
                            "Target": {
                                "Attribute": "Properties",
                                "Name": "Path",
                                "RequiresRecreation": "Never",
                            },
                            "Evaluation": "Static",
                            "ChangeSource": "DirectModification",
                        }
                    ],
                },
            },
            {
                "Type": "Resource",
                "ResourceChange": {
                    "Action": "Remove",
                    "LogicalResourceId": "IamGroup2",
                    "PhysicalResourceId": "Group2",
                    "ResourceType": "AWS::IAM::Group",
                    "Scope": [],
                    "Details": [],
                },
            },
            {
                "Type": "Resource",
                "ResourceChange": {
                    "Action": "Add",
                    "LogicalResourceId": "IamGroup3",
                    "ResourceType": "AWS::IAM::Group",
                    "Scope": [],
                    "Details": [],
                },
            },
        ]
        visualize_change_set(changes, _verbose=False)


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.change_set_visualizer", preview=False)
