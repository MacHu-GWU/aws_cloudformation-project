.. .. image:: https://readthedocs.org/projects/aws_cloudformation/badge/?version=latest
        :target: https://aws_cloudformation.readthedocs.io/index.html
        :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/aws_cloudformation-project/workflows/CI/badge.svg
    :target: https://github.com/MacHu-GWU/aws_cloudformation-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/aws_cloudformation-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/aws_cloudformation-project

.. image:: https://img.shields.io/pypi/v/aws_cloudformation.svg
    :target: https://pypi.python.org/pypi/aws_cloudformation

.. image:: https://img.shields.io/pypi/l/aws_cloudformation.svg
    :target: https://pypi.python.org/pypi/aws_cloudformation

.. image:: https://img.shields.io/pypi/pyversions/aws_cloudformation.svg
    :target: https://pypi.python.org/pypi/aws_cloudformation

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/aws_cloudformation-project

------

.. .. image:: https://img.shields.io/badge/Link-Document-blue.svg
    :target: https://aws_cloudformation.readthedocs.io/index.html

..  .. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://aws_cloudformation.readthedocs.io/py-modindex.html

..  .. image:: https://img.shields.io/badge/Link-Source_Code-blue.svg
    :target: https://aws_cloudformation.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/aws_cloudformation-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/aws_cloudformation-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/aws_cloudformation-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/aws_cloudformation#files


Welcome to ``aws_cloudformation`` Documentation
==============================================================================
AWS CloudFormation deployment for human, Enable ``terraform plan``, ``terraform apply`` styled deployment.

Features:

1. Preview the change set details before deployment.
2. Automatically upload big template to S3 before deployment.
3. Support SYNC call for deployment and deletion, wait until it success or fail (the original API is ASYNC call).
4. Allow prompt for user to enter "YES" to proceed.
5. Provide hyperlink for one-click to jump to the Console to preview.

.. contents::
    :class: this-will-duplicate-information-and-it-is-still-useful-here
    :depth: 1
    :local:


Talk is cheap, show me the code
------------------------------------------------------------------------------
⭐ **Console Output**:

