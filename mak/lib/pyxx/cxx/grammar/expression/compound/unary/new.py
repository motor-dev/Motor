"""
new-expression:
    ::? new new-placement? new-type-id new-initializer?
    ::? new new-placement? ( type-id ) new-initializer?

new-placement:
    ( expression-list )

new-type-id:
    type-specifier-seq new-declarator?

new-declarator:
    ptr-operator new-declarator?
    noptr-new-declarator

noptr-new-declarator:
    [ expression? ] attribute-specifier-seq?
    noptr-new-declarator [ constant-expression ] attribute-specifier-seq?

new-initializer:
    ( expression-list? )
    braced-init-list
"""

import glrp
from typing import Any
from .....parse import CxxParser, cxx98, cxx11
from ......ast.expressions import NewExpression, ParenthesizedExpression, ErrorExpression
from ......ast.type import AbstractDeclaratorList, TypeIdDeclarator, DeclaratorElementArray, DeclaratorElementAbstract, \
    DeclaratorElementError


@glrp.rule('constant-expression : "::"? "new" new-type-id new-initializer?')
@glrp.rule('constant-expression# : "::"? "new" new-type-id new-initializer?')
@cxx98
def new_expression(self: CxxParser, p: glrp.Production) -> Any:
    return NewExpression(p[2], None, p[3], bool(p[0]), False)


@glrp.rule('constant-expression : "::"? "new" "(" begin-type-id type-id ")" new-initializer?')
@glrp.rule('constant-expression# : "::"? "new" "(" begin-type-id type-id ")" new-initializer?')
@cxx98
def new_expression_type_id(self: CxxParser, p: glrp.Production) -> Any:
    return NewExpression(p[4], None, p[6], bool(p[0]), True)


@glrp.rule('constant-expression : "::"? "new" "(" begin-type-id "#error" ")" new-initializer?')
@glrp.rule('constant-expression# : "::"? "new" new-placement "(" "#error" ")" new-initializer?')
@glrp.rule('constant-expression : "::"? "new" new-placement "(" "#error" ")" new-initializer?')
@glrp.rule('constant-expression# : "::"? "new" "(" begin-type-id "#error" ")" new-initializer?')
@cxx98
def new_expression_type_id_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('constant-expression : "::"? "new" new-placement new-type-id new-initializer?')
@glrp.rule('constant-expression# : "::"? "new" new-placement new-type-id new-initializer?')
@cxx98
def new_expression_placement(self: CxxParser, p: glrp.Production) -> Any:
    return NewExpression(p[3], p[2], p[4], bool(p[0]), False)


@glrp.rule('constant-expression : "::"? "new" new-placement "(" type-id ")" new-initializer?')
@glrp.rule('constant-expression# : "::"? "new" new-placement "(" type-id ")" new-initializer?')
@cxx98
def new_expression_placement_type_id(self: CxxParser, p: glrp.Production) -> Any:
    return NewExpression(p[4], p[2], p[6], bool(p[0]), True)


@glrp.rule('new-placement : "(" begin-expression expression-list ")"')
@cxx98
def new_placement(self: CxxParser, p: glrp.Production) -> Any:
    return ParenthesizedExpression(p[2])


@glrp.rule('new-placement : "(" begin-expression "#error" ")"')
@cxx98
def new_placement_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('new-type-id : type-specifier-seq')
@cxx98
def new_type_id(self: CxxParser, p: glrp.Production) -> Any:
    return TypeIdDeclarator(p[0], None)


@glrp.rule('new-type-id : [no-merge-warning]type-specifier-seq new-declarator')
@cxx98
def new_type_id_declarator(self: CxxParser, p: glrp.Production) -> Any:
    return TypeIdDeclarator(p[0], p[1])


@glrp.rule('new-declarator : ptr-operator')
@cxx98
def new_declarator_ptr(self: CxxParser, p: glrp.Production) -> Any:
    return AbstractDeclaratorList(p[0][0](DeclaratorElementAbstract(), *p[0][1]))


@glrp.rule('new-declarator : ptr-operator new-declarator')
@cxx98
def new_declarator_recursive(self: CxxParser, p: glrp.Production) -> Any:
    return AbstractDeclaratorList(p[0][0](p[1], *p[0][1]))


@glrp.rule('new-declarator : noptr-new-declarator')
@cxx98
def new_declarator_noptr(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('noptr-new-declarator : [prec:left,16]"[" expression? "]" attribute-specifier-seq?')
@cxx98
def noptr_new_declarator_array(self: CxxParser, p: glrp.Production) -> Any:
    return DeclaratorElementArray(DeclaratorElementAbstract(), p[1], p[3])


@glrp.rule('noptr-new-declarator : [prec:left,16]"[" "#error" "]" attribute-specifier-seq?')
@cxx98
def noptr_new_declarator_array_error(self: CxxParser, p: glrp.Production) -> Any:
    return DeclaratorElementError(DeclaratorElementAbstract(), False)


@glrp.rule(
    'noptr-new-declarator : noptr-new-declarator [prec:left,16]"[" constant-expression "]" attribute-specifier-seq?')
@cxx98
def noptr_new_declarator_array_2(self: CxxParser, p: glrp.Production) -> Any:
    return DeclaratorElementArray(p[0], p[2], p[4])


@glrp.rule('noptr-new-declarator : noptr-new-declarator [prec:left,16]"[" "#error" "]" attribute-specifier-seq?')
@cxx98
def noptr_new_declarator_array_2_error(self: CxxParser, p: glrp.Production) -> Any:
    return DeclaratorElementError(p[0], False)


@glrp.rule('new-initializer? : [prec:left,1]"(" expression-list? ")"')
@cxx98
def new_initializer(self: CxxParser, p: glrp.Production) -> Any:
    return ParenthesizedExpression(p[1])


@glrp.rule('new-initializer? : [prec:left,1]"(" "#error" ")"')
@cxx98
def new_initializer_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('new-initializer?[prec:right,0] : ')
@cxx98
def new_initializer_opt(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule('new-initializer? : begin-new-initializer braced-init-list')
@cxx11
def new_initializer_opt_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return p[1]


@glrp.rule('begin-new-initializer[prec:right,1] : ')
@cxx11
def begin_new_initializer_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    pass
