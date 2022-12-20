"""
compound-statement:
    { statement-seq? }
statement-seq:
    statement
    statement-seq statement
"""

import glrp
from ...parse import cxx98
from ....ast.statements import CompoundStatement
from motor_typing import TYPE_CHECKING


@glrp.rule('compound-statement : "{" statement-seq? "}"')
@cxx98
def compound_statement(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return CompoundStatement(p[1])


#@glrp.rule('compound-statement : "{" balanced-token-seq? "}"')
#@cxx98
#def compound_statement(self, p):
#    # type: (CxxParser, glrp.Production) -> Any
#    pass


@glrp.rule('statement-seq? : statement-seq? statement')
@cxx98
def statement_seq(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[0]
    result.append(p[1])
    return result


@glrp.rule('statement-seq? :')
@cxx98
def statement_seq_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return []


if TYPE_CHECKING:
    from typing import Any
    from ...parse import CxxParser