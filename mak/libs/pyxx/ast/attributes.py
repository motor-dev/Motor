from typing import List, Optional
from glrp import Token
from . import Visitor


class Attribute(object):

    def accept(self, visitor: Visitor) -> None:
        raise NotImplementedError


class AttributeError(object):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_attribute_error(self)


class AttributeNamed(object):

    def __init__(self, namespace: Optional[str], attribute: str, value: Optional[List[Token]]):
        self._namespace = namespace
        self._attribute = attribute
        self._value = value

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_attribute_named(self)


class AttributeNamedList(Attribute):

    def __init__(self, using_namespace: Optional[str], attributes: List[AttributeNamed]) -> None:
        self._using_namespace = using_namespace
        self._attributes = attributes

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_attribute_named_list(self)


class AttributeAlignAsType(Attribute):

    def __init__(self, type: "TypeId") -> None:
        self._type = type

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_attribute_align_as_type(self)

    def accept_type(self, visitor: Visitor) -> None:
        self._type.accept(visitor)


class AttributeAlignAsExpression(Attribute):

    def __init__(self, expression: "Expression") -> None:
        self._expression = expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_attribute_align_as_expression(self)

    def accept_expression(self, visitor: Visitor) -> None:
        self._expression.accept(visitor)


class AttributeAlignAsAmbiguous(Attribute):

    def __init__(self, align_as_type: AttributeAlignAsType, align_as_expression: AttributeAlignAsExpression) -> None:
        self._align_as_type = align_as_type
        self._align_as_expression = align_as_expression

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_attribute_align_as_ambiguous(self)

    def accept_alignas_type(self, visitor: Visitor) -> None:
        self._align_as_type.accept(visitor)

    def accept_alignas_expression(self, visitor: Visitor) -> None:
        self._align_as_expression.accept(visitor)


class Documentation(object):
    pass


class AttributeDocumentation(Attribute):

    def __init__(self, documentation: Documentation) -> None:
        self._documentation = documentation

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_attribute_documentation(self)


class AttributeMacro(Attribute):

    def __init__(self, attribute: str, values: Optional[List[Token]]) -> None:
        self._attribute = attribute
        self._values = values

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_attribute_macro(self)


from .type import TypeId
from .expressions import Expression