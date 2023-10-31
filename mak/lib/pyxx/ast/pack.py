from .type import TypeId
from . import Visitor
from .base import Attribute, Expression
from .attributes import AttributeNamed


class PackExpandType(TypeId):

    def __init__(self, type_id: TypeId) -> None:
        self.type = type_id

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_pack_expand_type(self)

    def accept_type(self, visitor: Visitor) -> None:
        self.type.accept(visitor)


class PackExpandExpression(Expression):

    def __init__(self, expression: Expression) -> None:
        self.expression = expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_pack_expand_expression(self)

    def accept_expression(self, visitor: Visitor) -> None:
        self.expression.accept(visitor)


class PackExpandAttributeNamed(Attribute):

    def __init__(self, attribute: AttributeNamed) -> None:
        self.attribute = attribute

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_pack_expand_attribute_named(self)

    def accept_attribute(self, visitor: Visitor) -> None:
        self.attribute.accept(visitor)
