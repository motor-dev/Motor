"""
expression-statement:
    expression? ;
"""

import glrp
from typing import Any
from ...parse import CxxParser, cxx98
from ....ast.statements import ExpressionStatement, EmptyStatement, ErrorStatement
from typing import TYPE_CHECKING


@glrp.rule('expression-statement : expression? ";"')
@cxx98
def expression_statement(self: CxxParser, p: glrp.Production) -> Any:
    if p[0] is not None:
        return ExpressionStatement(p[0])
    else:
        return EmptyStatement()


@glrp.rule('expression-statement : "#error" ";"')
@cxx98
def expression_statement_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorStatement()
