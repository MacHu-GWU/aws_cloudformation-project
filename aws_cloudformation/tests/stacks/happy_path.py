# -*- coding: utf-8 -*-

import cottonformation as cf
from cottonformation.res import glue, cloudformation

from .common import param_project_name, make_db


def make_tpl_1() -> cf.Template:
    tpl = cf.Template()
    tpl.add(param_project_name)

    db1 = make_db("Database1", "database_1")
    tpl.add(db1)

    return tpl


def make_tpl_2() -> cf.Template:
    tpl = make_tpl_1()
    db1: glue.Database = tpl.Resources["Database1"]
    db1.rp_DatabaseInput.p_Description = "this is database 1"

    db2 = make_db("Database2", "database_2")
    tpl.add(db2)

    output_db2_logic_id = cf.Output(
        "Database2LogicId",
        Value=db2.ref(),
        Export=cf.Export(
            Name=cf.Sub.from_params(
                "{}-database-2-logic-id",
                param_project_name,
            )
        ),
    )
    tpl.add(output_db2_logic_id)
    return tpl


def make_tpl_3() -> cf.Template:
    tpl = make_tpl_2()
    tpl.remove(tpl.Resources["Database1"])
    db2: glue.Database = tpl.Resources["Database2"]
    db2.rp_DatabaseInput.p_Description = "this is database 2"

    db3 = make_db("Database3", "database_3")
    tpl.add(db3)
    return tpl


def make_tpl_4() -> cf.Template:
    tpl = make_tpl_3()

    db4 = make_db("Database4", "database_4")
    tpl.add(db4)

    # sub template 1
    tpl_1 = cf.Template()
    tpl_1.add(param_project_name)

    db_1_1 = make_db("Database11", "database_1_1")
    tpl_1.add(db_1_1)

    # add sub template 1 to main template
    stack_1 = cloudformation.Stack(
        "SubStack1",
        rp_TemplateURL="",
        p_Parameters={"ProjectName": param_project_name.ref()},
    )
    tpl.add(stack_1)
    tpl.add_nested_stack(stack_1, tpl_1)

    # sub template 1-1
    tpl_1_1 = cf.Template()
    tpl_1_1.add(param_project_name)

    db_1_1_1 = make_db("Database111", "database_1_1_1")
    tpl_1_1.add(db_1_1_1)

    # add sub template 1-1-1 to sub template 1-1
    stack_1_1 = cloudformation.Stack(
        "SubStack11",
        rp_TemplateURL="",
        p_Parameters={"ProjectName": param_project_name.ref()},
    )
    tpl_1_1.add(stack_1_1)

    tpl_1_1.add_nested_stack(stack_1_1, tpl_1)

    return tpl


tpl_1 = make_tpl_1().to_json()
tpl_2 = make_tpl_2().to_json()
tpl_3 = make_tpl_3().to_json()
tpl_4 = make_tpl_4().to_json()
