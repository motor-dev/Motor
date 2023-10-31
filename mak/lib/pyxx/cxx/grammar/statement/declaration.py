"""
declaration-statement:
    block-declaration
"""

import glrp
from typing import Any
from ...parse import CxxParser, cxx98
from ....ast.statements import DeclarationStatement


@glrp.rule('declaration-statement : block-declaration')
@cxx98
def declaration_statement(self: CxxParser, p: glrp.Production) -> Any:
    return DeclarationStatement(p[0])
