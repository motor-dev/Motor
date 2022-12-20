from motor_typing import TYPE_CHECKING
from .expressions import Expression


class Literal(Expression):
    pass


class BracedInitList(Literal):

    def __init__(self, initializer_list):
        # type: (List[List[Tuple[Expression, bool]]]) -> None
        self._initializer_list = initializer_list

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_braced_init_list(self)


class DesignatedBracedInitList(Literal):

    def __init__(self, initializer_list):
        # type: (List[DesignatedInitializer]) -> None
        self._initializer_list = initializer_list

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_designated_braced_init_list(self)


class DesignatedInitializer(object):

    def __init__(self, name, value):
        # type: (str, Expression) -> None
        self._name = name
        self._value = value

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_designated_initializer(self)


class BooleanLiteral(Literal):

    def __init__(self, boolean_value):
        # type: (bool) -> None
        self._boolean_value = boolean_value

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_boolean_literal(self)


class IntegerLiteral(Literal):

    def __init__(self, integer_value):
        # type: (str) -> None
        self._integer_value = integer_value

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_integer_literal(self)


class UserDefinedIntegerLiteral(IntegerLiteral):

    def __init__(self, integer_value, literal_type):
        # type: (str, str) -> None
        IntegerLiteral.__init__(self, integer_value)
        self._literal_type = literal_type

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_user_defined_integer_literal(self)


class CharacterLiteral(Literal):

    def __init__(self, character_value):
        # type: (str) -> None
        self._character_value = character_value

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_character_literal(self)


class UserDefinedCharacterLiteral(CharacterLiteral):

    def __init__(self, character_value, literal_type):
        # type: (str, str) -> None
        CharacterLiteral.__init__(self, character_value)
        self._literal_type = literal_type

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_user_defined_character_literal(self)


class StringLiteral(Literal):

    def __init__(self, string_value):
        # type: (str) -> None
        self._string_value = string_value

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_string_literal(self)


class StringLiteralMacro(StringLiteral):

    def __init__(self, macro_name, parameters):
        # type: (str, Optional[List[Token]]) -> None
        StringLiteral.__init__(self, macro_name)
        self._macro_parameters = parameters

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_string_literal_macro(self)


class UserDefinedStringLiteral(StringLiteral):

    def __init__(self, string_value, literal_type):
        # type: (str, str) -> None
        StringLiteral.__init__(self, string_value)
        self._literal_type = literal_type

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_user_defined_string_literal(self)


class StringList(Literal):

    def __init__(self, string_list):
        # type: (List[StringLiteral]) -> None
        self._string_list = string_list

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_string_list(self)


class FloatingLiteral(Literal):

    def __init__(self, floating_value):
        # type: (str) -> None
        self._floating_value = floating_value

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_floating_literal(self)


class UserDefinedFloatingLiteral(FloatingLiteral):

    def __init__(self, floating_value, literal_type):
        # type: (str, str) -> None
        FloatingLiteral.__init__(self, floating_value)
        self._literal_type = literal_type

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_user_defined_floating_literal(self)


if TYPE_CHECKING:
    from typing import List, Tuple, Optional
    from . import Visitor
    from glrp import Token
