# -*- coding: utf-8 -*-

import pytest


def test():
    import aws_cloudformation

    _ = aws_cloudformation.deploy_stack
    _ = aws_cloudformation.remove_stack


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
