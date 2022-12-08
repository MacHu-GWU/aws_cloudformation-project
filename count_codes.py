# -*- coding: utf-8 -*-

from pathlib_mate import Path

dir_here = Path.dir_here(__file__)

path_list = [
    dir_here / "aws_cloudformation",
    dir_here / "tests",
    dir_here / "tests_int",
]

total = 0
for path in path_list:
    if path.is_file():
        total += (path.read_text().count("\n") + 1)
    else:
        for p in path.select_by_ext(".py"):
            total += (p.read_text().count("\n") + 1)

print(f"total line of code (include test): {total}")
