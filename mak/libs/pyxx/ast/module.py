from .declarations import Declaration
from motor_typing import TYPE_CHECKING


class ModuleDeclaration(Declaration):

    def __init__(self, name, partition, attributes, export):
        # type: (List[str], Optional[List[str]], List[Attribute], bool) -> None
        self._name = name
        self._partition = partition
        self._attributes = attributes
        self._export = export

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_module_declaration(self)


class ModuleImportDeclaration(Declaration):

    def __init__(self, name, attributes):
        # type: (List[str], List[Attribute]) -> None
        self._name = name
        self._attributes = attributes

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_module_import_declaration(self)


class PrivateModuleFragment(Declaration):

    def __init__(self, declaration_seq):
        # type: (List[Declaration]) -> None
        self._declaration_seq = declaration_seq

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_private_module_fragment(self)


class ExportDeclaration(Declaration):

    def __init__(self, declaration_seq):
        # type: (List[Declaration]) -> None
        self._declaration_seq = declaration_seq

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_export_declaration(self)


class GlobalModuleFragment(object):

    def __init__(self, declaration_seq):
        # type: (List[Declaration]) -> None
        self._declaration_seq = declaration_seq

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_global_module_fragment(self)


if TYPE_CHECKING:
    from typing import List, Optional
    from . import Visitor
    from .attributes import Attribute