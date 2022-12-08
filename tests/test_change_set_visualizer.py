# -*- coding: utf-8 -*-

from aws_cloudformation.change_set_visualizer import visualize_change_set


class TestWaiter:
    def test(self):
        changes = [
            {
                "Type": "Resource",
                "ResourceChange": {
                    "Action": "Remove",
                    "LogicalResourceId": "Secret1",
                    "PhysicalResourceId": "arn:aws:secretsmanager:us-east-1:669508176277:secret:aws_cft_secret1-DIidyF",
                    "ResourceType": "AWS::SecretsManager::Secret",
                    "Scope": [],
                    "Details": [],
                },
            },
            {
                "Type": "Resource",
                "ResourceChange": {
                    "Action": "Modify",
                    "LogicalResourceId": "Secret222",
                    "PhysicalResourceId": "arn:aws:secretsmanager:us-east-1:669508176277:secret:aws_cft_secret2-wicjVX",
                    "ResourceType": "AWS::SecretsManager::Secret",
                    "Replacement": "Conditional",
                    "Scope": [
                        "UpdatePolicy",
                        "Metadata",
                        "CreationPolicy",
                        "Properties",
                        "Tags",
                    ],
                    "Details": [
                        {
                            "Target": {
                                "Attribute": "Metadata",
                                "RequiresRecreation": "Never",
                            },
                            "Evaluation": "Static",
                            "ChangeSource": "DirectModification",
                        },
                        {
                            "Target": {
                                "Attribute": "UpdatePolicy",
                                "RequiresRecreation": "Never",
                            },
                            "Evaluation": "Static",
                            "ChangeSource": "DirectModification",
                        },
                        {
                            "Target": {
                                "Attribute": "Properties",
                                "Name": "Description",
                                "RequiresRecreation": "Conditionally",
                            },
                            "Evaluation": "Static",
                            "ChangeSource": "DirectModification",
                        },
                        {
                            "Target": {
                                "Attribute": "Tags",
                                "RequiresRecreation": "Conditionally",
                            },
                            "Evaluation": "Static",
                            "ChangeSource": "DirectModification",
                        },
                        {
                            "Target": {
                                "Attribute": "CreationPolicy",
                                "RequiresRecreation": "Never",
                            },
                            "Evaluation": "Static",
                            "ChangeSource": "DirectModification",
                        },
                    ],
                },
            },
            {
                "Type": "Resource",
                "ResourceChange": {
                    "Action": "Add",
                    "LogicalResourceId": "Secret33333",
                    "ResourceType": "AWS::SecretsManager::Secret",
                    "Scope": [],
                    "Details": [],
                },
            },
        ]
        visualize_change_set(changes, _verbose=True)


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.change_set_visualizer", preview=False)
