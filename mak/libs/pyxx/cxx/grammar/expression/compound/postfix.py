"""
postfix-expression:
    primary-expression
    postfix-expression [ expr-or-braced-init-list ]
    postfix-expression ( expression-list? )
    simple-type-specifier ( expression-list? )
    typename-specifier ( expression-list? )
    simple-type-specifier braced-init-list
    typename-specifier braced-init-list
    postfix-expression . template? id-expression
    postfix-expression -> template? id-expression
    postfix-expression ++
    postfix-expression --
    dynamic_cast < type-id > ( expression )
    static_cast < type-id > ( expression )
    reinterpret_cast < type-id > ( expression )
    const_cast < type-id > ( expression )
    typeid ( expression )
    typeid ( type-id )

expression-list:
    initializer-list
"""

import glrp
from ....parser import cxx98, cxx11, cxx98_merge
from .....ast.expressions import SimpleCastExpression, TypeIdExpression, TypeIdExpressionType, ExpressionList, PostfixExpression, CxxCastExpression, CallExpression, SubscriptExpression, MemberAccessExpression, MemberAccessPtrExpression, AmbiguousExpression
from motor_typing import TYPE_CHECKING


@glrp.rule('postfix-expression : [no-merge-warning] primary-expression')
@cxx98
def postfix_expression_stop(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('postfix-expression : [no-merge-warning] postfix-expression "[" expr-or-braced-init-list "]"')
@cxx98
def postfix_expression_subscript(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SubscriptExpression(p[0], p[1])


@glrp.rule('postfix-expression : [no-merge-warning] postfix-expression "(" expression-list? ")"')
@cxx98
def postfix_expression_call(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return CallExpression(p[0], p[2])


@glrp.rule('postfix-expression : simple-type-specifier-cast "(" expression-list? ")"')
@cxx98
def postfix_expression_simple_cast(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SimpleCastExpression(p[2], p[0])


@glrp.rule('postfix-expression : typename-specifier "(" expression-list? ")"')
@cxx98
def postfix_expression_typename_cast(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SimpleCastExpression(p[2], p[0])


@glrp.rule('postfix-expression : [no-merge-warning] postfix-expression "." template? id-expression')
@cxx98
def postfix_expression_member_access(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return MemberAccessExpression(p[0], p[3], p[2])


@glrp.rule('postfix-expression : [no-merge-warning] postfix-expression "->" template? id-expression')
@cxx98
def postfix_expression_member_access_ptr(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return MemberAccessPtrExpression(p[0], p[3], p[2])


@glrp.rule('postfix-expression : [no-merge-warning] postfix-expression "++"')
@glrp.rule('postfix-expression : [no-merge-warning] postfix-expression "--"')
@cxx98
def postfix_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return PostfixExpression(p[0], p[1].text())


@glrp.rule('postfix-expression : "dynamic_cast" "<" type-id ">" "(" expression ")"')
@glrp.rule('postfix-expression : "static_cast" "<" type-id ">" "(" expression ")"')
@glrp.rule('postfix-expression : "reinterpret_cast" "<" type-id ">" "(" expression ")"')
@glrp.rule('postfix-expression : "const_cast" "<" type-id ">" "(" expression ")"')
@cxx98
def postfix_expression_cast(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return CxxCastExpression(p[5], p[1], p[0].text())


@glrp.rule('postfix-expression : typeid-expression')
@cxx98
def postfix_expression_typeid(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('postfix-expression : [no-merge-warning]simple-type-specifier-cast braced-init-list')
@cxx11
def postfix_expression_simple_cast_braced_init_list_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SimpleCastExpression(p[1], p[0])


@glrp.rule('postfix-expression : typename-specifier braced-init-list')
@cxx11
def postfix_expression_typename_cast_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return SimpleCastExpression(p[1], p[0])


@glrp.rule('typeid-expression : typeid "(" begin-expression expression ")"')
@cxx98
def typeid_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeIdExpression(p[3])


@glrp.rule('typeid-expression : typeid "(" begin-type-id type-id ")"')
@cxx98
def typeid_expression_type(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeIdExpressionType(p[3])


@glrp.rule('expression-list? : initializer-list')
@glrp.rule('expression-list : initializer-list')
@cxx98
def expression_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ExpressionList(p[0])


@glrp.rule('expression-list? :')
@cxx98
def expression_list_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ExpressionList(None)


@glrp.rule('begin-type-id : [split:type_id]')
@glrp.rule('begin-expression : [split:expression]')
@cxx98
def begin_type_or_expression(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    pass


@glrp.merge('typeid-expression')
@cxx98_merge
def ambiguous_typeid_expression(self, type_id, expression):
    # type: (CxxParser, List[Any], List[Any]) -> Any
    return AmbiguousExpression(type_id + expression)


@glrp.merge('postfix-expression')
@cxx98_merge
def ambiguous_postfix_expression(
    self, simple_type_specifier_cast, ambiguous_template_id, id_template, id_nontemplate, ambiguous_postfix_expression
):
    # type: (CxxParser, List[Any], List[Any], List[Any], List[Any], List[Any]) -> Any
    expressions = simple_type_specifier_cast + ambiguous_template_id + id_template + id_nontemplate + ambiguous_postfix_expression
    return AmbiguousExpression(expressions)


if TYPE_CHECKING:
    from typing import Any, List
    from ....parser import CxxParser