"""
try-block:
    try compound-statement handler-seq

function-try-block:
    try ctor-initializer? compound-statement handler-seq

handler-seq:
    handler handler-seq?

handler:
    catch ( exception-declaration ) compound-statement

exception-declaration:
    attribute-specifier-seq? type-specifier-seq declarator
    attribute-specifier-seq? type-specifier-seq abstract-declarator?
    ...
"""

import glrp
from ...parser import cxx98, cxx98_merge
from motor_typing import TYPE_CHECKING
from . import specification


@glrp.rule('try-block : "try" compound-statement handler-seq')
@cxx98
def try_block(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('function-try-block : "try" ctor-initializer? compound-statement handler-seq')
@cxx98
def function_try_block(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('handler-seq : handler handler-seq?')
@cxx98
def handler_seq(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('handler-seq? : handler handler-seq?')
@glrp.rule('handler-seq? : ')
@cxx98
def handler_seq_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('handler : "catch" "(" exception-declaration ")" compound-statement')
@cxx98
def handler(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('exception-declaration : begin-exception-declaration-declarator exception-declaration-declarator')
@glrp.rule('exception-declaration : begin-exception-declaration-no-declarator exception-declaration-no-declarator')
@glrp.rule(
    'exception-declaration : begin-exception-declaration-abstract-declarator exception-declaration-abstract-declarator'
)
@glrp.rule(
    'exception-declaration-declarator : attribute-specifier-seq? begin-type-id-declarator [no-merge-warning] type-specifier-seq declarator'
)
@glrp.rule(
    'exception-declaration-no-declarator : attribute-specifier-seq? begin-type-id-no-declarator type-specifier-seq'
)
@glrp.rule(
    'exception-declaration-abstract-declarator : attribute-specifier-seq? begin-type-id-abstract-declarator [no-merge-warning] type-specifier-seq abstract-declarator'
)
@glrp.rule('exception-declaration-no-declarator : "..."')
@cxx98
def exception_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('begin-exception-declaration-declarator : [split:exception_declaration_declarator]')
@glrp.rule('begin-exception-declaration-no-declarator : [split:exception_declaration_no_declarator]')
@glrp.rule('begin-exception-declaration-abstract-declarator : [split:exception_declaration_abstract_declarator]')
@cxx98
def begin_exception_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('exception-declaration-declarator')
@cxx98_merge
def ambiguous_exception_declaration_declarator(self, type_specifier_seq_end, type_specifier_seq_continue):
    # type: (CxxParser, List[Any], List[Any]) -> None
    pass


@glrp.merge('exception-declaration-abstract-declarator')
@cxx98_merge
def ambiguous_exception_declaration_abstract_declarator(self, type_specifier_seq_end, type_specifier_seq_continue):
    # type: (CxxParser, List[Any], List[Any]) -> None
    pass


@glrp.merge('exception-declaration')
@cxx98_merge
def ambiguous_exception_declaration(
    self, exception_declaration_declarator, exception_declaration_no_declarator,
    exception_declaration_abstract_declarator
):
    # type: (CxxParser, List[Any], List[Any], List[Any]) -> None
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ...parser import CxxParser