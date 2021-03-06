from .ir_declaration import IrDeclaration
from motor_typing import TYPE_CHECKING


class IrAttribute:
    def __init__(self, attribute, parameters=[]):
        # type: (str, List[Union[IrExpression, IrType]]) -> None
        self._attribute = attribute
        self._parameters = parameters

    def resolve(self, module):
        # type: (IrModule) -> List[IrAttribute]
        return [self]

    def signature(self):
        # type: () -> str
        return str(self)

    def __str__(self):
        # type: () -> str
        return self._attribute + (
            ('(%s)' % ', '.join(str(value) for value in self._parameters)) if self._parameters else ''
        )


class IrAttributeGroup:
    def resolve(self, module):
        # type: (IrModule) -> IrAttributeGroupObject
        raise NotImplementedError

    def signature(self):
        # type: () -> str
        raise NotImplementedError


class IrAttributeGroupObject(IrAttributeGroup):
    def __init__(self, attribute_list):
        # type: (List[IrAttribute]) -> None
        self._attributes = attribute_list

    def resolve(self, module):
        # type: (IrModule) -> IrAttributeGroupObject
        self._attributes = [a for attribute in self._attributes for a in attribute.resolve(module)]
        return self

    def __str__(self):
        # type: () -> str
        return '; '.join(str(attr) for attr in self._attributes)

    def signature(self):
        # type: () -> str
        return '|'.join(attr.signature() for attr in self._attributes)


class IrAttributeGroupDeclaration(IrDeclaration):
    def __init__(self, attribute_group):
        # type: (IrAttributeGroupObject) -> None
        self._attribute_group = attribute_group

    def collect(self, ir_name):
        # type: (str) -> List[Tuple[str, IrDeclaration]]
        return []

    def signature(self):
        # type: () -> str
        return self._attribute_group.signature()

    def resolve(self, module):
        # type: (IrModule) -> None
        self._attribute_group = self._attribute_group.resolve(module)


class IrAttributeGroupLink(IrAttributeGroup):
    def __init__(self, reference):
        # type: (IrReference) -> None
        self._reference = reference

    def resolve(self, module):
        # type: (IrModule) -> IrAttributeGroupObject
        return module.get(self._reference, IrAttributeGroupDeclaration)._attribute_group


if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union
    from .ir_module import IrModule
    from .ir_reference import IrReference
    from .ir_expr import IrExpression
    from .ir_type import IrType