# -*- coding: utf-8 -*-

from aws_cloudformation.model import *

def test():
    pass

if __name__ == "__main__":
    from aws_cloudformation.tests import run_cov_test

    run_cov_test(__file__, "aws_cloudformation.model", preview=False)