.. code-block:: bash

    ============== Deploy stack: 'cottonformation-deploy-stack-test' ===============
      preview stack in AWS CloudFormation console: https://console.aws.amazon.com/cloudformation/home?#/stacks?filteringStatus=active&filteringText=cottonformation-deploy-stack-test&viewNested=true&hideStacks=false
      preview **change set details** at: https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/changesets/changes?stackId=arn:aws:cloudformation:us-east-1:111122223333:stack/cottonformation-deploy-stack-test/0c5596c0-76b4-11ed-92b1-0a0bcad48579&changeSetId=arn:aws:cloudformation:us-east-1:111122223333:changeSet/cottonformation-deploy-stack-test-2022-12-08-04-51-58-892/8c88d0c1-d5c7-495b-820e-29e5752a04d4
      wait for change set creation to finish ...
        on 1 th attempt, elapsed 5 seconds, remain 55 seconds ...
        reached status CREATE_COMPLETE
    +---------------------------- Change Set Statistics -----------------------------
    | 🟢 Add        1 Resource
    |
    +--------------------------------------------------------------------------------
    +----------------------------------- Changes ------------------------------------
    | 🟢 📦 Add Resource:        Secret1    AWS::SecretsManager::Secret
    |
    +--------------------------------------------------------------------------------
        need to execute the change set to apply those changes.
      preview **create stack progress** at: https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/stackinfo?filteringText=cottonformation-deploy-stack-test&viewNested=true&hideStacks=false&stackId=arn:aws:cloudformation:us-east-1:111122223333:stack/cottonformation-deploy-stack-test/0c5596c0-76b4-11ed-92b1-0a0bcad48579&filteringStatus=active
      wait for deploy to finish ...
        on 2 th attempt, elapsed 10 seconds, remain 50 seconds ...
        reached status 🟢 'CREATE_COMPLETE'
      done


    ============== Deploy stack: 'cottonformation-deploy-stack-test' ===============
      preview stack in AWS CloudFormation console: https://console.aws.amazon.com/cloudformation/home?#/stacks?filteringStatus=active&filteringText=cottonformation-deploy-stack-test&viewNested=true&hideStacks=false
      preview **change set details** at: https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/changesets/changes?stackId=arn:aws:cloudformation:us-east-1:111122223333:stack/cottonformation-deploy-stack-test/0c5596c0-76b4-11ed-92b1-0a0bcad48579&changeSetId=arn:aws:cloudformation:us-east-1:111122223333:changeSet/cottonformation-deploy-stack-test-2022-12-08-04-52-39-134/8e1fd139-7a37-43dd-9378-40a328970036
      wait for change set creation to finish ...
        on 1 th attempt, elapsed 5 seconds, remain 55 seconds ...
        reached status CREATE_COMPLETE
    +---------------------------- Change Set Statistics -----------------------------
    | 🟢 Add        1 Resource
    | 🔵 Modify     1 Resource
    |
    +--------------------------------------------------------------------------------
    +----------------------------------- Changes ------------------------------------
    | 🟢 📦 Add Resource:        Secret222    AWS::SecretsManager::Secret
    | 🔵 📦 Modify Resource:     Secret1      AWS::SecretsManager::Secret
    |     🔵 💡 Properties:      Secret1      AWS::SecretsManager::Secret.Description
    |     🔵 💡 Tags:            Secret1      AWS::SecretsManager::Secret
    |
    +--------------------------------------------------------------------------------
        need to execute the change set to apply those changes.
      preview **update stack progress** at: https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/stackinfo?filteringText=cottonformation-deploy-stack-test&viewNested=true&hideStacks=false&stackId=arn:aws:cloudformation:us-east-1:111122223333:stack/cottonformation-deploy-stack-test/0c5596c0-76b4-11ed-92b1-0a0bcad48579&filteringStatus=active
      wait for deploy to finish ...
        on 3 th attempt, elapsed 15 seconds, remain 45 seconds ...
        reached status 🟢 'UPDATE_COMPLETE'
      done


    ============== Deploy stack: 'cottonformation-deploy-stack-test' ===============
      preview stack in AWS CloudFormation console: https://console.aws.amazon.com/cloudformation/home?#/stacks?filteringStatus=active&filteringText=cottonformation-deploy-stack-test&viewNested=true&hideStacks=false
      preview **change set details** at: https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/changesets/changes?stackId=arn:aws:cloudformation:us-east-1:111122223333:stack/cottonformation-deploy-stack-test/0c5596c0-76b4-11ed-92b1-0a0bcad48579&changeSetId=arn:aws:cloudformation:us-east-1:111122223333:changeSet/cottonformation-deploy-stack-test-2022-12-08-04-53-07-499/6edbcdf2-8e27-463f-bc5f-35587463fceb
      wait for change set creation to finish ...
        on 2 th attempt, elapsed 10 seconds, remain 50 seconds ...
        reached status CREATE_COMPLETE
    +---------------------------- Change Set Statistics -----------------------------
    | 🟢 Add        1 Resource
    | 🔵 Modify     1 Resource
    | 🔴 Remove     1 Resource
    |
    +--------------------------------------------------------------------------------
    +----------------------------------- Changes ------------------------------------
    | 🟢 📦 Add Resource:        Secret33333    AWS::SecretsManager::Secret
    | 🔵 📦 Modify Resource:     Secret222      AWS::SecretsManager::Secret
    |     🔵 💡 Properties:      Secret222      AWS::SecretsManager::Secret.Description
    |     🔵 💡 Metadata:        Secret222      AWS::SecretsManager::Secret
    |     🔵 💡 CreationPolicy:  Secret222      AWS::SecretsManager::Secret
    |     🔵 💡 UpdatePolicy:    Secret222      AWS::SecretsManager::Secret
    |     🔵 💡 Tags:            Secret222      AWS::SecretsManager::Secret
    | 🔴 📦 Remove Resource:     Secret1        AWS::SecretsManager::Secret
    |
    +--------------------------------------------------------------------------------
        need to execute the change set to apply those changes.
      preview **update stack progress** at: https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/stackinfo?filteringText=cottonformation-deploy-stack-test&viewNested=true&hideStacks=false&stackId=arn:aws:cloudformation:us-east-1:111122223333:stack/cottonformation-deploy-stack-test/0c5596c0-76b4-11ed-92b1-0a0bcad48579&filteringStatus=active
      wait for deploy to finish ...
        on 3 th attempt, elapsed 15 seconds, remain 45 seconds ...
        reached status 🟢 'UPDATE_COMPLETE'
      done


    =============== Remove stack 'cottonformation-deploy-stack-test' ===============
      preview stack in AWS CloudFormation console: https://console.aws.amazon.com/cloudformation/home?#/stacks?filteringStatus=active&filteringText=cottonformation-deploy-stack-test&viewNested=true&hideStacks=false
      wait for delete to finish ...
        on 1 th attempt, elapsed 5 seconds, remain 55 seconds ...
        already deleted.
      done


