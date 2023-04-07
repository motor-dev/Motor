"""
compound-statement:
    { statement-seq? }
statement-seq:
    statement
    statement-seq statement
"""

import glrp
from typing import Any
from ...parse import CxxParser, cxx98
from ....ast.statements import CompoundStatement, ErrorStatement


@glrp.rule('compound-statement : "{" statement-seq? "}"')
@cxx98
def compound_statement(self: CxxParser, p: glrp.Production) -> Any:
    return CompoundStatement(p[1])


@glrp.rule('compound-statement : "{" statement-seq? [prec:right,-1]"#error" "}"')
@cxx98
def compound_statement_error(self: CxxParser, p: glrp.Production) -> Any:
    return CompoundStatement(p[1] + [ErrorStatement()])


#@glrp.rule('compound-statement : "{" balanced-token-seq? "}"')
#@cxx98
#def compound_statement(self: CxxParser, p: glrp.Production) -> Any:
#    pass


@glrp.rule('statement-seq? : statement-seq? statement')
@cxx98
def statement_seq(self: CxxParser, p: glrp.Production) -> Any:
    result = p[0]
    result.append(p[1])
    return result


@glrp.rule('statement-seq? :')
@cxx98
def statement_seq_opt(self: CxxParser, p: glrp.Production) -> Any:
    return []
