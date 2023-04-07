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
from typing import Any, List
from ....parse import CxxParser, cxx98, cxx98_merge, cxx23
from .....ast.declarations import AmbiguousDeclaration
from .....ast.function import SimpleParameterClause, ParameterDeclaration, AmbiguousParameterClause


@glrp.rule('parameter-declaration-clause : variadic-parameter-list?')
@cxx98
def parameter_declaration_clause_variadic(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleParameterClause([], p[0])


@glrp.rule('parameter-declaration-clause : [no-merge-warning]parameter-declaration-list variadic-parameter-list?')
@cxx98
def parameter_declaration_clause_end(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleParameterClause(p[0], p[1])


@glrp.rule('parameter-declaration-clause : parameter-declaration-list "," variadic-parameter-list')
@cxx98
def parameter_declaration_clause(self: CxxParser, p: glrp.Production) -> Any:
    return p[0], p[2]


@glrp.rule('variadic-parameter-list : "..."')
@glrp.rule('variadic-parameter-list? : "..."')
@cxx98
def variadic_parameter_list(self: CxxParser, p: glrp.Production) -> Any:
    return True


@glrp.rule('variadic-parameter-list? :')
@cxx98
def variadic_parameter_list_opt(self: CxxParser, p: glrp.Production) -> Any:
    return False


@glrp.rule('parameter-declaration-list : parameter-declaration')
@cxx98
def parameter_declaration_list_end(self: CxxParser, p: glrp.Production) -> Any:
    return [p[0]]


@glrp.rule('parameter-declaration-list : parameter-declaration-list "," parameter-declaration')
@cxx98
def parameter_declaration_list(self: CxxParser, p: glrp.Production) -> Any:
    return p[0] + [p[2]]


@glrp.rule('parameter-declaration : attribute-specifier-seq? "this"? [no-merge-warning] decl-specifier-seq declarator')
@glrp.rule(
    'parameter-declaration : attribute-specifier-seq? "this"? [no-merge-warning] decl-specifier-seq abstract-declarator'
)
@glrp.rule(
    '"parameter-declaration#" : attribute-specifier-seq? "this"? [no-merge-warning] decl-specifier-seq declarator'
)
@glrp.rule(
    '"parameter-declaration#" : attribute-specifier-seq? "this"? [no-merge-warning] decl-specifier-seq abstract-declarator'
)
@cxx98
def parameter_declaration_declarator(self: CxxParser, p: glrp.Production) -> Any:
    return ParameterDeclaration(p[0], p[2], p[3], None, p[1])


@glrp.rule(
    'parameter-declaration : attribute-specifier-seq? "this"? [no-merge-warning] decl-specifier-seq declarator "=" initializer-clause'
)
@glrp.rule(
    'parameter-declaration : attribute-specifier-seq? "this"? [no-merge-warning] decl-specifier-seq abstract-declarator "=" initializer-clause'
)
@glrp.rule(
    '"parameter-declaration#" : attribute-specifier-seq? "this"? [no-merge-warning] decl-specifier-seq declarator "=" "initializer-clause#"'
)
@glrp.rule(
    '"parameter-declaration#" : attribute-specifier-seq? "this"? [no-merge-warning] decl-specifier-seq abstract-declarator "=" "initializer-clause#"'
)
@cxx98
def parameter_declaration_declarator_initializer(self: CxxParser, p: glrp.Production) -> Any:
    return ParameterDeclaration(p[0], p[2], p[3], p[5], p[1])


@glrp.rule('parameter-declaration : attribute-specifier-seq? "this"? decl-specifier-seq "=" initializer-clause')
@glrp.rule('"parameter-declaration#" : attribute-specifier-seq? "this"? decl-specifier-seq "=" "initializer-clause#"')
@cxx98
def parameter_declaration_initializer(self: CxxParser, p: glrp.Production) -> Any:
    return ParameterDeclaration(p[0], p[2], None, p[4], p[1])


@glrp.rule(
    'parameter-declaration : attribute-specifier-seq? "this"? decl-specifier-seq [prec:nonassoc,0][split:end_declarator_list]'
)
@glrp.rule(
    '"parameter-declaration#" : attribute-specifier-seq? "this"? decl-specifier-seq [prec:nonassoc,0][split:end_declarator_list]'
)
@cxx98
def parameter_declaration(self: CxxParser, p: glrp.Production) -> Any:
    return ParameterDeclaration(p[0], p[2], None, None, p[1])


@glrp.rule('"this"? : ')
@cxx98
def this_opt(self: CxxParser, p: glrp.Production) -> Any:
    return False


@glrp.rule('"this"? : "this"')
@cxx23
def this_cxx23(self: CxxParser, p: glrp.Production) -> Any:
    return True


@glrp.rule('"..."? : "..."')
@cxx98
def ellipsis(self: CxxParser, p: glrp.Production) -> Any:
    return True


@glrp.rule('"..."? : ')
@cxx98
def ellipsis_opt(self: CxxParser, p: glrp.Production) -> Any:
    return False


@glrp.merge('parameter-declaration')
@cxx98_merge
def ambiguous_parameter_declaration(
    self: CxxParser, decl_specifier_seq_end: List[Any], decl_specifier_seq_continue: List[Any]
) -> Any:
    return AmbiguousDeclaration(decl_specifier_seq_end + decl_specifier_seq_continue)


@glrp.merge('parameter-declaration')
@cxx98_merge
def ambiguous_parameter_declaration_2(
    self: CxxParser, ptr_declarator: List[Any], ambiguous_abstract_declarator_2: List[Any]
) -> Any:
    return AmbiguousDeclaration(ptr_declarator + ambiguous_abstract_declarator_2)


@glrp.merge('parameter-declaration#')
@glrp.merge_result('ambiguous_parameter_declaration')
@cxx98_merge
def ambiguous_parameter_declaration_ext(
    self: CxxParser, decl_specifier_seq_end: List[Any], decl_specifier_seq_continue: List[Any]
) -> Any:
    return AmbiguousDeclaration(decl_specifier_seq_end + decl_specifier_seq_continue)


@glrp.merge('parameter-declaration#')
@glrp.merge_result('ambiguous_parameter_declaration_2')
@cxx98_merge
def ambiguous_parameter_declaration_ext_2(
    self: CxxParser, ptr_declarator: List[Any], ambiguous_abstract_declarator_2: List[Any]
) -> Any:
    return AmbiguousDeclaration(ptr_declarator + ambiguous_abstract_declarator_2)


@glrp.merge('parameter-declaration-clause')
@cxx98_merge
def ambiguous_parameter_declaration_clause(
    self: CxxParser, continue_declarator_list: List[Any], end_declarator_list: List[Any]
) -> Any:
    return AmbiguousParameterClause(continue_declarator_list + end_declarator_list)


@glrp.merge('parameter-declaration')
@cxx98_merge
def ambiguous_parameter_declaration_final(
    self: CxxParser, final_keyword: List[Any], final_identifier: List[Any]
) -> Any:
    if len(final_keyword) == 1:
        return final_keyword[0]
    elif len(final_keyword) > 1:
        return AmbiguousDeclaration(final_keyword)
    else:
        assert len(final_identifier) > 1
        return AmbiguousDeclaration(final_identifier)


@glrp.merge('parameter-declaration#')
@cxx98_merge
def ambiguous_parameter_declaration_ext_final(
    self: CxxParser, final_keyword: List[Any], final_identifier: List[Any]
) -> Any:
    if len(final_keyword) == 1:
        return final_keyword[0]
    elif len(final_keyword) > 1:
        return AmbiguousDeclaration(final_keyword)
    else:
        assert len(final_identifier) > 1
        return AmbiguousDeclaration(final_identifier)
