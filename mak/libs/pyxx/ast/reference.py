from motor_typing import TYPE_CHECKING


class _Id(object):
    pass


class RootId(_Id):
    pass


class Id(_Id):

    def __init__(self, name):
        # type: (str) -> None
        self._name = name


class TemplateId(_Id):

    def __init__(self, id, template_arguments):
        # type: (_Id, List[TemplateArgument]) -> None
        self._id = id
        self._template_arguments = template_arguments


class DestructorId(_Id):

    def __init__(self, id):
        # type: (_Id) -> None
        self._id = id


class OperatorId(_Id):

    def __init__(self, operator):
        # type: (str) -> None
        self._operator = operator


class ConversionOperatorId(_Id):

    def __init__(self, conversion_type):
        # type: (TypeId) -> None
        self._conversion_type = conversion_type


class LiteralOperatorId(_Id):

    def __init__(self, literal_operator):
        # type: (str) -> None
        self._literal_operator = literal_operator


class Reference(object):

    def __init__(self, name_list):
        # type: (List[Tuple[bool, _Id]]) -> None
        self._name_list = name_list


if TYPE_CHECKING:
    from typing import Any, List, Tuple
    from .type import TypeId
    from .template import TemplateArgument
