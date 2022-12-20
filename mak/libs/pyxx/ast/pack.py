from motor_typing import TYPE_CHECKING
from .attributes import Attribute
from .type import TypeId
from .expressions import Expression


class PackExpandType(TypeId):

    def __init__(self, type):
        # type: (TypeId) -> None
        self._type = type

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_pack_expand_type(self)


class PackExpandExpression(Expression):

    def __init__(self, expression):
        # type: (Expression) -> None
        self._expression = expression

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_pack_expand_expression(self)


class PackExpandAttributeNamed(Attribute):

    def __init__(self, attribute):
        # type: (AttributeNamed) -> None
        self._attribute = attribute

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_pack_expand_attribute_named(self)


if TYPE_CHECKING:
    from . import Visitor
    from .attributes import AttributeNamed
