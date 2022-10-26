from .attributes import Attribute
from motor_typing import TYPE_CHECKING


class PackExpandType(object):

    def __init__(self, type):
        # type: (Any) -> None
        self._type = type


class PackExpandExpression:

    def __init__(self, expression):
        # type: (Any) -> None
        self._expression = expression


class PackExpandAttributeNamed(Attribute):

    def __init__(self, attribute):
        # type: (AttributeNamed) -> None
        self._attribute = attribute


if TYPE_CHECKING:
    from .attributes import AttributeNamed
    from typing import Any