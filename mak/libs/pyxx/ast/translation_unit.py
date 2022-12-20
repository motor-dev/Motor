from motor_typing import TYPE_CHECKING


class TranslationUnit(object):

    def __init__(self, global_module_fragment, module_declaration, declarations, private_module_fragment):
        # type: (None, None, List[Declaration], List[Declaration]) -> None
        self._declarations = declarations
        self._private_module_frgment = private_module_fragment

    def accept(self, visitor):
        # type: (Visitor) -> None
        visitor.visit_translation_unit(self)


if TYPE_CHECKING:
    from typing import List
    from . import Visitor
    from .declarations import Declaration