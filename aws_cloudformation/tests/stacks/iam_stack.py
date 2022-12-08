# -*- coding: utf-8 -*-

import cottonformation as cf
from cottonformation.res import iam


def make_iam_group1() -> cf.Template:
    tpl = cf.Template()

    iam_group1 = iam.Group(
        "IamGroup1",
        p_GroupName="Group1",
    )
    tpl.add(iam_group1)
    return tpl


def make_iam_group2() -> cf.Template:
    tpl = make_iam_group1()

    iam_group1 = tpl.Resources["IamGroup1"]
    iam_group1.p_Path = "/path1/"

    iam_group2 = iam.Group(
        "IamGroup2",
        p_GroupName="Group2",
    )
    tpl.add(iam_group2)

    return tpl


def make_iam_group3() -> cf.Template:
    tpl = make_iam_group2()

    iam_group1 = tpl.Resources["IamGroup1"]
    iam_group1.p_Path = "/path11/"

    tpl.remove(tpl.Resources["IamGroup2"])

    iam_group3 = iam.Group(
        "IamGroup3",
        p_GroupName="Group3",
        p_ManagedPolicyArns=[
            "arn:aws:iam::aws:policy/IAMReadOnlyAccess",
        ]
    )
    tpl.add(iam_group3)
    return tpl
