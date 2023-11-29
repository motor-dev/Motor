import hashlib
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union
from .Build import BuildContext
from .ConfigSet import ConfigSet
from .TaskGen import task_gen
from .Node import Node

NOT_RUN: int = ...
MISSING: int = ...
CRASHED: int = ...
EXCEPTION: int = ...
CANCELED: int = ...
SKIPPED: int = ...
SUCCESS: int = ...

ASK_LATER: int = ...
SKIP_ME: int = ...
RUN_ME: int = ...
CANCEL_ME: int = ...

COMPILE_TEMPLATE_SHELL: str = ...
COMPILE_TEMPLATE_NOSHELL: str = ...

classes: Dict[str, Type[Task]] = ...


class Task(object):
    vars: List[str] = ...
    always_run: bool = ...
    shell: bool = ...
    color: str = ...
    ext_in: Union[str, List[str]] = ...
    ext_out: Union[str, List[str]] = ...
    before: Union[str, List[str]] = ...
    after: Union[str, List[str]] = ...
    hcode: bytes = ...
    keep_last_cmd: bool = ...
    weight: int = ...
    tree_weight: int = ...
    prio_order: int = ...
    run_str: str = ...
    orig_run_str: str = ...

    def __init__(self, env: ConfigSet, **kw: Any) -> None:
        self.generator: task_gen = ...
        self.env: ConfigSet = ...
        self.inputs: List[Node] = ...
        self.outputs: List[Node] = ...
        self.dep_nodes: List[Node] = ...
        self.run_after: Set["Task"] = ...
        self.cache_sig: bytes = ...
        self.m: hashlib._Hash = ...
        self.cwd: str = ...
        self.hasrun: int

    def __lt__(self, other: Task) -> bool:
        ...

    def __le__(self, other: Task) -> bool:
        ...

    def __gt__(self, other: Task) -> bool:
        ...

    def __ge__(self, other: Task) -> bool:
        ...

    def get_cwd(self) -> Node:
        ...

    def quote_flag(self, x: str) -> str:
        ...

    def priority(self) -> Tuple[int, int]:
        ...

    def split_argfile(self, cmd: List[str]) -> Tuple[List[str], List[str]]:
        ...

    def exec_command(self, cmd: Union[str, List[str]], **kw: Any) -> int:
        ...

    def process(self) -> int:
        ...

    def log_display(self, bld: BuildContext) -> None:
        ...

    def display(self) -> str:
        ...

    def keyword(self) -> str:
        ...

    def uid(self) -> bytes:
        ...

    def set_inputs(self, inp: Union[Node, List[Node]]) -> None:
        ...

    def set_outputs(self, out: Union[Node, List[Node]]) -> None:
        ...

    def set_run_after(self, task: "Task") -> None:
        ...

    def signature(self) -> bytes:
        ...

    def runnable_status(self) -> int:
        ...

    def post_run(self) -> None:
        ...

    def sig_explicit_deps(self) -> None:
        ...

    def sig_deep_inputs(self) -> None:
        ...

    def sig_vars(self) -> None:
        ...

    def sig_implicit_deps(self) -> bytes:
        ...

    def compute_sig_implicit_deps(self) -> bytes:
        ...

    def are_implicit_nodes_ready(self) -> None:
        ...

    def scan(self) -> Tuple[List[Node], List[str]]:
        ...


def task_factory(
        name: str,
        func: Union[str, Callable[[Task], Optional[int]], None] = ...,
        vars: List[str] = ...,
        color: str = ...,
        ext_in: List[str] = ...,
        ext_out: List[str] = ...,
        before: List[str] = ...,
        after: List[str] = ...,
        shell: bool = ...,
        scan: Optional[Callable[[], Tuple[List[Node], List[str]]]] = ...
) -> type:
    ...


def set_file_constraints(tasks: List[Task]) -> None:
    ...


def set_precedence_constraints(tasks: List[Task]) -> None:
    ...
