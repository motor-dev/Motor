"""
conversion-function-id:
    operator conversion-type-id

conversion-type-id:
    type-specifier-seq conversion-declarator?

conversion-declarator:
    ptr-operator conversion-declarator?
"""

import glrp
from typing import Any
from ...parse import CxxParser, cxx98
from ....ast.reference import ConversionOperatorId
from ....ast.type import TypeIdDeclarator, DeclaratorElementAbstract


@glrp.rule('conversion-function-id : operator conversion-type-id')
@cxx98
def conversion_function_id(self: CxxParser, p: glrp.Production) -> Any:
    return ConversionOperatorId(p[0].position, p[1])


@glrp.rule('conversion-type-id : type-specifier-seq')
@cxx98
def conversion_type_id(self: CxxParser, p: glrp.Production) -> Any:
    return TypeIdDeclarator(p[0], None)


@glrp.rule('conversion-type-id : [no-merge-warning] type-specifier-seq conversion-declarator')
@cxx98
def conversion_type_id_declarator(self: CxxParser, p: glrp.Production) -> Any:
    return TypeIdDeclarator(p[0], p[1])


@glrp.rule('conversion-declarator : ptr-operator conversion-declarator?')
@glrp.rule('conversion-declarator? : ptr-operator conversion-declarator?')
@cxx98
def conversion_declarator(self: CxxParser, p: glrp.Production) -> Any:
    klass = p[0][0]
    args = p[0][1]
    return klass(p[1], *args)


@glrp.rule('conversion-declarator? : ')
@cxx98
def conversion_declarator_opt(self: CxxParser, p: glrp.Production) -> Any:
    return DeclaratorElementAbstract()
