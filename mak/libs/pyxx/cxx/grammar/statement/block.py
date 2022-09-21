"""
compound-statement:
    { statement-seq? }
statement-seq:
    statement
    statement-seq statement
"""

import glrp
from ...parser import cxx98
from motor_typing import TYPE_CHECKING


@glrp.rule('compound-statement : "{" statement-seq? "}"')
@cxx98
def compound_statement(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('statement-seq? : statement-seq? statement')
@glrp.rule('statement-seq? :')
@cxx98
def statement_seq_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ...parser import CxxParser