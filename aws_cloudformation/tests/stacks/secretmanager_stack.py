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
