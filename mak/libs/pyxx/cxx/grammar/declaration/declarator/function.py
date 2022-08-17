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
from ....parser import cxx98, cxx11, cxx98_merge, cxx11_merge
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


@glrp.rule('parameter-declaration : parameter-declaration-proxy')
@cxx98
def parameter_declaration(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('parameter-declaration-proxy : attribute-specifier-seq? decl-specifier-seq declarator')
@glrp.rule(
    'parameter-declaration-proxy : attribute-specifier-seq? decl-specifier-seq declarator "=" initializer-clause'
)
@glrp.rule('parameter-declaration-proxy : attribute-specifier-seq? decl-specifier-seq abstract-declarator?')
@glrp.rule(
    'parameter-declaration-proxy : attribute-specifier-seq? decl-specifier-seq abstract-declarator? "=" initializer-clause'
)
@cxx98
def parameter_declaration_proxy(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('parameter-declaration-proxy : attribute-specifier-seq? decl-specifier-seq abstract-pack-declarator')
@glrp.rule(
    'parameter-declaration-proxy : attribute-specifier-seq? decl-specifier-seq abstract-pack-declarator "=" initializer-clause'
)
@cxx11
def parameter_declaration_proxy_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('"..."? : "..."')
@glrp.rule('"..."? : ')
@cxx98
def ellipsis_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.merge('parameter-declaration-list?')
@cxx11_merge
def ambiguous_parameter_declaration_list_opt(self, pack_declarator, declarator_end):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('parameter-declaration-proxy')
@cxx98_merge
def ambiguous_parameter_declaration(self, ambiguous_declarator, ambiguous_nested_name_specifier):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('parameter-declaration-proxy')
@cxx98_merge
def ambiguous_parameter_declaration_2(self, ambiguous_abstract_declarator_opt, noptr_declarator):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


@glrp.merge('parameter-declaration-clause')
@cxx11_merge
def ambiguous_parameter_declaration_clause(self, ambiguous_parameter_declaration_list_opt, pack_declarator):
    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
    pass


if TYPE_CHECKING:
    from typing import Optional
    from ....parser import CxxParser