from .type import TypeId
from . import Visitor
from .attributes import Attribute
from .expressions import Expression
from .attributes import AttributeNamed


class PackExpandType(TypeId):

    def __init__(self, type: TypeId) -> None:
        self._type = type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_pack_expand_type(self)

    def accept_type(self, visitor: Visitor) -> None:
        self._type.accept(visitor)


class PackExpandExpression(Expression):

    def __init__(self, expression: Expression) -> None:
        self._expression = expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_pack_expand_expression(self)

    def accept_expression(self, visitor: Visitor) -> None:
        self._expression.accept(visitor)


class PackExpandAttributeNamed(Attribute):

    def __init__(self, attribute: AttributeNamed) -> None:
        self._attribute = attribute

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_pack_expand_attribute_named(self)

    def accept_attribute(self, visitor: Visitor) -> None:
        self._attribute.accept(visitor)
