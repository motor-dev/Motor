import pyxx.ast
from typing import Dict, List, Tuple


class Kernel(object):
    def __init__(self, parameters: List[Tuple[str, Tuple[int, int]]]) -> None:
        self.parameters = parameters


class KernelNamespace(object):
    def __init__(self) -> None:
        self.using_directives: List[pyxx.ast.UsingDirective] = []
        self.using_declarations: List[pyxx.ast.UsingDeclaration] = []
        self.children: Dict[str, "KernelNamespace"] = {}
        self.kernels: Dict[str, Kernel] = {}
