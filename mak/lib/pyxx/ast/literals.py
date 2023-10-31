from typing import List, Optional
from glrp import Token
from . import Visitor
from .base import Expression


class Literal(Expression):
    pass


class AbstractBracedInitList(Literal):
    pass


class BracedInitList(AbstractBracedInitList):

    def __init__(self, initializer_list: List[Expression]) -> None:
        self.initializer_list = initializer_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_braced_init_list(self)

    def accept_initializers(self, visitor: Visitor) -> None:
        for initializer in self.initializer_list:
            initializer.accept(visitor)


class AmbiguousBracedInitList(AbstractBracedInitList):

    def __init__(self, braced_init_lists: List[BracedInitList]) -> None:
        self.braced_init_lists = braced_init_lists

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ambiguous_braced_init_list(self)

    def accept_first(self, visitor: Visitor) -> None:
        self.braced_init_lists[0].accept(visitor)

    def accept_all(self, visitor: Visitor) -> None:
        for init_list in self.braced_init_lists:
            init_list.accept(visitor)


class DesignatedInitializer(object):

    def __init__(self, name: str, value: Expression) -> None:
        self.name = name
        self.value = value

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_designated_initializer(self)

    def accept_value(self, visitor: Visitor) -> None:
        self.value.accept(visitor)


class DesignatedBracedInitList(AbstractBracedInitList):

    def __init__(self, initializer_list: List[DesignatedInitializer]):
        self.initializer_list = initializer_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_designated_braced_init_list(self)

    def accept_initializers(self, visitor: Visitor) -> None:
        for initializer in self.initializer_list:
            initializer.accept(visitor)


class BooleanLiteral(Literal):

    def __init__(self, boolean_value: bool) -> None:
        self.boolean_value = boolean_value

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_boolean_literal(self)


class IntegerLiteral(Literal):

    def __init__(self, integer_value: str) -> None:
        self.integer_value = integer_value

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_integer_literal(self)


class UserDefinedIntegerLiteral(IntegerLiteral):

    def __init__(self, integer_value: str, literal_type: str):
        IntegerLiteral.__init__(self, integer_value)
        self.literal_type = literal_type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_user_defined_integer_literal(self)


class CharacterLiteral(Literal):

    def __init__(self, character_value: str) -> None:
        self.character_value = character_value

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_character_literal(self)


class UserDefinedCharacterLiteral(CharacterLiteral):

    def __init__(self, character_value: str, literal_type: str) -> None:
        CharacterLiteral.__init__(self, character_value)
        self.literal_type = literal_type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_user_defined_character_literal(self)


class StringLiteral(Literal):

    def __init__(self, string_value: str) -> None:
        self.string_value = string_value

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_string_literal(self)


class StringLiteralMacro(StringLiteral):

    def __init__(self, macro_name: str, parameters: Optional[List[Token]]) -> None:
        StringLiteral.__init__(self, macro_name)
        self.macro_parameters = parameters

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_string_literal_macro(self)


class UserDefinedStringLiteral(StringLiteral):

    def __init__(self, string_value: str, literal_type: str) -> None:
        StringLiteral.__init__(self, string_value)
        self.literal_type = literal_type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_user_defined_string_literal(self)


class StringList(Literal):

    def __init__(self, string_list: List[StringLiteral]) -> None:
        self.string_list = string_list

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_string_list(self)

    def accept_strings(self, visitor: Visitor) -> None:
        for string in self.string_list:
            string.accept(visitor)


class FloatingLiteral(Literal):

    def __init__(self, floating_value: str) -> None:
        self.floating_value = floating_value

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_floating_literal(self)


class UserDefinedFloatingLiteral(FloatingLiteral):

    def __init__(self, floating_value: str, literal_type: str):
        FloatingLiteral.__init__(self, floating_value)
        self.literal_type = literal_type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_user_defined_floating_literal(self)
