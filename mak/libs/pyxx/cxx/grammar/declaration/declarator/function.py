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


@glrp.rule('parameter-declaration-clause : ')
@glrp.rule('parameter-declaration-clause : parameter-declaration-list')
@glrp.rule('parameter-declaration-clause : parameter-declaration-list "," variadic-parameter-list')
@glrp.rule('parameter-declaration-clause : variadic-parameter-list')
@glrp.rule('parameter-declaration-clause : parameter-declaration-list variadic-parameter-list')
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


@glrp.rule('parameter-declaration-list? : parameter-declaration')
@glrp.rule('parameter-declaration-list? : parameter-declaration-list "," parameter-declaration')
@glrp.rule('parameter-declaration-list? : ')
@cxx98
def parameter_declaration_list_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.rule('parameter-declaration : parameter-declaration-declarator')
@glrp.rule('parameter-declaration : parameter-declaration-no-declarator')
@glrp.rule(
    'parameter-declaration-declarator : attribute-specifier-seq? [no-merge-warning]decl-specifier-seq begin-declarator-no-initializer declarator'
)
@glrp.rule(
    'parameter-declaration-declarator : attribute-specifier-seq? [no-merge-warning]decl-specifier-seq begin-declarator-initializer declarator "=" initializer-clause'
)
@glrp.rule(
    'parameter-declaration-declarator : attribute-specifier-seq? [no-merge-warning]decl-specifier-seq begin-declarator-no-initializer abstract-declarator'
)
@glrp.rule(
    'parameter-declaration-declarator : attribute-specifier-seq? [no-merge-warning]decl-specifier-seq begin-declarator-initializer abstract-declarator "=" initializer-clause'
)
@glrp.rule('parameter-declaration-no-declarator : attribute-specifier-seq? decl-specifier-seq begin-no-declarator')
@glrp.rule(
    'parameter-declaration-no-declarator : attribute-specifier-seq? decl-specifier-seq begin-no-declarator "=" initializer-clause'
)
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


@glrp.merge('parameter-declaration-list')
@cxx98_merge
def ambiguous_parameter_declaration_list_opt(
    self, ambiguous_parameter_declaration_declarator_initializer, declarator_initializer, no_declarator
):
    # type: (CxxParser, List[Any], List[Any],  List[Any]) -> Any
    pass


@glrp.merge('parameter-declaration')
@cxx98_merge
def ambiguous_parameter_declaration_declarator(self, decl_specifier_seq_end, decl_specifier_seq_continue):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('parameter-declaration-declarator')
@cxx98_merge
def ambiguous_parameter_declaration_declarator_initializer(self, declarator_no_initializer, declarator_initializer):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('parameter-declaration-declarator')
@cxx98_merge
def ambiguous_parameter_declaration_2(self, ambiguous_abstract_declarator_2, ptr_declarator):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('parameter-declaration-clause-variadic')
@cxx98_merge
def ambiguous_parameter_declaration_clause_variadic(
    self, ambiguous_parameter_declaration_declarator_initializer, no_declarator
):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    pass


@glrp.merge('parameter-declaration-clause')
@cxx98_merge
def ambiguous_parameter_declaration_clause(
    self, ambiguous_parameter_declaration_declarator_initializer, ambiguous_parameter_declaration_clause_variadic,
    ambiguous_parameter_declaration_list_opt
):
    # type: (CxxParser, List[Any], List[Any], List[Any]) -> Any
    pass


if TYPE_CHECKING:
    from typing import Any, List
    from ....parser import CxxParser