⭐ **CloudFormation declaration**, see `cottonformation <https://github.com/MacHu-GWU/cottonformation-project>`_:

.. code-block:: python

    # -*- coding: utf-8 -*-

    import cottonformation as cf
    from cottonformation.res import secretsmanager


    def make_tpl_1() -> cf.Template:
        """
        Create Secret1
        """
        tpl = cf.Template()

        secret1 = secretsmanager.Secret(
            "Secret1",
            p_Name="aws_cft_secret1",
            p_Description="This is Secret 1",
            p_Tags=[
                cf.Tag(p_Key="Creator", p_Value="Alice"),
                cf.Tag(p_Key="Description", p_Value="Hello"),
            ]
        )
        tpl.add(secret1)

        return tpl


    def make_tpl_2() -> cf.Template:
        """
        Modify Secret1
        Create Secret222
        """
        tpl = make_tpl_1()

        secret1: secretsmanager.Secret = tpl.Resources["Secret1"]
        secret1.p_Description = "This must be Secret 1"
        secret1.p_Tags = [
            cf.Tag(p_Key="Creator", p_Value="Bob"),
            cf.Tag(p_Key="Env", p_Value="Dev"),
        ]

        secret2 = secretsmanager.Secret(
            "Secret222",
            p_Name="aws_cft_secret2",
            p_Description="This is Secret 2",
        )
        tpl.add(secret2)

        output_secret2_arn = cf.Output(
            "Secret222Arn",
            Value=secret2.ref(),
        )
        tpl.add(output_secret2_arn)

        return tpl


    def make_tpl_3() -> cf.Template:
        """
        Delete Secret1
        Modify Secret222
        Create Secret33333
        """
        tpl = make_tpl_2()

        tpl.remove(tpl.Resources["Secret1"])

        secret2: secretsmanager.Secret = tpl.Resources["Secret222"]
        secret2.p_Description = "This definitely be Secret 2"
        secret2.p_Tags = [
            cf.Tag(p_Key="Creator", p_Value="Cathy"),
            cf.Tag(p_Key="Env", p_Value="QA"),
        ]
        secret2.ra_Metadata = {"email": "cathy@email.com"}

        secret3 = secretsmanager.Secret(
            "Secret33333",
            p_Name="aws_cft_secret3",
            p_Description="This is Secret 3",
        )
        tpl.add(secret3)

        return tpl

⭐ **Deployment Script**:

.. code-block:: python

    # -*- coding: utf-8 -*-

    from aws_cloudformation import deploy_stack, remove_stack
    from aws_cloudformation.tests import bsm
    from aws_cloudformation.tests.stacks.secretmanager_stack import (
        make_tpl_1,
        make_tpl_2,
        make_tpl_3,
    )

    stack_name = "cottonformation-deploy-stack-test"

    deploy_stack(
        bsm,
        stack_name=stack_name,
        template=make_tpl_1().to_json(),
        skip_prompt=True, # by default, it prompt user input for YES / NO to proceed
        # skip_plan=False, # by default, it does plan first
        # wait=True, # by default, it waits the update to finish
    )

    deploy_stack(
        bsm,
        stack_name=stack_name,
        template=make_tpl_2().to_json(),
        skip_prompt=True,
        # skip_plan=False,
        # wait=True,
    )

    deploy_stack(
        bsm,
        stack_name=stack_name,
        template=make_tpl_3().to_json(),
        skip_prompt=True,
        # skip_plan=False,
        # wait=True,
    )

    remove_stack(
        bsm,
        stack_name=stack_name,
        skip_prompt=True,
    )


