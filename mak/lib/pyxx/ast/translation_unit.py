from typing import List
from . import Visitor
from .declarations import Declaration


class TranslationUnit(object):

    def __init__(
            self, global_module_fragment: None, module_declaration: None, declarations: List[Declaration],
            private_module_fragment: List[Declaration], included_files: List[str]
    ) -> None:
        self.global_module_fragment = global_module_fragment
        self.module_declaration = module_declaration
        self.declarations = declarations
        self.private_module_fragment = private_module_fragment
        self.included_files = included_files

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_translation_unit(self)

    def accept_children(self, visitor: Visitor) -> None:
        for declaration in self.declarations:
            declaration.accept(visitor)
