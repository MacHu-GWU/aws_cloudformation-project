# -*- coding: utf-8 -*-
import pytest

from aws_cloudformation.stack import StackStatusEnum, DriftStatusEnum, Parameter


class TestStackStatusEnum:
    def test(self):
        assert StackStatusEnum.UPDATE_COMPLETE.is_success() is True
        assert StackStatusEnum.UPDATE_COMPLETE.is_failed() is False
        assert StackStatusEnum.UPDATE_COMPLETE.is_in_progress() is False
        assert StackStatusEnum.UPDATE_COMPLETE.is_complete() is True
        assert StackStatusEnum.UPDATE_COMPLETE.is_stopped() is True

        assert StackStatusEnum.UPDATE_ROLLBACK_COMPLETE.is_success() is False
        assert StackStatusEnum.UPDATE_ROLLBACK_COMPLETE.is_failed() is True
        assert StackStatusEnum.UPDATE_ROLLBACK_COMPLETE.is_in_progress() is False
        assert StackStatusEnum.UPDATE_ROLLBACK_COMPLETE.is_complete() is True
        assert StackStatusEnum.UPDATE_ROLLBACK_COMPLETE.is_stopped() is True

        assert StackStatusEnum.UPDATE_ROLLBACK_IN_PROGRESS.is_success() is False
        assert StackStatusEnum.UPDATE_ROLLBACK_IN_PROGRESS.is_failed() is True
        assert StackStatusEnum.UPDATE_ROLLBACK_IN_PROGRESS.is_in_progress() is True
        assert StackStatusEnum.UPDATE_ROLLBACK_IN_PROGRESS.is_complete() is False
        assert StackStatusEnum.UPDATE_ROLLBACK_IN_PROGRESS.is_stopped() is False

        assert StackStatusEnum.UPDATE_ROLLBACK_FAILED.is_success() is False
        assert StackStatusEnum.UPDATE_ROLLBACK_FAILED.is_failed() is True
        assert StackStatusEnum.UPDATE_ROLLBACK_FAILED.is_in_progress() is False
        assert StackStatusEnum.UPDATE_ROLLBACK_FAILED.is_complete() is False
        assert StackStatusEnum.UPDATE_ROLLBACK_FAILED.is_stopped() is True

        assert StackStatusEnum.UPDATE_COMPLETE.is_live() is True
        assert StackStatusEnum.DELETE_COMPLETE.is_live() is False

        StackStatusEnum.get_by_name("UPDATE_COMPLETE")


class TestDriftStatusEnum:
    def test(self):
        DriftStatusEnum.get_by_name("DRIFTED")


class TestParameter:
    def test_init(self):
        with pytest.raises(ValueError):
            Parameter(key="k", value="v", use_previous_value=True)

        assert Parameter(key="k", value="v").to_kwargs() == {
            "ParameterKey": "k",
            "ParameterValue": "v",
        }

        assert Parameter(key="k", use_previous_value=True).to_kwargs() == {
            "ParameterKey": "k",
            "UsePreviousValue": True,
        }


if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.stack", preview=False)
