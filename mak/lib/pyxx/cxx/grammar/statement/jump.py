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
from typing import Any
from ...parse import CxxParser, cxx98, cxx20
from ....ast.statements import BreakStatement, ContinueStatement, ReturnStatement, GotoStatement, CoReturnStatement, ErrorStatement


@glrp.rule('jump-statement : "break" ";"')
@cxx98
def jump_statement_break(self: CxxParser, p: glrp.Production) -> Any:
    return BreakStatement()


@glrp.rule('jump-statement : "continue" ";"')
@cxx98
def jump_statement_continue(self: CxxParser, p: glrp.Production) -> Any:
    return ContinueStatement()


@glrp.rule('jump-statement : "return" expr-or-braced-init-list? ";"')
@cxx98
def jump_statement_return(self: CxxParser, p: glrp.Production) -> Any:
    return ReturnStatement(p[1])


@glrp.rule('jump-statement : "goto" "identifier" ";"')
@cxx98
def jump_statement_goto(self: CxxParser, p: glrp.Production) -> Any:
    return GotoStatement(p[1].text())


@glrp.rule('jump-statement : coroutine-return-statement')
@cxx20
def jump_statement_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('coroutine-return-statement : "co_return" expr-or-braced-init-list? ";"')
@cxx20
def coroutine_return_statement_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return CoReturnStatement(p[1])


@glrp.rule('jump-statement : "return" "#error" ";"')
@glrp.rule('jump-statement : "goto" "#error" ";"')
@cxx98
def jump_statement_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorStatement()
