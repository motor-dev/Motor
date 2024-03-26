from typing import List, Optional
from . import Visitor
from .base import Attribute, Declaration


class ModuleDeclaration(Declaration):

    def __init__(self, name: List[str], partition: Optional[List[str]], attributes: List[Attribute], export: bool):
        Declaration.__init__(self, attributes)
        self.name = name
        self.partition = partition
        self.export = export

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_module_declaration(self)


class ModuleImportDeclaration(Declaration):

    def __init__(self, name: List[str], attributes: List[Attribute]) -> None:
        Declaration.__init__(self, attributes)
        self.name = name

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_module_import_declaration(self)


class PrivateModuleFragment(Declaration):

    def __init__(self, declaration_seq: List[Declaration]) -> None:
        Declaration.__init__(self, [])
        self.declaration_seq = declaration_seq

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_private_module_fragment(self)

    def accept_declarations(self, visitor: Visitor) -> None:
        for decl in self.declaration_seq:
            decl.accept(visitor)


class ExportDeclaration(Declaration):

    def __init__(self, declaration_seq: List[Declaration]) -> None:
        Declaration.__init__(self, [])
        self.declaration_seq = declaration_seq

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_export_declaration(self)

    def accept_declarations(self, visitor: Visitor) -> None:
        for decl in self.declaration_seq:
            decl.accept(visitor)


class GlobalModuleFragment(object):

    def __init__(self, declaration_seq: List[Declaration]) -> None:
        self.declaration_seq = declaration_seq

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_global_module_fragment(self)

    def accept_declarations(self, visitor: Visitor) -> None:
        for decl in self.declaration_seq:
            decl.accept(visitor)
