# -*- coding: utf-8 -*-

import cottonformation as cf
from cottonformation.res import glue

param_project_name = cf.Parameter(
    "ProjectName",
    Type=cf.Parameter.TypeEnum.String,
)


def make_db(
    logic_id: str,
    db_name: str,
) -> glue.Database:
    return glue.Database(
        logic_id,
        rp_CatalogId=cf.AWS_ACCOUNT_ID,
        rp_DatabaseInput=glue.PropDatabaseDatabaseInput(
            p_Name=cf.Sub(
                f"${{ProjectName}}_{db_name}",
                dict(
                    ProjectName=param_project_name.ref(),
                ),
            ),
        ),
    )
