# -*- coding: utf-8 -*-

import cottonformation as cf

from .common import param_project_name, make_db


def make_tpl_0_malformed() -> cf.Template:
    tpl = cf.Template()

    tpl.add(param_project_name)

    db0 = make_db(
        logic_id="Database0",
        db_name="a" * 300,
    )
    tpl.add(db0)

    return tpl


def make_tpl_1() -> cf.Template:
    tpl = cf.Template()

    tpl.add(param_project_name)

    db1 = make_db(
        logic_id="Database1",
        db_name="database_1",
    )
    tpl.add(db1)

    return tpl


def make_tpl_2_malformed() -> cf.Template:
    tpl = make_tpl_1()

    db2 = make_db(
        logic_id="Database2",
        db_name="a" * 300,
    )
    tpl.add(db2)

    return tpl


tpl_0_malformed = make_tpl_0_malformed().to_json()
tpl_1 = make_tpl_1().to_json()
tpl_2_malformed = make_tpl_2_malformed().to_json()
