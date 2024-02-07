"""
primary-expression:
    literal
    this
    ( expression )
    id-expression
    lambda-expression
    fold-expression
    requires-expression
"""

import glrp
from typing import Any
from ....parse import CxxParser, cxx98, cxx11, cxx17, cxx20
from .....ast.expressions import (
    ThisExpression,
    IdExpression,
    ParenthesizedExpression,
    NullPtrExpression,
    TypeTraitExpression,
    ErrorExpression,
)
from .....ast.literals import (
    IntegerLiteral,
    UserDefinedIntegerLiteral,
    CharacterLiteral,
    UserDefinedCharacterLiteral,
    FloatingLiteral,
    UserDefinedFloatingLiteral,
    BooleanLiteral,
    StringLiteral,
    StringLiteralMacro,
    UserDefinedStringLiteral,
    StringList,
)
from . import id
from . import lambda_expr
from . import fold
from . import requires


@glrp.rule('constant-expression : "integer-literal"')
@glrp.rule('constant-expression# : "integer-literal"')
@cxx98
def primary_expression_integer_literal(self: CxxParser, p: glrp.Production) -> Any:
    return IntegerLiteral(p[0].text())


@glrp.rule('constraint-logical-expression : "integer-literal"')
@cxx20
def primary_expression_integer_literal_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return IntegerLiteral(p[0].text())


@glrp.rule('constant-expression : "character-literal"')
@glrp.rule('constant-expression# : "character-literal"')
@cxx98
def primary_expression_character_literal(self: CxxParser, p: glrp.Production) -> Any:
    return CharacterLiteral(p[0].value)


@glrp.rule('constraint-logical-expression : "character-literal"')
@cxx20
def primary_expression_character_literal_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return CharacterLiteral(p[0].value)


@glrp.rule('constant-expression : "floating-literal"')
@glrp.rule('constant-expression# : "floating-literal"')
@cxx98
def primary_expression_floating_literal(self: CxxParser, p: glrp.Production) -> Any:
    return FloatingLiteral(p[0].text())


@glrp.rule('constraint-logical-expression : "floating-literal"')
@cxx20
def primary_expression_floating_literal_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return FloatingLiteral(p[0].text())


@glrp.rule('constant-expression : string-literal-list')
@glrp.rule('constant-expression# : string-literal-list')
@cxx98
def primary_expression_string_literal_list(self: CxxParser, p: glrp.Production) -> Any:
    return StringList(p[0])


@glrp.rule('constraint-logical-expression : string-literal-list')
@cxx20
def primary_expression_string_literal_list_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return StringList(p[0])


@glrp.rule('constant-expression : "this"')
@glrp.rule('constant-expression# : "this"')
@cxx98
def primary_expression_this(self: CxxParser, p: glrp.Production) -> Any:
    return ThisExpression()


@glrp.rule('constraint-logical-expression : "this"')
@cxx20
def primary_expression_this_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ThisExpression()


@glrp.rule('constant-expression : "true"')
@glrp.rule('constant-expression# : "true"')
@cxx98
def primary_expression_true(self: CxxParser, p: glrp.Production) -> Any:
    return BooleanLiteral(True)


@glrp.rule('constraint-logical-expression : "true"')
@cxx20
def primary_expression_true_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return BooleanLiteral(True)


@glrp.rule('constant-expression : "false"')
@glrp.rule('constant-expression# : "false"')
@cxx98
def primary_expression_false(self: CxxParser, p: glrp.Production) -> Any:
    return BooleanLiteral(False)


@glrp.rule('constraint-logical-expression : "false"')
@cxx20
def primary_expression_false_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return BooleanLiteral(False)


@glrp.rule('constant-expression : "type-trait-macro"')
@glrp.rule('constant-expression# : "type-trait-macro"')
@cxx98
def primary_expression_type_trait(self: CxxParser, p: glrp.Production) -> Any:
    return TypeTraitExpression(p[0].text(), None)


@glrp.rule('constraint-logical-expression : "type-trait-macro"')
@cxx20
def primary_expression_type_trait_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return TypeTraitExpression(p[0].text(), None)


@glrp.rule('constant-expression : "type-trait-macro-function" "(" balanced-token-seq? ")"')
@glrp.rule('constant-expression# : "type-trait-macro-function" "(" balanced-token-seq? ")"')
@cxx98
def primary_expression_type_trait_function_cxx(self: CxxParser, p: glrp.Production) -> Any:
    return TypeTraitExpression(p[0].text(), p[2])


@glrp.rule('constraint-logical-expression : "type-trait-macro-function" "(" balanced-token-seq? ")"')
@cxx20
def primary_expression_type_trait_function_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return TypeTraitExpression(p[0].text(), p[2])


@glrp.rule('constant-expression : [prec:right,15]"(" begin-expression expression ")"')
@glrp.rule('constant-expression# : [prec:right,15]"(" begin-expression expression ")"')
@cxx98
def primary_expression_proxy(self: CxxParser, p: glrp.Production) -> Any:
    return ParenthesizedExpression(p[2])


@glrp.rule('constraint-logical-expression : [prec:right,15]"(" begin-expression expression ")"')
@cxx20
def primary_expression_proxy_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ParenthesizedExpression(p[2])


@glrp.rule('constant-expression : [prec:right,15]"(" begin-expression "#error" ")"')
@glrp.rule('constant-expression# : [prec:right,15]"(" begin-expression "#error" ")"')
@cxx98
def primary_expression_proxy_error(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('constraint-logical-expression : [prec:right,15]"(" begin-expression "#error" ")"')
@cxx20
def primary_expression_proxy_error_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return ErrorExpression()


@glrp.rule('constant-expression : "user-defined-integer-literal"')
@glrp.rule('constant-expression# : "user-defined-integer-literal"')
@cxx11
def primary_expression_user_defined_integer_literal_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return UserDefinedIntegerLiteral(p[0].value[0], p[0].value[1])


@glrp.rule('constraint-logical-expression : "user-defined-integer-literal"')
@cxx20
def primary_expression_user_defined_integer_literal_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return UserDefinedIntegerLiteral(p[0].value[0], p[0].value[1])


@glrp.rule('constant-expression : "user-defined-character-literal"')
@glrp.rule('constant-expression# : "user-defined-character-literal"')
@cxx11
def primary_expression_user_defined_character_literal_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return UserDefinedCharacterLiteral(p[0].value[0], p[0].value[1])


@glrp.rule('constraint-logical-expression : "user-defined-character-literal"')
@cxx20
def primary_expression_user_defined_character_literal_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return UserDefinedCharacterLiteral(p[0].value[0], p[0].value[1])


@glrp.rule('constant-expression : "user-defined-floating-literal"')
@glrp.rule('constant-expression# : "user-defined-floating-literal"')
@cxx11
def primary_expression_user_defined_floating_literal_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return UserDefinedFloatingLiteral(p[0].value[0], p[0].value[1])


@glrp.rule('constraint-logical-expression : "user-defined-floating-literal"')
@cxx20
def primary_expression_user_defined_floating_literal_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return UserDefinedFloatingLiteral(p[0].value[0], p[0].value[1])


@glrp.rule('constant-expression : "nullptr"')
@glrp.rule('constant-expression# : "nullptr"')
@cxx11
def primary_expression_nullptr_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    return NullPtrExpression()


@glrp.rule('constraint-logical-expression : "nullptr"')
@cxx20
def primary_expression_nullptr_cxx20(self: CxxParser, p: glrp.Production) -> Any:
    return NullPtrExpression()


@glrp.rule('string-literal-list : "string-literal" string-literal-list?')
@glrp.rule('string-literal-list? : "string-literal" string-literal-list?')
@cxx11
def string_literal_list_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    result = p[1]
    result.insert(0, StringLiteral(p[0].value))
    return result


@glrp.rule('string-literal-list : "string-literal-macro" string-literal-list?')
@glrp.rule('string-literal-list? : "string-literal-macro" string-literal-list?')
@cxx98
def string_literal_list_macro(self: CxxParser, p: glrp.Production) -> Any:
    result = p[1]
    result.insert(0, StringLiteralMacro(p[0].text(), None))
    return result


@glrp.rule('string-literal-list : "string-literal-macro-function" "(" balanced-token-seq? ")" string-literal-list?')
@glrp.rule('string-literal-list? : "string-literal-macro-function" "(" balanced-token-seq? ")" string-literal-list?')
@cxx98
def string_literal_list_macro_parameters(self: CxxParser, p: glrp.Production) -> Any:
    result = p[4]
    result.insert(0, StringLiteralMacro(p[0].text(), p[2]))
    return result


@glrp.rule('string-literal-list : "user-defined-string-literal" string-literal-list?')
@glrp.rule('string-literal-list? : "user-defined-string-literal" string-literal-list?')
@cxx11
def string_literal_list_user_defined_cxx11(self: CxxParser, p: glrp.Production) -> Any:
    result = p[1]
    result.insert(0, UserDefinedStringLiteral(p[0].value[0], p[0].value[1]))
    return result


@glrp.rule('string-literal-list? : ')
@cxx98
def string_literal_list_opt(self: CxxParser, p: glrp.Production) -> Any:
    return []
