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
from typing import Any
from ....parse import CxxParser, cxx98, cxx11
from .....ast import (
    SimpleCastExpression,
    TypeIdExpression,
    TypeIdExpressionType,
    PostfixExpression,
    CxxCastExpression,
    CallExpression,
    SubscriptExpression,
    MemberAccessExpression,
    MemberAccessPtrExpression,
    ParenthesizedExpression,
    InitializerList,
    AmbiguousInitializerList,
    ErrorExpression,
)


@glrp.rule('postfix-expression : [no-merge-warning] primary-expression')
@cxx98
def postfix_expression_stop(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('postfix-expression : [no-merge-warning] postfix-expression "[" expr-or-braced-init-list "]"')
@cxx98
def postfix_expression_subscript(self: CxxParser, p: glrp.Production) -> Any:
    return SubscriptExpression(p[0], p[1])


@glrp.rule('postfix-expression : [no-merge-warning] postfix-expression "[" "#error" "]"')
@cxx98
def postfix_expression_subscript_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('postfix-expression : [no-merge-warning] postfix-expression "(" expression-list? ")"')
@cxx98
def postfix_expression_call(self: CxxParser, p: glrp.Production) -> Any:
    return CallExpression(p[0], ParenthesizedExpression(p[2]))


@glrp.rule('postfix-expression : [no-merge-warning] postfix-expression "(" "#error" ")"')
@cxx98
def postfix_expression_call_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('postfix-expression : simple-type-specifier-cast "(" expression-list? ")"')
@cxx98
def postfix_expression_simple_cast(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleCastExpression(ParenthesizedExpression(p[2]), p[0])


@glrp.rule('postfix-expression : simple-type-specifier-cast "(" "#error" ")"')
@cxx98
def postfix_expression_simple_cast_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('postfix-expression : typename-specifier "(" expression-list? ")"')
@cxx98
def postfix_expression_typename_cast(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleCastExpression(ParenthesizedExpression(p[2]), p[0])


@glrp.rule('postfix-expression : typename-specifier "(" "#error" ")"')
@cxx98
def postfix_expression_typename_cast_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('postfix-expression : [no-merge-warning] postfix-expression "." template? id-expression')
@cxx98
def postfix_expression_member_access(self: CxxParser, p: glrp.Production) -> Any:
    return MemberAccessExpression(p[0], p[3], p[2])


@glrp.rule('postfix-expression : [no-merge-warning] postfix-expression "->" template? id-expression')
@cxx98
def postfix_expression_member_access_ptr(self: CxxParser, p: glrp.Production) -> Any:
    return MemberAccessPtrExpression(p[0], p[3], p[2])


@glrp.rule('postfix-expression : [no-merge-warning] postfix-expression "++"')
@glrp.rule('postfix-expression : [no-merge-warning] postfix-expression "--"')
@cxx98
def postfix_expression(self: CxxParser, p: glrp.Production) -> Any:
    return PostfixExpression(p[0], p[1].text())


@glrp.rule('postfix-expression : "dynamic_cast" "<" type-id ">" "(" expression ")"')
@glrp.rule('postfix-expression : "static_cast" "<" type-id ">" "(" expression ")"')
@glrp.rule('postfix-expression : "reinterpret_cast" "<" type-id ">" "(" expression ")"')
@glrp.rule('postfix-expression : "const_cast" "<" type-id ">" "(" expression ")"')
@cxx98
def postfix_expression_cast(self: CxxParser, p: glrp.Production) -> Any:
    return CxxCastExpression(p[5], p[1], p[0].text())


@glrp.rule('postfix-expression : "dynamic_cast" "<" type-id ">" "(" "#error" ")"')
@glrp.rule('postfix-expression : "static_cast" "<" type-id ">" "(" "#error" ")"')
@glrp.rule('postfix-expression : "reinterpret_cast" "<" type-id ">" "(" "#error" ")"')
@glrp.rule('postfix-expression : "const_cast" "<" type-id ">" "(" "#error" ")"')
@glrp.rule('postfix-expression : "dynamic_cast" "<" "#error" ">" "(" expression ")"')
@glrp.rule('postfix-expression : "static_cast" "<" "#error" ">" "(" expression ")"')
@glrp.rule('postfix-expression : "reinterpret_cast" "<" "#error" ">" "(" expression ")"')
@glrp.rule('postfix-expression : "const_cast" "<" "#error" ">" "(" expression ")"')
@glrp.rule('postfix-expression : "dynamic_cast" "<" "#error" ">" "(" "#error" ")"')
@glrp.rule('postfix-expression : "static_cast" "<" "#error" ">" "(" "#error" ")"')
@glrp.rule('postfix-expression : "reinterpret_cast" "<" "#error" ">" "(" "#error" ")"')
@glrp.rule('postfix-expression : "const_cast" "<" "#error" ">" "(" "#error" ")"')
@cxx98
def postfix_expression_cast_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('postfix-expression : typeid-expression')
@cxx98
def postfix_expression_typeid(self: CxxParser, p: glrp.Production) -> Any:
    return p[0]


@glrp.rule('postfix-expression : [no-merge-warning]simple-type-specifier-cast braced-init-list')
@cxx11
def postfix_expression_simple_cast_braced_init_list_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleCastExpression(p[1], p[0])


@glrp.rule('postfix-expression : typename-specifier braced-init-list')
@cxx11
def postfix_expression_typename_cast_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleCastExpression(p[1], p[0])


@glrp.rule('typeid-expression : typeid "(" begin-expression expression ")"')
@cxx98
def typeid_expression(self: CxxParser, p: glrp.Production) -> Any:
    return TypeIdExpression(p[3])


@glrp.rule('typeid-expression : typeid "(" begin-type-id type-id ")"')
@cxx98
def typeid_expression_type(self: CxxParser, p: glrp.Production) -> Any:
    return TypeIdExpressionType(p[3])


@glrp.rule('typeid-expression : typeid "(" "#error" ")"')
@cxx98
def typeid_expression_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('expression-list? : initializer-list')
@glrp.rule('expression-list : initializer-list')
@cxx98
def expression_list(self: CxxParser, p: glrp.Production) -> Any:
    if len(p[0]) == 1:
        return InitializerList(p[0][0])
    else:
        return AmbiguousInitializerList([InitializerList(l) for l in sorted(p[0], key=lambda x: len(x))])


@glrp.rule('expression-list? :')
@cxx98
def expression_list_opt(self: CxxParser, p: glrp.Production) -> Any:
    return None


@glrp.rule('begin-type-id : [split:type_id]')
@glrp.rule('begin-expression : [split:expression]')
@cxx98
def begin_type_or_expression(self: CxxParser, p: glrp.Production) -> Any:
    pass