API Reference
------------------------------------------------------------------------------
.. code-block:: python

    def deploy_stack(
        bsm: "BotoSesManager",
        stack_name: str,
        template: T.Optional[str],
        use_previous_template: T.Optional[bool] = None,
        bucket: T.Optional[str] = None,
        prefix: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_TEMPLATE,
        parameters: T.List[Parameter] = None,
        tags: dict = None,
        execution_role_arn: T.Optional[str] = None,
        include_iam: bool = False,
        include_named_iam: bool = False,
        include_macro: bool = False,
        stack_policy: T.Optional[str] = None,
        prefix_stack_policy: T.Optional[str] = DEFAULT_S3_PREFIX_FOR_STACK_POLICY,
        resource_types: T.Optional[T.List[str]] = None,
        client_request_token: T.Optional[str] = None,
        enable_termination_protection: T.Optional[bool] = None,
        disable_rollback: T.Optional[bool] = None,
        wait: bool = True,
        delays: T.Union[int, float] = DEFAULT_UPDATE_DELAYS,
        timeout: T.Union[int, float] = DEFAULT_UPDATE_TIMEOUT,
        skip_plan: bool = False,
        skip_prompt: bool = False,
        change_set_delays: T.Union[int, float] = DEFAULT_CHANGE_SET_DELAYS,
        change_set_timeout: T.Union[int, float] = DEFAULT_CHANGE_SET_TIMEOUT,
        verbose: bool = True,
    ):
        """
        Deploy (create or update) an AWS CloudFormation stack. But way more powerful
        than the original boto3 API.

        Reference:

        - Create Stack Boto3 API: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.create_stack
        - Update Stack Boto3 API: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.update_stack

        :param bsm: ``boto_session_manager.BotoSesManager`` object
        :param stack_name: the stack name or unique stack id
        :param template: CloudFormation template JSON or Yaml body in text, or the
            s3 uri pointing to a CloudFormation template file.
        :param use_previous_template: see "Update Stack Boto3 API" link
        :param bucket: default None; if given, automatically upload template to S3
            before deployment. see :func:`~aws_cloudformation.better_boto.upload_template_to_s3`
            for more details.
        :param prefix: the s3 prefix where you want to upload the template to
        :param parameters: see "Update Stack Boto3 API" link
        :param tags: see "Update Stack Boto3 API" link
        :param execution_role_arn: see "Update Stack Boto3 API" link
        :param include_iam: see "Capacities" part in "Update Stack Boto3 API" link
        :param include_named_iam: see "Capacities" part in "Update Stack Boto3 API" link
        :param include_macro: see "Capacities" part in "Update Stack Boto3 API" link
        :param stack_policy: Stack Policy JSON or Yaml body in text, or the
            s3 uri pointing to a Stack Policy JSON template file.
        :param prefix_stack_policy: see "Update Stack Boto3 API" link
        :param resource_types: see "Update Stack Boto3 API" link
        :param client_request_token: see "Update Stack Boto3 API" link
        :param enable_termination_protection: see "Create Stack Boto3 API" link
        :param disable_rollback: see "Update Stack Boto3 API" link
        :param wait: default True; if True, then wait the create / update action
            to success or fail; if False, then it is an async call and return immediately;
            note that if you have skip_plan is False (using change set), you always
            have to wait the change set creation to finish.
        :param delays: how long it waits (in seconds) between two
            "describe_stacks" api call to get the stack status
        :param timeout: how long it will raise timeout error
        :param skip_plan: default False; if False, force to use change set to
            create / update; if True, then do create / update without change set.
        :param skip_prompt: default False; if False, you have to enter "Yes"
            in prompt to do deployment; if True, then execute the deployment directly.
        :param change_set_delays: how long it waits (in seconds) between two
            "describe_change_set" api call to get the change set status
        :param change_set_timeout: how long it will raise timeout error
        :param verbose: whether you want to log information to console

        :return: Nothing

        .. versionadded:: 0.1.1
        """

    def remove_stack(
        bsm: "BotoSesManager",
        stack_name: T.Optional[str] = None,
        retain_resources: T.Optional[T.List[str]] = None,
        role_arn: T.Optional[bool] = None,
        client_request_token: T.Optional[str] = None,
        wait: bool = True,
        delays: T.Union[int, float] = DEFAULT_UPDATE_DELAYS,
        timeout: T.Union[int, float] = DEFAULT_UPDATE_TIMEOUT,
        skip_prompt: bool = False,
        verbose: bool = True,
    ):
        """
        Remove an AWS CloudFormation Stack.

        Reference:

        - Delete Stack Boto3 API: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.delete_stack

        :param bsm: ``boto_session_manager.BotoSesManager`` object
        :param stack_name: the stack name or unique stack id
        :param retain_resources: see "Delete Stack Boto3 API" link
        :param role_arn: see "Delete Stack Boto3 API" link
        :param client_request_token: see "Delete Stack Boto3 API" link
        :param wait: default True; if True, then wait the delete action
            to success or fail; if False, then it is an async call and return immediately.
        :param delays: how long it waits (in seconds) between two
            "describe_stacks" api call to get the stack status
        :param timeout: how long it will raise timeout error
        :param skip_prompt: default False; if False, you have to enter "Yes"
            in prompt to do deletion; if True, then execute the deletion directly.
        :param verbose: whether you want to log information to console

        :return: Nothing

        .. versionadded:: 0.1.1
        """


.. _install:

Install
------------------------------------------------------------------------------

``aws_cloudformation`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install aws_cloudformation

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade aws_cloudformation