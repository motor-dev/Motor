from motor_typing import TYPE_CHECKING


class TranslationUnit(object):

    def __init__(self, global_module_fragment, module_declaration, declarations, private_module_fragment):
        # type: (None, None, List[Declaration], List[Declaration]) -> None
        self._declarations = declarations
        self._private_module_frgment = private_module_fragment


if TYPE_CHECKING:
    from typing import List
    from .declarations import Declaration