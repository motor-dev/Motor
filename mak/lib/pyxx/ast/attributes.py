from typing import List, Optional, Tuple
from glrp import Token
from . import Visitor
from .base import Attribute, TypeId, Expression


class InvalidAttribute(object):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_invalid_attribute(self)


class AttributeNamed(object):

    def __init__(self, namespace: Optional[str], attribute: str, value: Optional[List[Token]],
                 position: Tuple[int, int]):
        self.position = position
        self.namespace = namespace
        self.attribute = attribute
        self.value = value

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_attribute_named(self.namespace, self)


class AttributeNamedList(Attribute):

    def __init__(self, using_namespace: Optional[str], attributes: List[AttributeNamed]) -> None:
        self.using_namespace = using_namespace
        self.attributes = attributes

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_attribute_named_list(self)

    def accept_attributes(self, visitor: Visitor) -> None:
        for attribute in self.attributes:
            visitor.visit_attribute_named(self.using_namespace, attribute)


class AttributeAlignAsType(Attribute):

    def __init__(self, typeid: TypeId) -> None:
        self.typeid = typeid

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_attribute_align_as_type(self)

    def accept_type(self, visitor: Visitor) -> None:
        self.typeid.accept(visitor)


class AttributeAlignAsExpression(Attribute):

    def __init__(self, expression: Expression) -> None:
        self.expression = expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_attribute_align_as_expression(self)

    def accept_expression(self, visitor: Visitor) -> None:
        self.expression.accept(visitor)


class AttributeAlignAsAmbiguous(Attribute):

    def __init__(self, align_as_type: AttributeAlignAsType, align_as_expression: AttributeAlignAsExpression) -> None:
        self.align_as_type = align_as_type
        self.align_as_expression = align_as_expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_attribute_align_as_ambiguous(self)

    def accept_alignas_type(self, visitor: Visitor) -> None:
        self.align_as_type.accept(visitor)

    def accept_alignas_expression(self, visitor: Visitor) -> None:
        self.align_as_expression.accept(visitor)


class Documentation(object):
    pass


class AttributeDocumentation(Attribute):

    def __init__(self, documentation: Documentation) -> None:
        self.documentation = documentation

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_attribute_documentation(self)


class AttributeMacro(Attribute):

    def __init__(self, position: Tuple[int, int], attribute: str, values: Optional[List[Token]]) -> None:
        self.position = position
        self.attribute = attribute
        self.values = values

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_attribute_macro(self)
