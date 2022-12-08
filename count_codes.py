# -*- coding: utf-8 -*-

import typing as T
from pathlib_mate import Path

dir_here = Path.dir_here(__file__)

def count_python_code_lines(path_list: T.List[Path]) -> int:
    total = 0
    for path in path_list:
        if path.is_file():
            total += (path.read_text().count("\n") + 1)
        else:
            for p in path.select_by_ext(".py"):
                total += (p.read_text().count("\n") + 1)
    return total


total_source = count_python_code_lines([
    dir_here / "aws_cloudformation",
])
total_tests = count_python_code_lines([
    dir_here / "tests",
    dir_here / "tests_int",
])

print(f"total line of source code: {total_source}")
print(f"total line of test code: {total_tests}")
print(f"total line of code: {total_source + total_tests}")
