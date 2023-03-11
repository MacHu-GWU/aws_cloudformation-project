.. _release_history:

Release and Version History
==============================================================================


Backlog
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**



1.3.2 (2023-03-11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

- :func:`~aws_cloudformation.deploy.deploy_stack` now returns a :class:`~aws_cloudformation.deploy.DeployStackResponse` object.

**Bugfixes**

**Miscellaneous**

- fix type hint


1.3.1 (2023-03-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add "StackSet" support, add :func:`~aws_cloudformation.deploy.remove_stack_set` and :func:`~aws_cloudformation.deploy.deploy_stack_set`.
- now ``deploy_stack`` and ``remove_stack`` supports full list of boto3 arguments.

**Minor Improvements**

- use sentinel ``NOTHING`` to avoid ambiguity of ``None``.

**Bugfixes**

- fix a bug that waiter didn't raise exception when ``deploy_stack`` or ``remove_stack`` fail.

**Miscellaneous**


1.2.1 (2022-12-08)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add support to visualize change set for nested stack
- expose more useful functions / classes as public API

**Minor Improvements**

- more integration test using real AWS CloudFormation


1.1.2 (2022-12-08)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Bugfixes**

- fix a bug that using s3 uri for ``TemplateUrl`` argument, it should use ``https://s3.amazonaws.com/${bucket}/${key}``


1.1.1 (2022-12-08)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Minor Improvements**

- Add colorful console log.
- stablize the API.

**Bugfixes**

- raise exception explicitly when stack status is ``REVIEW_IN_PROGRESS``.

**Miscellaneous**

- Enrich documentation


0.1.1 (2022-12-07)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- First release
- Add :func:`~aws_cloudformation.deploy.deploy_stack`, similar to ``terraform plan`` and ``terraform apply`` combined API. Allow direct deploy or using change set
- Add :func:`~aws_cloudformation.deploy.remove_stack`, similar to ``terraform destroy``.

**Miscellaneous**

- total line of source code: 2168
- total line of test code: 329
- total line of code: 2497
