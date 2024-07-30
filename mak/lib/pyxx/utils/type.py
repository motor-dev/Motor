from .stringref import StringRef
from .. import ast


class TypeExtractor(StringRef):
    def __init__(self) -> None:
        super().__init__()
        self._position = (-1, -1)
        self._nested = 0

    def visit_decl_specifier_seq(self, decl_specifier_seq: ast.DeclSpecifierSeq) -> None:
        decl_specifier_seq.accept_type_specifier_seq(self)

    def visit_declarator_element_method(self, declarator_element_method: ast.DeclaratorElementMethod) -> None:
        self._nested += 1
        super().visit_declarator_element_method(declarator_element_method)
        self._nested -= 1

    def visit_declarator_element_id(self, declarator_element_id: ast.DeclaratorElementId) -> None:
        if self._nested == 0:
            p1 = len(self.result)
            declarator_element_id.accept_name(self)
            p2 = len(self.result)
            self._position = (p1, p2)
        else:
            print('caca')
            declarator_element_id.accept_name(self)

    def visit_declarator_element_pack_id(self, declarator_element_pack_id: ast.DeclaratorElementPackId) -> None:
        if self._nested == 0:
            self.result += '...'
            p1 = len(self.result)
            declarator_element_pack_id.accept_name(self)
            p2 = len(self.result)
            self._position = (p1, p2)
        else:
            self.result += '...'
            declarator_element_pack_id.accept_name(self)

    def visit_declarator_element_abstract(self, declarator_element_abstract: ast.DeclaratorElementAbstract) -> None:
        if self._nested == 0:
            self._position = (len(self.result), len(self.result))

    def visit_declarator_element_abstract_pack(
            self, declarator_element_abstract_pack: ast.DeclaratorElementAbstractPack
    ) -> None:
        self.result += '...'
        if self._nested == 0:
            self._position = (len(self.result), len(self.result))

    def visit_parameter_declaration(self, parameter_declaration: ast.ParameterDeclaration) -> None:
        if parameter_declaration.this_specifier:
            self.result += 'this '
        parameter_declaration.accept_decl_specifier_seq(self)
        parameter_declaration.accept_declarator(self)


class ReturnTypeExtractor(TypeExtractor):
    def __init__(self) -> None:
        super().__init__()

    def visit_declarator_element_method(self, declarator_element_method: ast.DeclaratorElementMethod) -> None:
        if self._nested > 0:
            self._nested += 1
            super().visit_declarator_element_method(declarator_element_method)
            self._nested -= 1
        else:
            declarator_element_method.accept_next(self)
