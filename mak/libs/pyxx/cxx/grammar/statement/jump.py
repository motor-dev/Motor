"""
jump-statement:
    break ;
    continue ;
    return expr-or-braced-init-list? ;
    coroutine-return-statement
    goto identifier ;

coroutine-return-statement:
    co_return expr-or-braced-init-list? ;
"""

import glrp
from ...parse import cxx98, cxx20
from ....ast.statements import BreakStatement, ContinueStatement, ReturnStatement, GotoStatement, CoReturnStatement
from motor_typing import TYPE_CHECKING


@glrp.rule('jump-statement : "break" ";"')
@cxx98
def jump_statement_break(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BreakStatement()


@glrp.rule('jump-statement : "continue" ";"')
@cxx98
def jump_statement_continue(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ContinueStatement()


@glrp.rule('jump-statement : "return" expr-or-braced-init-list? ";"')
@cxx98
def jump_statement_return(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ReturnStatement(p[1])


@glrp.rule('jump-statement : "goto" "identifier" ";"')
@cxx98
def jump_statement_goto(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return GotoStatement(p[1].text())


@glrp.rule('jump-statement : coroutine-return-statement')
@cxx20
def jump_statement_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('coroutine-return-statement : "co_return" expr-or-braced-init-list? ";"')
@cxx20
def coroutine_return_statement_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return CoReturnStatement(p[1])


if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser