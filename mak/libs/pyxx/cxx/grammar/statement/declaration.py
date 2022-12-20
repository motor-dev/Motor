"""
declaration-statement:
    block-declaration
"""

import glrp
from ...parse import cxx98
from ....ast.statements import DeclarationStatement
from motor_typing import TYPE_CHECKING


@glrp.rule('declaration-statement : block-declaration')
@cxx98
def declaration_statement(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return DeclarationStatement(p[0])


if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser