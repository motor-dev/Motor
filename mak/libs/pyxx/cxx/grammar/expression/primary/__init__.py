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
from ....parse import cxx98, cxx11, cxx17, cxx20
from .....ast.expressions import ThisExpression, IdExpression, ParenthesizedExpression, NullPtrExpression, TypeTraitExpression
from .....ast.literals import IntegerLiteral, UserDefinedIntegerLiteral, CharacterLiteral, UserDefinedCharacterLiteral, FloatingLiteral, UserDefinedFloatingLiteral, BooleanLiteral, StringLiteral, StringLiteralMacro, UserDefinedStringLiteral, StringList
from motor_typing import TYPE_CHECKING
from . import id
from . import lambda_expr
from . import fold
from . import requires


@glrp.rule('primary-expression : "integer-literal"')
@cxx98
def primary_expression_integer_literal(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return IntegerLiteral(p[0].text())


@glrp.rule('primary-expression : "character-literal"')
@cxx98
def primary_expression_character_literal(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return CharacterLiteral(p[0].text())


@glrp.rule('primary-expression : "floating-literal"')
@cxx98
def primary_expression_floating_literal(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return FloatingLiteral(p[0].text())


@glrp.rule('primary-expression : string-literal-list')
@cxx98
def primary_expression_string_literal_list(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return StringList(p[0])


@glrp.rule('primary-expression : "this"')
@cxx98
def primary_expression_this(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ThisExpression()


@glrp.rule('primary-expression : "true"')
@cxx98
def primary_expression_true(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BooleanLiteral(True)


@glrp.rule('primary-expression : "false"')
@cxx98
def primary_expression_false(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return BooleanLiteral(False)


@glrp.rule('primary-expression : primary-expression-proxy')
@cxx98
def primary_expression_primary_expression_proxy(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('primary-expression : id-expression')
@cxx98
def primary_expression_id(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return IdExpression(p[0])


# Primary expression that can be use in a constraint
@glrp.rule('primary-expression : "type-trait-macro"')
@cxx98
def primary_expression_type_trait(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeTraitExpression(p[0].text(), None)


@glrp.rule('primary-expression : "type-trait-macro-function" "(" balanced-token-seq? ")"')
@cxx98
def primary_expression_type_trait_function(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return TypeTraitExpression(p[0].text(), p[2])


@glrp.rule('primary-expression-proxy : "(" begin-expression expression ")"')
@cxx98
def primary_expression_proxy(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return ParenthesizedExpression(p[2])


@glrp.rule('primary-expression : "user-defined-integer-literal"')
@cxx11
def primary_expression_user_defined_integer_literal_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return UserDefinedIntegerLiteral(p[0].value[0], p[0].value[1])


@glrp.rule('primary-expression : "user-defined-character-literal"')
@cxx11
def primary_expression_user_defined_character_literal_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return UserDefinedCharacterLiteral(p[0].value[0], p[0].value[1])


@glrp.rule('primary-expression : "user-defined-floating-literal"')
@cxx11
def primary_expression_user_defined_floating_literal_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return UserDefinedFloatingLiteral(p[0].value[0], p[0].value[1])


@glrp.rule('primary-expression : lambda-expression')
@cxx11
def primary_expression_lambda_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('primary-expression : "nullptr"')
@cxx11
def primary_expression_nullptr_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return NullPtrExpression()


@glrp.rule('string-literal-list : "string-literal" string-literal-list?')
@glrp.rule('string-literal-list? : "string-literal" string-literal-list?')
@cxx11
def string_literal_list_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[1]
    result.append(StringLiteral(p[0].value))
    return result


@glrp.rule('string-literal-list : "string-literal-macro" string-literal-list?')
@glrp.rule('string-literal-list? : "string-literal-macro" string-literal-list?')
@cxx98
def string_literal_list_macro(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[1]
    result.append(StringLiteralMacro(p[0].text(), None))
    return result


@glrp.rule('string-literal-list : "string-literal-macro-function" "(" balanced-token-seq? ")" string-literal-list?')
@glrp.rule('string-literal-list? : "string-literal-macro-function" "(" balanced-token-seq? ")" string-literal-list?')
@cxx98
def string_literal_list_macro_parameters(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[4]
    result.append(StringLiteralMacro(p[0].text(), p[2]))
    return result


@glrp.rule('string-literal-list : "user-defined-string-literal" string-literal-list?')
@glrp.rule('string-literal-list? : "user-defined-string-literal" string-literal-list?')
@cxx11
def string_literal_list_user_defined_cxx11(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    result = p[1]
    result.append(UserDefinedStringLiteral(p[0]._value[0], p[0]._value[1]))
    return result


@glrp.rule('string-literal-list? : ')
@cxx98
def string_literal_list_opt(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return []


@glrp.rule('primary-expression-proxy : fold-expression')
@cxx17
def primary_expression_proxy_cxx17(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


@glrp.rule('primary-expression : requires-expression')
@cxx20
def primary_expression_cxx20(self, p):
    # type: (CxxParser, glrp.Production) -> Any
    return p[0]


if TYPE_CHECKING:
    from typing import Any
    from ....parse import CxxParser