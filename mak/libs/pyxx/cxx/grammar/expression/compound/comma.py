"""
expression:
    assignment-expression
    expression , assignment-expression
"""

import glrp
from ....parser import cxx98, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('expression : expression-proxy')
@cxx98
def expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('expression-proxy : assignment-expression')
@glrp.rule('expression-proxy : expression-proxy "," assignment-expression')
@cxx98
def expression_proxy(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('expression? : expression')
@glrp.rule('expression? : ')
@cxx98
def expression_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('expression')
@cxx98_merge
def ambiguous_expression(self, ambiguous_postfix_expression, id_template):
    # type: (CxxParser, List[Any], List[Any]) -> None
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ....parser import CxxParser