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


@glrp.rule('parameter-declaration-clause : variadic-parameter-list?')
@glrp.rule('parameter-declaration-clause : [no-merge-warning]parameter-declaration-list variadic-parameter-list?')
@glrp.rule('parameter-declaration-clause : parameter-declaration-list "," variadic-parameter-list')
@cxx98
def parameter_declaration_clause(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('variadic-parameter-list : "..."')
@cxx98
def variadic_parameter_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('variadic-parameter-list? : "..."')
@glrp.rule('variadic-parameter-list? :')
@cxx98
def variadic_parameter_list_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('parameter-declaration-list : parameter-declaration')
@glrp.rule('parameter-declaration-list : parameter-declaration-list "," parameter-declaration')
@cxx98
def parameter_declaration_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('parameter-declaration : attribute-specifier-seq? [no-merge-warning] decl-specifier-seq declarator')
@glrp.rule(
    'parameter-declaration : attribute-specifier-seq? [no-merge-warning] decl-specifier-seq declarator "=" initializer-clause'
)
@glrp.rule('parameter-declaration : attribute-specifier-seq? [no-merge-warning] decl-specifier-seq abstract-declarator')
@glrp.rule(
    'parameter-declaration : attribute-specifier-seq? [no-merge-warning] decl-specifier-seq abstract-declarator "=" initializer-clause'
)
@glrp.rule('parameter-declaration : attribute-specifier-seq? decl-specifier-seq [split:end_declarator_list]')
@glrp.rule('parameter-declaration : attribute-specifier-seq? decl-specifier-seq "=" initializer-clause')
@cxx98
def parameter_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('"..."? : "..."')
@glrp.rule('"..."? : ')
@cxx98
def ellipsis_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('parameter-declaration')
@cxx98_merge
def ambiguous_parameter_declaration(self, ptr_declarator, ambiguous_abstract_declarator_2):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('parameter-declaration')
@cxx98_merge
def ambiguous_parameter_declaration_constraint(self, type_constraint, id_nontemplate):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('parameter-declaration-clause')
@cxx98_merge
def ambiguous_parameter_declaration_clause(self, continue_declarator_list, end_declarator_list):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ....parser import CxxParser