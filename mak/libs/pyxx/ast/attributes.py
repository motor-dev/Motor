from motor_typing import TYPE_CHECKING


class Attribute(object):
    pass


class AttributeNamedList(Attribute):

    def __init__(self, using_namespace, attributes):
        # type: (Optional[str], List[AttributeNamed]) -> None
        self._using_namespace = using_namespace
        self._attributes = attributes

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_attribute_named_list(self)


class AttributeNamed(object):

    def __init__(self, namespace, attribute, value):
        # type: (Optional[str], str, Optional[List[Token]]) -> None
        self._namespace = namespace
        self._attribute = attribute
        self._value = value

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_attribute_named(self)


class AttributeAlignAsType(Attribute):

    def __init__(self, type):
        # type: (TypeId) -> None
        self._type = type

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_attribute_align_as_type(self)


class AttributeAlignAsExpression(Attribute):

    def __init__(self, expression):
        # type: (Expression) -> None
        self._expression = expression

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_attribute_align_as_expression(self)


class AttributeAlignAsAmbiguous(Attribute):

    def __init__(self, align_as_type, align_as_expression):
        # type: (AttributeAlignAsType, AttributeAlignAsExpression) -> None
        self._align_as_type = align_as_type
        self._align_as_expression = align_as_expression

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_attribute_align_as_ambiguous(self)


class AttributeAlignAsAmbiguousPack(Attribute):

    def __init__(self, align_as_pack, align_as_decl):
        # type: (AttributeAlignAsType, AttributeAlignAsType) -> None
        self._align_as_type = align_as_pack
        self._align_as_decl = align_as_decl

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_attribute_align_as_ambiguous_pack(self)


class AttributeDocumentation(Attribute):

    def __init__(self, documentation):
        # type: (Documentation) -> None
        self._documentation = documentation

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_attribute_documentation(self)


class AttributeMacro(Attribute):

    def __init__(self, attribute, values):
        # type: (str, Optional[List[Token]]) -> None
        self._attribute = attribute
        self._values = values

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_attribute_macro(self)


class Documentation(object):
    pass


if TYPE_CHECKING:
    from typing import List, Optional
    from . import Visitor
    from .expressions import Expression
    from .type import TypeId
    from glrp import Token