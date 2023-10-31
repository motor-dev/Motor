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
from typing import Any, List
from ...parse import CxxParser, cxx98, cxx98_merge
from ....ast.function import TryFunctionBody, StatementFunctionBody
from ....ast.statements import TryBlock, ExceptionHandler, ExceptionDeclarationError, ExceptionDeclarationTypeSpecifier, ExceptionDeclarationAny, AmbiguousExceptionDeclaration
from . import specification


@glrp.rule('try-block : "try" compound-statement handler-seq')
@cxx98
def try_block(self: CxxParser, p: glrp.Production) -> Any:
    return TryBlock(p[1], p[2])


@glrp.rule('function-try-block : "try" ctor-initializer? compound-statement handler-seq')
@cxx98
def function_try_block(self: CxxParser, p: glrp.Production) -> Any:
    return TryFunctionBody(StatementFunctionBody(p[1], p[2]), p[3])


@glrp.rule('handler-seq : handler handler-seq?')
@glrp.rule('handler-seq? : handler handler-seq?')
@cxx98
def handler_seq(self: CxxParser, p: glrp.Production) -> Any:
    result = p[1]
    if p[0] is not None:
        result.insert(0, p[0])
    return result


@glrp.rule('handler-seq? : ')
@cxx98
def handler_seq_opt(self: CxxParser, p: glrp.Production) -> Any:
    return []


@glrp.rule('handler : "catch" "(" exception-declaration ")" compound-statement')
@cxx98
def handler(self: CxxParser, p: glrp.Production) -> Any:
    return ExceptionHandler(p[2], p[4])


@glrp.rule('handler : "catch" "#error" compound-statement')
@cxx98
def handler_error(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule('handler : "catch" "(" "#error" ")" compound-statement')
@cxx98
def handler_error_2(self: CxxParser, p: glrp.Production) -> Any:
    return ExceptionHandler(ExceptionDeclarationError(), p[4])


@glrp.rule('exception-declaration : attribute-specifier-seq? [no-merge-warning] type-specifier-seq declarator')
@glrp.rule('exception-declaration : attribute-specifier-seq? [no-merge-warning] type-specifier-seq abstract-declarator')
@cxx98
def exception_declaration_declarator(self: CxxParser, p: glrp.Production) -> Any:
    return ExceptionDeclarationTypeSpecifier(p[0], p[1], p[2])


@glrp.rule('exception-declaration : attribute-specifier-seq? type-specifier-seq ')
@cxx98
def exception_declaration_no_declarator(self: CxxParser, p: glrp.Production) -> Any:
    return ExceptionDeclarationTypeSpecifier(p[0], p[1], None)


@glrp.rule('exception-declaration : "..."')
@cxx98
def exception_declaration_declarator_any(self: CxxParser, p: glrp.Production) -> Any:
    return ExceptionDeclarationAny()


@glrp.merge('exception-declaration')
@cxx98_merge
def ambiguous_exception_declaration(
    self: CxxParser, continue_declarator_list: List[Any], end_declarator_list: List[Any]
) -> Any:
    return AmbiguousExceptionDeclaration(continue_declarator_list + end_declarator_list)


@glrp.merge('exception-declaration')
@cxx98_merge
def ambiguous_exception_declaration_2(
    self: CxxParser, ambiguous_abstract_declarator_2: List[Any], ptr_declarator: List[Any]
) -> Any:
    return AmbiguousExceptionDeclaration(ambiguous_abstract_declarator_2 + ptr_declarator)
