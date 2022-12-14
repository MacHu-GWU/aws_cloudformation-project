.. _release_history:

Release and Version History
==============================================================================


Backlog
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add "StackSet" support

**Minor Improvements**

**Bugfixes**

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
