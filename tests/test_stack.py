# -*- coding: utf-8 -*-

from aws_cloudformation.stack import StackStatusEnum


class TestStackStatusEnum:
    def test(self):
        assert StackStatusEnum.UPDATE_COMPLETE.is_success() is True
        assert StackStatusEnum.UPDATE_COMPLETE.is_failed() is False
        assert StackStatusEnum.UPDATE_COMPLETE.is_in_progress() is False
        assert StackStatusEnum.UPDATE_COMPLETE.is_complete() is True

        assert StackStatusEnum.UPDATE_ROLLBACK_COMPLETE.is_success() is False
        assert StackStatusEnum.UPDATE_ROLLBACK_COMPLETE.is_failed() is True
        assert StackStatusEnum.UPDATE_ROLLBACK_COMPLETE.is_in_progress() is False
        assert StackStatusEnum.UPDATE_ROLLBACK_COMPLETE.is_complete() is True

        assert StackStatusEnum.UPDATE_ROLLBACK_IN_PROGRESS.is_success() is False
        assert StackStatusEnum.UPDATE_ROLLBACK_IN_PROGRESS.is_failed() is True
        assert StackStatusEnum.UPDATE_ROLLBACK_IN_PROGRESS.is_in_progress() is True
        assert StackStatusEnum.UPDATE_ROLLBACK_IN_PROGRESS.is_complete() is False

        assert StackStatusEnum.UPDATE_ROLLBACK_FAILED.is_success() is False
        assert StackStatusEnum.UPDATE_ROLLBACK_FAILED.is_failed() is True
        assert StackStatusEnum.UPDATE_ROLLBACK_FAILED.is_in_progress() is False
        assert StackStatusEnum.UPDATE_ROLLBACK_FAILED.is_complete() is False


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.stack", preview=False)
