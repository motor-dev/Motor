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
from ...parser import cxx98, cxx20
from motor_typing import TYPE_CHECKING


@glrp.rule('jump-statement : "break" ";"')
@glrp.rule('jump-statement : "continue" ";"')
@glrp.rule('jump-statement : "return" expr-or-braced-init-list? ";"')
@glrp.rule('jump-statement : "goto" "identifier" ";"')
@cxx98
def jump_statement(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('jump-statement : coroutine-return-statement')
@cxx20
def jump_statement_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('coroutine-return-statement : "co_return" expr-or-braced-init-list? ";"')
@cxx20
def coroutine_return_statement_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ...parser import CxxParser