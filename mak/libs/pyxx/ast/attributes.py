from motor_typing import TYPE_CHECKING


class Attribute(object):
    pass


class AttributeNamedList(Attribute):

    def __init__(self, using_namespace, attributes):
        # type: (Optional[str], List[AttributeNamed]) -> None
        self._using_namespace = using_namespace
        self._attributes = attributes


class AttributeNamed(object):

    def __init__(self, namespace, attribute, value):
        # type: (Optional[str], str, Optional[List[Any]]) -> None
        self._namespace = namespace
        self._attribute = attribute
        self._value = value


class AttributeAlignAsType(Attribute):

    def __init__(self, type):
        # type: (Any) -> None
        self._type = type


class AttributeAlignAsExpression(Attribute):

    def __init__(self, expression):
        # type: (Any) -> None
        self._expression = expression


class AttributeAlignAsAmbiguous(Attribute):

    def __init__(self, align_as_type, align_as_expression):
        # type: (AttributeAlignAsType, AttributeAlignAsExpression) -> None
        self._align_as_type = align_as_type
        self._align_as_expression = align_as_expression


class AttributeAlignAsAmbiguousPack(Attribute):

    def __init__(self, align_as_pack, align_as_decl):
        # type: (AttributeAlignAsType, AttributeAlignAsType) -> None
        self._align_as_type = align_as_pack
        self._align_as_decl = align_as_decl


class AttributeDocumentation(Attribute):

    def __init__(self, documentation):
        # type: (Any) -> None
        self._documentation = documentation


class AttributeMacro(Attribute):

    def __init__(self, attribute, values):
        # type: (str, Optional[List[Any]]) -> None
        self._attribute = attribute
        self._values = values


if TYPE_CHECKING:
    from typing import Any, List, Optional