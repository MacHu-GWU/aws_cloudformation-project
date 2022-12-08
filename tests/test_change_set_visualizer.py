# -*- coding: utf-8 -*-

from aws_cloudformation.change_set_visualizer import ChangeSet, visualize_change_set


class TestWaiter:
    def test(self):
        response = {
            "ChangeSetName": "aws-cf-int-test",
            "ChangeSetId": "arn:aws:cloudformation:us-east-1:669508176277:changeSet/aws-cf-int-test-2022-12-08-21-16-14-563/0e669c50-3947-445f-b623-a9cddd8d697a",
            "StackName": "aws-cf-int-test",
            "StackId": "arn:aws:cloudformation:us-east-1:669508176277:stack/aws-cf-int-test/cd0bd470-77",
            "Changes": [
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
            ],
        }
        visualize_change_set(ChangeSet.from_dict(response), _verbose=True)


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.change_set_visualizer", preview=False)
