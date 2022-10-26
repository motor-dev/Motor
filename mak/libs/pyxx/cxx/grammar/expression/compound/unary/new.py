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
from .....parser import cxx98, cxx11, cxx98_merge
from ......ast.expressions import AmbiguousExpression, NewExpression
from ......ast.types import AbstractDeclaratorList, TypeIdDeclarator, AmbiguousTypeId, DeclaratorElementArray
from motor_typing import TYPE_CHECKING


@glrp.rule('new-expression : "::"? "new" new-type-id new-initializer?')
@cxx98
def new_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return NewExpression(p[2], None, p[3], bool(p[0]))


@glrp.rule('new-expression : "::"? "new" "(" begin-type-id type-id ")" new-initializer?')
@cxx98
def new_expression_type_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return NewExpression(p[4], None, p[6], bool(p[0]))


@glrp.rule('new-expression : "::"? "new" new-placement new-type-id new-initializer?')
@cxx98
def new_expression_placement(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return NewExpression(p[3], p[2], p[4], bool(p[0]))


@glrp.rule('new-expression : "::"? "new" new-placement "(" type-id ")" new-initializer?')
@cxx98
def new_expression_placement_type_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return NewExpression(p[4], p[2], p[6], bool(p[0]))


@glrp.rule('new-placement : "(" begin-expression expression-list ")"')
@cxx98
def new_placement(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[2]


@glrp.rule('new-type-id : type-specifier-seq')
@cxx98
def new_type_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeIdDeclarator(p[0], None)


@glrp.rule('new-type-id : [no-merge-warning]type-specifier-seq new-declarator')
@cxx98
def new_type_id_declarator(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeIdDeclarator(p[0], p[1])


@glrp.rule('new-declarator : ptr-operator')
@cxx98
def new_declarator_ptr(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = AbstractDeclaratorList()
    result.add(p[0])
    return result


@glrp.rule('new-declarator : ptr-operator new-declarator')
@cxx98
def new_declarator_recursive(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[1]
    result.add(p[0])
    return result


@glrp.rule('new-declarator : noptr-new-declarator')
@cxx98
def new_declarator_noptr(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('noptr-new-declarator : "[" expression? "]" attribute-specifier-seq?')
@cxx98
def noptr_new_declarator_array(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    #result = AbstractDeclaratorList()
    #result.add(DeclaratorElementArray(p[1], p[3]))
    #return result
    pass


@glrp.rule('noptr-new-declarator : noptr-new-declarator "[" constant-expression "]" attribute-specifier-seq?')
@cxx98
def noptr_new_declarator_array_2(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[0]
    result.add(DeclaratorElementArray(p[2], p[4]))
    return result


@glrp.rule('new-initializer? : "(" expression-list? ")"')
@cxx98
def new_initializer(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[1]


@glrp.rule('new-initializer?[prec:right,0] : ')
@cxx98
def new_initializer_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return None


@glrp.rule('new-initializer? : begin-new-initializer braced-init-list')
@cxx11
def new_initializer_opt_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('begin-new-initializer[prec:right,1] : ')
@cxx11
def begin_new_initializer_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.merge('new-expression')
@cxx98_merge
def ambiguous_new_expression(self, type_id, expression):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    expressions = type_id + expression
    return AmbiguousExpression(expressions)


if TYPE_CHECKING:
    from typing import Any, List
    from .....parser import CxxParser