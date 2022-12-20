"""
expression-statement:
    expression? ;
"""

import glrp
from ...parse import cxx98
from ....ast.statements import ExpressionStatement, EmptyStatement
from motor_typing import TYPE_CHECKING


@glrp.rule('expression-statement : expression? ";"')
@cxx98
def expression_statement(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    if p[0] is not None:
        return ExpressionStatement(p[0])
    else:
        return EmptyStatement()


if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser