"""
declarator:
    ptr-declarator
    noptr-declarator parameters-and-qualifiers trailing-return-type

ptr-declarator:
    noptr-declarator
    ptr-operator ptr-declarator

noptr-declarator:
    declarator-id attribute-specifier-seq?
    noptr-declarator parameters-and-qualifiers
    noptr-declarator [ constant-expression? ] attribute-specifier-seq?
    ( ptr-declarator )

parameters-and-qualifiers:
    ( parameter-declaration-clause ) cv-qualifier-seq? ref-qualifier? noexcept-specifier? attribute-specifier-seq?

trailing-return-type:
    -> type-id

ptr-operator:
    * attribute-specifier-seq? cv-qualifier-seq?
    & attribute-specifier-seq?
    && attribute-specifier-seq?
    nested-name-specifier * attribute-specifier-seq? cv-qualifier-seq?

cv-qualifier-seq:
    cv-qualifier cv-qualifier-seq?

cv-qualifier:
    const
    volatile

ref-qualifier:
    &
    &&

declarator-id:
    ...? id-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98, cxx11
from .....ast.type import (
    CvQualifiers,
    RefQualifiers,
    DeclaratorList,
    DeclaratorElementError,
    DeclaratorElementId,
    DeclaratorElementPackId,
    DeclaratorElementGroup,
    DeclaratorElementArray,
    DeclaratorElementPointer,
    DeclaratorElementReference,
    DeclaratorElementRValueReference,
    DeclaratorElementMethod,
    DeclaratorElementAbstract,
)


@glrp.rule('declarator : ptr-declarator')
@cxx98
def declarator(self: CxxParser, p: glrp.Production) -> Any:
    return DeclaratorList(p[0])


@glrp.rule('declarator : noptr-declarator parameters-and-qualifiers trailing-return-type')
@cxx11
def declarator_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    if p[1] is None:
        return DeclaratorList(DeclaratorElementError(p[0], True))
    else:
        return DeclaratorList(DeclaratorElementMethod(p[0], p[1][0], p[2], p[1][1], p[1][2], p[1][3], p[1][4]))


@glrp.rule('ptr-declarator : noptr-declarator [prec:nonassoc,0][split:end_declarator_list]')
@cxx98
def ptr_declarator_noptr(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('ptr-declarator : ptr-operator ptr-declarator')
@cxx98
def ptr_declarator(self: CxxParser, p: glrp.Production) -> Any:
    klass = p[0][0]
    arguments = p[0][1]
    return klass(p[1], *arguments)


@glrp.rule('noptr-declarator : declarator-id attribute-specifier-seq?')
@cxx98
def noptr_declarator_id(self: CxxParser, p: glrp.Production) -> Any:
    if p[0][0]:
        return DeclaratorElementPackId(p[0][1], p[1])
    else:
        return DeclaratorElementId(p[0][1], p[1])


@glrp.rule('noptr-declarator : noptr-declarator parameters-and-qualifiers')
@cxx98
def noptr_declarator_method(self: CxxParser, p: glrp.Production) -> Any:
    if p[1] is None:
        return DeclaratorElementError(p[0], True)
    else:
        return DeclaratorElementMethod(p[0], p[1][0], None, p[1][1], p[1][2], p[1][3], p[1][4])


@glrp.rule('noptr-declarator : noptr-declarator "[" constant-expression? "]" attribute-specifier-seq?')
@cxx98
def noptr_declarator_array(self: CxxParser, p: glrp.Production) -> Any:
    return DeclaratorElementArray(p[0], p[2], p[4])


@glrp.rule('noptr-declarator : "(" begin-ptr-declarator ptr-declarator ")"')
@cxx98
def noptr_declarator(self: CxxParser, p: glrp.Production) -> Any:
    return DeclaratorElementGroup(p[2])


@glrp.rule(
    'parameters-and-qualifiers : [prec:nonassoc,0][split:continue_declarator_list]"(" begin-parameter-declaration-clause parameter-declaration-clause ")" cv-qualifier-seq? ref-qualifier? exception-specification? attribute-specifier-seq?'
)
@cxx98
def parameters_and_qualifiers(self: CxxParser, p: glrp.Production) -> Any:
    return (p[2], p[4], p[5], p[6], p[7])


@glrp.rule(
    'parameters-and-qualifiers : [prec:nonassoc,0][split:continue_declarator_list]"(" begin-parameter-declaration-clause  "#error" ")" cv-qualifier-seq? ref-qualifier? exception-specification? attribute-specifier-seq?'
)
@cxx98
def parameters_and_qualifiers_error(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule('trailing-return-type : "->" type-id')
@glrp.rule('trailing-return-type? : "->" type-id')
@cxx11
def trailing_return_type(self: CxxParser, p: glrp.Production) -> Any:
    return p[1]


@glrp.rule('trailing-return-type? : ')
@cxx11
def trailing_return_type_opt(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule('ptr-operator : [prec:left,1]"*" attribute-specifier-seq? cv-qualifier-seq?')
@cxx98
def ptr_operator(self: CxxParser, p: glrp.Production) -> Any:
    return DeclaratorElementPointer, (None, p[1], p[2])


@glrp.rule('ptr-operator : nested-name-specifier "*" attribute-specifier-seq? cv-qualifier-seq?')
@cxx98
def ptr_operator_qualified_ptr(self: CxxParser, p: glrp.Production) -> Any:
    return DeclaratorElementPointer, (p[0], p[2], p[3])


@glrp.rule('ptr-operator : [prec:left,1]"&" attribute-specifier-seq?')
@cxx98
def ptr_operator_ref(self: CxxParser, p: glrp.Production) -> Any:
    return DeclaratorElementReference, (p[1],)


@glrp.rule('ptr-operator : [prec:left,1]"&&" attribute-specifier-seq?')
@cxx11
def ptr_operator_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return DeclaratorElementRValueReference, (p[1],)


@glrp.rule('cv-qualifier-seq? : cv-qualifier cv-qualifier-seq?')
@cxx98
def cv_qualifier_seq(self: CxxParser, p: glrp.Production) -> Any:
    return [p[0]] + p[1]


@glrp.rule('cv-qualifier-seq? :')
@cxx98
def cv_qualifier_seq_opt(self: CxxParser, p: glrp.Production) -> Any:
    return []


@glrp.rule('cv-qualifier : "const"')
@cxx98
def cv_qualifier_const(self: CxxParser, p: glrp.Production) -> Any:
    return CvQualifiers.CONST


@glrp.rule('cv-qualifier : "volatile"')
@cxx98
def cv_qualifier_volatile(self: CxxParser, p: glrp.Production) -> Any:
    return CvQualifiers.VOLATILE


@glrp.rule('ref-qualifier? : "&"')
@cxx98
def ref_qualifier(self: CxxParser, p: glrp.Production) -> Any:
    return RefQualifiers.REF


@glrp.rule('ref-qualifier? :')
@cxx98
def ref_qualifier_opt(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule('ref-qualifier? : "&&"')
@cxx11
def ref_qualifier_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return RefQualifiers.RREF


@glrp.rule('declarator-id : id-expression')
@cxx98
def declarator_id(self: CxxParser, p: glrp.Production) -> Any:
    return (False, p[0])


@glrp.rule('declarator-id : [prec:nonassoc,0][split:continue_declarator_list]"..." id-expression')
@cxx11
def declarator_id_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return (True, p[1])


@glrp.rule('begin-ptr-declarator : [split:ptr_declarator]')
@cxx98
def begin_ptr_declarator(self: CxxParser, p: glrp.Production) -> Any:
    pass


@glrp.rule('begin-parameter-declaration-clause : [split:parameter_declaration_clause]')
@cxx98
def begin_parameter_declaration_clause(self: CxxParser, p: glrp.Production) -> Any:
    pass
