from typing import Any, Callable, Dict, List, Optional, Union
from typing_extensions import ParamSpec, Concatenate
from .Build import BuildContext
from .ConfigSet import ConfigSet
from .Node import Node
from .Task import Task

HEADER_EXTS: List[str] = ...


class task_gen(object):
    mappings: Dict[str, Callable[[task_gen, Node], None]]

    def __init__(self, bld: BuildContext, target: str, *k: Any, **kw: Any) -> None:
        self.source: List[Node] = ...
        self.target: str = ...
        self.features: List[str] = ...
        self.tasks: List[Task] = ...
        self.env: ConfigSet = ...
        self.bld: BuildContext = ...
        self.path: Node = ...

    def __str__(self) -> str:
        ...

    def __repr__(self) -> str:
        ...

    def get_cwd(self) -> Node:
        ...

    def get_name(self) -> str:
        ...

    def set_name(self, name: str) -> None:
        ...

    name = property(get_name, set_name)

    def to_list(self, val: Any) -> Any:
        ...

    def post(self) -> bool:
        ...

    def get_hook(self, node: Node) -> Callable[["task_gen", Node], None]:
        ...

    def create_task(self, name: str, src: Union[Node, List[Node], None] = ..., tgt: Union[Node, List[Node], None] = ...,
                    **kw: Any) -> Task:
        ...

    def clone(self, env: ConfigSet) -> "task_gen":
        ...


def declare_chain(
        name: str = ...,
        rule: Any = ...,
        reentrant: int = ...,
        color: str = ...,
        ext_in: List[str] = ...,
        ext_out: List[str] = ...,
        before: List[str] = ...,
        after: List[str] = ...,
        decider: Any = ...,
        scan: Any = ...,
        install_path: str = ...,
        shell: bool = ...
) -> Callable[[task_gen, Node], Task]:
    ...


P = ParamSpec("P")


def taskgen_method(func: Callable[Concatenate[task_gen, P], Any]) -> Callable[Concatenate[task_gen, P], Any]:
    ...


def feature(*k: str) -> Callable[[Callable[[task_gen], None]], Callable[[task_gen], None]]:
    ...


def before(*k: str) -> Callable[[Callable[[task_gen], None]], Callable[[task_gen], None]]:
    ...


def before_method(*k: str) -> Callable[[Callable[[task_gen], None]], Callable[[task_gen], None]]:
    ...


def after(*k: str) -> Callable[[Callable[[task_gen], None]], Callable[[task_gen], None]]:
    ...


def after_method(*k: str) -> Callable[[Callable[[task_gen], None]], Callable[[task_gen], None]]:
    ...


def extension(*k: str) -> Callable[[Callable[[task_gen, Node], None]], Callable[[task_gen, Node], None]]:
    ...


def to_nodes(self: task_gen, lst: Union[str, List[Union[str, Node]]], path: Optional[Node] = ...) -> List[Node]:
    ...
