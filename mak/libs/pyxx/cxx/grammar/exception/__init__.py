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


@glrp.rule('exception-declaration : attribute-specifier-seq? [no-merge-warning] type-specifier-seq declarator')
@glrp.rule('exception-declaration : attribute-specifier-seq? type-specifier-seq [split:end_declarator_list]')
@glrp.rule('exception-declaration : attribute-specifier-seq? [no-merge-warning] type-specifier-seq abstract-declarator')
@glrp.rule('exception-declaration : "..."')
@cxx98
def exception_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('exception-declaration')
@cxx98_merge
def ambiguous_exception_declaration(self, continue_declarator_list, end_declarator_list):
    # type: (CxxParser, List[Any], List[Any]) -> None
    pass


@glrp.merge('exception-declaration')
@cxx98_merge
def ambiguous_exception_declaration_2(self, type_specifier_seq_continue, type_specifier_seq_end):
    # type: (CxxParser, List[Any], List[Any]) -> None
    pass


@glrp.merge('exception-declaration')
@cxx98_merge
def ambiguous_exception_declaration_3(
    self, ambiguous_noptr_abstract_declarator, ambiguous_abstract_declarator_2, ptr_declarator
):
    # type: (CxxParser, List[Any], List[Any], List[Any]) -> None
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ...parser import CxxParser