"""
parameter-declaration-clause:
    parameter-declaration-list? ...?
    parameter-declaration-list , ...

parameter-declaration-list:
    parameter-declaration
    parameter-declaration-list , parameter-declaration

parameter-declaration:
    attribute-specifier-seq? decl-specifier-seq declarator
    attribute-specifier-seq? decl-specifier-seq declarator = initializer-clause
    attribute-specifier-seq? decl-specifier-seq abstract-declarator?
    attribute-specifier-seq? decl-specifier-seq abstract-declarator? = initializer-clause
"""

import glrp
from ....parser import cxx98, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('parameter-declaration-clause : parameter-declaration-list? variadic-parameter-list?')
@glrp.rule('parameter-declaration-clause : parameter-declaration-list "," variadic-parameter-list')
@cxx98
def parameter_declaration_clause(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('variadic-parameter-list : "..."')
@cxx98
def variadic_parameter_list(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('variadic-parameter-list? : "..."')
@glrp.rule('variadic-parameter-list? :')
@cxx98
def variadic_parameter_list_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('parameter-declaration-list : parameter-declaration')
@glrp.rule('parameter-declaration-list : parameter-declaration-list "," parameter-declaration')
@cxx98
def parameter_declaration_list(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('parameter-declaration-list? : parameter-declaration')
@glrp.rule('parameter-declaration-list? : parameter-declaration-list "," parameter-declaration')
@glrp.rule('parameter-declaration-list? : ')
@cxx98
def parameter_declaration_list_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('parameter-declaration : parameter-declaration-declarator')
@glrp.rule('parameter-declaration : parameter-declaration-no-declarator')
@glrp.rule('parameter-declaration : parameter-declaration-abstract-declarator')
@glrp.rule(
    'parameter-declaration-declarator : begin-parameter-declaration-declarator attribute-specifier-seq? [no-merge-warning]decl-specifier-seq declarator'
)
@glrp.rule(
    'parameter-declaration-declarator : begin-parameter-declaration-declarator attribute-specifier-seq? [no-merge-warning]decl-specifier-seq declarator "=" initializer-clause'
)
@glrp.rule(
    'parameter-declaration-no-declarator : begin-parameter-declaration-no-declarator attribute-specifier-seq? decl-specifier-seq'
)
@glrp.rule(
    'parameter-declaration-no-declarator : begin-parameter-declaration-no-declarator attribute-specifier-seq? decl-specifier-seq "=" initializer-clause'
)
@glrp.rule(
    'parameter-declaration-abstract-declarator : begin-parameter-declaration-abstract-declarator attribute-specifier-seq? [no-merge-warning]decl-specifier-seq abstract-declarator'
)
@glrp.rule(
    'parameter-declaration-abstract-declarator : begin-parameter-declaration-abstract-declarator attribute-specifier-seq? [no-merge-warning]decl-specifier-seq abstract-declarator "=" initializer-clause'
)
@cxx98
def parameter_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('begin-parameter-declaration-declarator : [split:parameter_declaration_declarator]')
@glrp.rule('begin-parameter-declaration-no-declarator : [split:parameter_declaration_no_declarator]')
@glrp.rule('begin-parameter-declaration-abstract-declarator : [split:parameter_declaration_abstract_declarator]')
@cxx98
def begin_parameter_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('"..."? : "..."')
@glrp.rule('"..."? : ')
@cxx98
def ellipsis_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('parameter-declaration-declarator')
@cxx98_merge
def ambiguous_parameter_declaration_declarator(self, decl_specifier_seq_end, decl_specifier_seq_continue):
    # type: (CxxParser, Any, Any) -> Any
    pass


@glrp.merge('parameter-declaration-abstract-declarator')
@cxx98_merge
def ambiguous_parameter_declaration_abstract_declarator(self, decl_specifier_seq_end, decl_specifier_seq_continue):
    # type: (CxxParser, Any, Any) -> Any
    pass


@glrp.merge('parameter-declaration')
@cxx98_merge
def ambiguous_parameter_declaration(
    self, parameter_declaration_declarator, parameter_declaration_no_declarator,
    parameter_declaration_abstract_declarator
):
    # type: (CxxParser, Any, Any, Any) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any
    from ....parser import CxxParser