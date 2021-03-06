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
from ....parser import cxx98, cxx11, cxx98_merge
from motor_typing import TYPE_CHECKING


@glrp.rule('declarator : ptr-declarator')
@cxx98
def declarator(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('declarator : noptr-declarator parameters-and-qualifiers trailing-return-type')
@cxx11
def declarator_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('ptr-declarator : noptr-declarator[split:declarator_end]')
@glrp.rule('ptr-declarator : ptr-operator ptr-declarator')
@cxx98
def ptr_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('noptr-declarator : declarator-id attribute-specifier-seq?')
@glrp.rule('noptr-declarator : noptr-declarator parameters-and-qualifiers')
@glrp.rule('noptr-declarator : noptr-declarator "[" constant-expression? "]" attribute-specifier-seq?')
@glrp.rule('noptr-declarator : "(" noptr-declarator-disambiguation ptr-declarator ")"')
@cxx98
def noptr_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('noptr-declarator-disambiguation[split:noptr_declarator] :')
@cxx98
def noptr_declarator_disambiguation(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule(
    'parameters-and-qualifiers : [split:declarator_continue]"(" parameters-and-qualifiers-disambiguation parameter-declaration-clause ")" cv-qualifier-seq? ref-qualifier? exception-specification? attribute-specifier-seq?'
)
@cxx98
def parameters_and_qualifiers(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('parameters-and-qualifiers-disambiguation[split:parameters_and_qualifiers] :')
@cxx98
def parameters_and_qualifiers_disambiguation(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('trailing-return-type : "->" type-id')
@cxx11
def trailing_return_type(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('trailing-return-type? : "->" type-id')
@glrp.rule('trailing-return-type? : ')
@cxx11
def trailing_return_type_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('ptr-operator : [prec:left,1]"*" attribute-specifier-seq? cv-qualifier-seq?')
@glrp.rule('ptr-operator : nested-name-specifier "*" attribute-specifier-seq? cv-qualifier-seq?')
@glrp.rule('ptr-operator : [prec:left,1]"&" attribute-specifier-seq?')
@cxx98
def ptr_operator(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('ptr-operator : [prec:left,1]"&&" attribute-specifier-seq?')
@cxx11
def ptr_operator_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('cv-qualifier-seq? : cv-qualifier cv-qualifier-seq?')
@glrp.rule('cv-qualifier-seq? :')
@cxx98
def cv_qualifier_seq_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('cv-qualifier : "const"')
@glrp.rule('cv-qualifier : "volatile"')
@cxx98
def cv_qualifier(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('ref-qualifier? : "&"')
@glrp.rule('ref-qualifier? :')
@cxx98
def ref_qualifier_opt(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('ref-qualifier? : "&&"')
@cxx11
def ref_qualifier_opt_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('declarator-id : id-expression')
@cxx98
def declarator_id(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


@glrp.rule('declarator-id : [split:pack_declarator]"..." id-expression')
@cxx11
def declarator_id_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> None
    pass


#@glrp.merge('declarator-id')
#@cxx98_merge
#def generic_declarator_id(self, generic_nested_name_specifier, generic_id_expression):
#    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
#    pass

#@glrp.merge('declarator')
#@cxx98_merge
#def generic_declarator(self, generic_nested_name_specifier, generic_declarator_id):
#    # type: (CxxParser, Optional[glrp.Production], Optional[glrp.Production]) -> None
#    pass

if TYPE_CHECKING:
    from motor_typing import Optional
    from ....parser import CxxParser