import queue
from .Context import Context
from .ConfigSet import ConfigSet
from .Node import Node
from .Task import Task
from .TaskGen import task_gen
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

CACHE_DIR: str = ...
CACHE_SUFFIX: str = ...
INSTALL: int = ...
UNINSTALL: int = ...
SAVED_ATTRS: str = ...
CFG_FILES: str = ...
POST_AT_ONCE: int = ...
POST_LAZY: int = ...
PROTOCOL: int = ...


class _Producer(object):
    def __init__(self) -> None:
        self.processed: int = ...
        self.total: int = ...
        self.ready: queue.Queue[Any] = ...


class BuildContext(Context):
    cmd: str = ...
    variant: str = ...

    def __init__(self, **kw: Any) -> None:
        Context.__init__(self, **kw)
        self.is_install: int = ...
        self.top_dir: str = ...
        self.out_dir: str = ...
        self.run_dir: str = ...
        self.launch_dir: str = ...
        self.post_mode: int = ...
        self.cache_dir: str = ...
        self.all_envs: Dict[str, ConfigSet] = ...

        self.node_sigs: Dict[Node, bytes] = ...
        self.task_sigs: Dict[bytes, bytes] = ...
        self.imp_sigs: Dict[bytes, bytes] = ...
        self.node_deps: Dict[bytes, List[Node]] = ...
        self.raw_deps: Dict[bytes, List[str]] = ...
        self.task_gen_cache_names: Dict[str, task_gen] = ...
        self.jobs: int = ...
        self.targets: str = ...
        self.keep: bool = ...
        self.progress_bar: int = ...
        self.deps_man: Dict[Node, Any] = ...
        self.current_group = 0
        self.groups: List[List[task_gen]] = ...
        self.group_names: Dict[str, List[task_gen]] = ...

        self.root: Node = ...
        self.srcnode: Node = ...
        self.bldnode: Node = ...
        self.path: Node = ...
        self.producer: _Producer = ...

    def get_variant_dir(self) -> str:
        return self.path.name

    def __call__(self, *k: Any, **kw: Any) -> task_gen:
        ...

    def load_envs(self) -> None:
        ...

    def init_dirs(self) -> None:
        ...

    def execute(self) -> Optional[str]:
        ...

    def execute_build(self) -> None:
        ...

    def restore(self) -> None:
        ...

    def store(self) -> None:
        ...

    def compile(self) -> None:
        ...

    def is_dirty(self) -> bool:
        ...

    def setup(self, tool: Union[str, List[str]], tooldir: Optional[str] = None, funs: Optional[str] = None) -> None:
        ...

    def get_env(self) -> ConfigSet:
        ...

    def set_env(self, val: ConfigSet) -> None:
        ...

    def add_manual_dependency(self, path: str, value: Any) -> None:
        ...

    def launch_node(self) -> Node:
        ...

    def hash_env_vars(self, env: ConfigSet, vars_lst: List[str]) -> bytes:
        ...

    def get_tgen_by_name(self, name: str) -> task_gen:
        ...

    def progress_line(self, idx: int, total: int, col1: str, col2: str) -> str:
        ...

    def pre_build(self) -> None:
        ...

    def post_build(self) -> None:
        ...

    def add_pre_fun(self, meth: Callable[["BuildContext"], None]) -> None:
        ...

    def add_post_fun(self, meth: Callable[["BuildContext"], None]) -> None:
        ...

    def get_group(self, x: Union[str, int, None]) -> task_gen:
        ...

    def add_to_group(self, tgen: task_gen, group: Union[str, int, None] = None) -> None:
        ...

    def get_group_name(self, g: Union[int, List[task_gen]]) -> str:
        ...

    def get_group_idx(self, tg: task_gen) -> Optional[int]:
        ...

    def add_group(self, name: Optional[str] = None, move: bool = True) -> None:
        ...

    def set_group(self, idx: int) -> None:
        ...

    def total(self) -> int:
        ...

    def get_targets(self) -> Tuple[int, List[task_gen]]:
        ...

    def post_group(self) -> None:
        ...

    def get_tasks_group(self, idx: int) -> List[Task]:
        ...

    def get_build_iterator(self) -> List[Task]:
        ...

    def install_files(self, dest: Union[str, Node], files: List[Union[str, Node]], **kw: Any) -> task_gen:
        ...

    def install_as(self, dest: Union[str, Node], srcfile: Union[str, Node], **kw: Any) -> task_gen:
        ...

    def symlink_as(self, dest: Union[str, Node], src: str, **kw: Any) -> task_gen:
        ...

    env = property(BuildContext.get_env, BuildContext.set_env)


def process_install_task(self: task_gen) -> None:
    ...


def add_install_task(self: task_gen, **kw: Any) -> Task:
    ...


def add_install_files(self: task_gen, **kw: Any) -> Task:
    ...


def add_install_as(self: task_gen, **kw: Any) -> Task:
    ...


def add_symlink_as(self: task_gen, **kw: Any) -> Task:
    ...


class InstallContext(BuildContext):
    ...


class UninstallContext(InstallContext):
    ...


class CleanContext(BuildContext):

    def clean(self) -> None:
        ...


class ListContext(BuildContext):
    ...


class StepContext(BuildContext):

    def __init__(self, **kw: Any):
        BuildContext.__init__(self, **kw)
        self.files: str = ...

    def compile(self) -> None:
        ...

    def get_matcher(self, pat: str) -> Callable[[Node], bool]:
        ...


class EnvContext(BuildContext):
    ...
