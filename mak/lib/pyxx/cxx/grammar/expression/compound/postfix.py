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


@glrp.rule('constant-expression[prec:left,16] : constant-expression [prec:left,16]"[" expr-or-braced-init-list "]"')
@glrp.rule('constant-expression#[prec:left,16] : constant-expression# [prec:left,16]"[" expr-or-braced-init-list "]"')
@cxx98
def postfix_expression_subscript(self: CxxParser, p: glrp.Production) -> Any:
    return SubscriptExpression(p[0], p[1])


@glrp.rule('constant-expression[prec:left,16] : constant-expression [prec:left,16]"[" "#error" "]"')
@glrp.rule('constant-expression#[prec:left,16] : constant-expression# [prec:left,16]"[" "#error" "]"')
@cxx98
def postfix_expression_subscript_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('constant-expression[prec:left,16] : constant-expression [prec:left,16]"(" expression-list? ")"')
@glrp.rule('constant-expression#[prec:left,16] : constant-expression# [prec:left,16]"(" expression-list? ")"')
@cxx98
def postfix_expression_call(self: CxxParser, p: glrp.Production) -> Any:
    return CallExpression(p[0], ParenthesizedExpression(p[2]))


@glrp.rule('constant-expression[prec:left,16] : constant-expression [prec:left,16]"(" "#error" ")"')
@glrp.rule('constant-expression#[prec:left,16] : constant-expression# [prec:left,16]"(" "#error" ")"')
@cxx98
def postfix_expression_call_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('constant-expression[prec:left,16] : simple-type-specifier-cast [prec:left,16]"(" expression-list? ")"')
@glrp.rule('constant-expression#[prec:left,16] : simple-type-specifier-cast [prec:left,16]"(" expression-list? ")"')
@cxx98
def postfix_expression_simple_cast(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleCastExpression(ParenthesizedExpression(p[2]), p[0])


@glrp.rule('constant-expression[prec:left,16] : simple-type-specifier-cast [prec:left,16]"(" "#error" ")"')
@glrp.rule('constant-expression#[prec:left,16] : simple-type-specifier-cast [prec:left,16]"(" "#error" ")"')
@cxx98
def postfix_expression_simple_cast_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('constant-expression[prec:left,16] : typename-specifier [prec:left,16]"(" expression-list? ")"')
@glrp.rule('constant-expression#[prec:left,16] : typename-specifier [prec:left,16]"(" expression-list? ")"')
@cxx98
def postfix_expression_typename_cast(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleCastExpression(ParenthesizedExpression(p[2]), p[0])


@glrp.rule('constant-expression[prec:left,16] : typename-specifier [prec:left,16]"(" "#error" ")"')
@glrp.rule('constant-expression#[prec:left,16] : typename-specifier [prec:left,16]"(" "#error" ")"')
@cxx98
def postfix_expression_typename_cast_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('constant-expression[prec:left,16] : constant-expression [prec:left,16]"." template? id-expression')
@glrp.rule('constant-expression#[prec:left,16] : constant-expression# [prec:left,16]"." template? id-expression')
@cxx98
def postfix_expression_member_access(self: CxxParser, p: glrp.Production) -> Any:
    return MemberAccessExpression(p[0], p[3], p[2])


@glrp.rule('constant-expression[prec:left,16] : constant-expression [prec:left,16]"->" template? id-expression')
@glrp.rule('constant-expression#[prec:left,16] : constant-expression# [prec:left,16]"->" template? id-expression')
@cxx98
def postfix_expression_member_access_ptr(self: CxxParser, p: glrp.Production) -> Any:
    return MemberAccessPtrExpression(p[0], p[3], p[2])


@glrp.rule('constant-expression[prec:left,16] : constant-expression [prec:left,16]"++"')
@glrp.rule('constant-expression[prec:left,16] : constant-expression [prec:left,16]"--"')
@glrp.rule('constant-expression#[prec:left,16] : constant-expression# [prec:left,16]"++"')
@glrp.rule('constant-expression#[prec:left,16] : constant-expression# [prec:left,16]"--"')
@cxx98
def postfix_expression(self: CxxParser, p: glrp.Production) -> Any:
    return PostfixExpression(p[0], p[1].text())


@glrp.rule('constant-expression : "dynamic_cast" "<" type-id ">" "(" expression ")"')
@glrp.rule('constant-expression : "static_cast" "<" type-id ">" "(" expression ")"')
@glrp.rule('constant-expression : "reinterpret_cast" "<" type-id ">" "(" expression ")"')
@glrp.rule('constant-expression : "const_cast" "<" type-id ">" "(" expression ")"')
@glrp.rule('constant-expression# : "dynamic_cast" "<" type-id ">" "(" expression ")"')
@glrp.rule('constant-expression# : "static_cast" "<" type-id ">" "(" expression ")"')
@glrp.rule('constant-expression# : "reinterpret_cast" "<" type-id ">" "(" expression ")"')
@glrp.rule('constant-expression# : "const_cast" "<" type-id ">" "(" expression ")"')
@cxx98
def postfix_expression_cast(self: CxxParser, p: glrp.Production) -> Any:
    return CxxCastExpression(p[5], p[1], p[0].text())


@glrp.rule('constant-expression : "dynamic_cast" "<" type-id ">" "(" "#error" ")"')
@glrp.rule('constant-expression : "static_cast" "<" type-id ">" "(" "#error" ")"')
@glrp.rule('constant-expression : "reinterpret_cast" "<" type-id ">" "(" "#error" ")"')
@glrp.rule('constant-expression : "const_cast" "<" type-id ">" "(" "#error" ")"')
@glrp.rule('constant-expression : "dynamic_cast" "<" "#error" ">" "(" expression ")"')
@glrp.rule('constant-expression : "static_cast" "<" "#error" ">" "(" expression ")"')
@glrp.rule('constant-expression : "reinterpret_cast" "<" "#error" ">" "(" expression ")"')
@glrp.rule('constant-expression : "const_cast" "<" "#error" ">" "(" expression ")"')
@glrp.rule('constant-expression : "dynamic_cast" "<" "#error" ">" "(" "#error" ")"')
@glrp.rule('constant-expression : "static_cast" "<" "#error" ">" "(" "#error" ")"')
@glrp.rule('constant-expression : "reinterpret_cast" "<" "#error" ">" "(" "#error" ")"')
@glrp.rule('constant-expression : "const_cast" "<" "#error" ">" "(" "#error" ")"')
@glrp.rule('constant-expression# : "dynamic_cast" "<" type-id ">" "(" "#error" ")"')
@glrp.rule('constant-expression# : "static_cast" "<" type-id ">" "(" "#error" ")"')
@glrp.rule('constant-expression# : "reinterpret_cast" "<" type-id ">" "(" "#error" ")"')
@glrp.rule('constant-expression# : "const_cast" "<" type-id ">" "(" "#error" ")"')
@glrp.rule('constant-expression# : "dynamic_cast" "<" "#error" ">" "(" expression ")"')
@glrp.rule('constant-expression# : "static_cast" "<" "#error" ">" "(" expression ")"')
@glrp.rule('constant-expression# : "reinterpret_cast" "<" "#error" ">" "(" expression ")"')
@glrp.rule('constant-expression# : "const_cast" "<" "#error" ">" "(" expression ")"')
@glrp.rule('constant-expression# : "dynamic_cast" "<" "#error" ">" "(" "#error" ")"')
@glrp.rule('constant-expression# : "static_cast" "<" "#error" ">" "(" "#error" ")"')
@glrp.rule('constant-expression# : "reinterpret_cast" "<" "#error" ">" "(" "#error" ")"')
@glrp.rule('constant-expression# : "const_cast" "<" "#error" ">" "(" "#error" ")"')
@cxx98
def postfix_expression_cast_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('constant-expression : simple-type-specifier-cast braced-init-list')
@glrp.rule('constant-expression# : simple-type-specifier-cast braced-init-list')
@cxx11
def postfix_expression_simple_cast_braced_init_list_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleCastExpression(p[1], p[0])


@glrp.rule('constant-expression : typename-specifier braced-init-list')
@glrp.rule('constant-expression# : typename-specifier braced-init-list')
@cxx11
def postfix_expression_typename_cast_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return SimpleCastExpression(p[1], p[0])


@glrp.rule('constant-expression : typeid "(" begin-expression expression ")"')
@glrp.rule('constant-expression# : typeid "(" begin-expression expression ")"')
@cxx98
def typeid_expression(self: CxxParser, p: glrp.Production) -> Any:
    return TypeIdExpression(p[3])


@glrp.rule('constant-expression : typeid "(" begin-type-id type-id ")"')
@glrp.rule('constant-expression# : typeid "(" begin-type-id type-id ")"')
@cxx98
def typeid_expression_type(self: CxxParser, p: glrp.Production) -> Any:
    return TypeIdExpressionType(p[3])


@glrp.rule('constant-expression : typeid "(" "#error" ")"')
@glrp.rule('constant-expression# : typeid "(" "#error" ")"')
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
