# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager, AwsServiceEnum

aws_profile = "awshsh_infra_us_east_1"

bsm = BotoSesManager(profile_name=aws_profile)
cf_client = bsm.get_client(AwsServiceEnum.CloudFormation)
