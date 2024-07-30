from .. import ast
from .stringref import StringRef


class NameExtractor(ast.Visitor):
    """Extracts the name of an init_declarator in result"""

    def __init__(self) -> None:
        super().__init__()
        self.result = ''

    def visit_init_declarator(self, init_declarator: ast.InitDeclarator) -> None:
        init_declarator.accept_declarator(self)

    def visit_declarator_list(self, declarator_list: ast.DeclaratorList) -> None:
        declarator_list.accept_element(self)

    def visit_abstract_declarator_list(self, abstract_declarator_list: ast.AbstractDeclaratorList) -> None:
        sr = StrignRef()
        abstract_declarator_list.accept_element(sr)
        self.result = sr.result

    def visit_declarator_element_id(self, declarator_element_id: ast.DeclaratorElementId) -> None:
        declarator_element_id.accept_name(self)

    def visit_declarator_element_pack_id(self, declarator_element_pack_id: ast.DeclaratorElementPackId) -> None:
        declarator_element_pack_id.accept_name(self)

    def visit_declarator_element_group(self, declarator_element_group: ast.DeclaratorElementGroup) -> None:
        declarator_element_group.accept_next(self)

    def visit_declarator_element_pointer(self, declarator_element_pointer: ast.DeclaratorElementPointer) -> None:
        declarator_element_pointer.accept_next(self)

    def visit_declarator_element_reference(self, declarator_element_reference: ast.DeclaratorElementReference) -> None:
        declarator_element_reference.accept_next(self)

    def visit_declarator_element_rvalue_reference(
            self, declarator_element_rvalue_reference: ast.DeclaratorElementRValueReference
    ) -> None:
        declarator_element_rvalue_reference.accept_next(self)

    def visit_declarator_element_array(self, declarator_element_array: ast.DeclaratorElementArray) -> None:
        declarator_element_array.accept_next(self)

    def visit_declarator_element_method(self, declarator_element_method: ast.DeclaratorElementMethod) -> None:
        declarator_element_method.accept_next(self)
