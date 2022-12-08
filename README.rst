
.. image:: https://readthedocs.org/projects/aws_cloudformation/badge/?version=latest
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


.. image:: https://img.shields.io/badge/Link-Document-blue.svg
    :target: https://aws_cloudformation.readthedocs.io/index.html

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://aws_cloudformation.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Source_Code-blue.svg
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
Enable ``terraform plan``, ``terraform apply`` styled deployment.

**Talk is cheap, show me the code**

⭐ CloudFormation declaration, see `cottonformation <https://github.com/MacHu-GWU/cottonformation-project>`_:

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

⭐ Deployment Script:

.. code-block:: python

    # -*- coding: utf-8 -*-

    from aws_cloudformation.deploy import deploy_stack, remove_stack
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
        skip_prompt=True,
    )

    deploy_stack(
        bsm,
        stack_name=stack_name,
        template=make_tpl_2().to_json(),
        skip_prompt=True,
    )

    deploy_stack(
        bsm,
        stack_name=stack_name,
        template=make_tpl_3().to_json(),
        skip_prompt=True,
    )

    remove_stack(
        bsm,
        stack_name=stack_name,
        skip_prompt=True,
    )

⭐ Console Output:

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


.. _install:

Install
------------------------------------------------------------------------------

``aws_cloudformation`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install aws_cloudformation

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade aws_cloudformation