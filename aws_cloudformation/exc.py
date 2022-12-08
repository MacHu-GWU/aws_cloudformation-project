# -*- coding: utf-8 -*-


class StackNotExistError(Exception):
    pass


class DeployStackFailedError(Exception):
    pass


class CreateStackChangeSetButNotChangeError(Exception):
    pass


class CreateStackChangeSetFailedError(Exception):
    pass

