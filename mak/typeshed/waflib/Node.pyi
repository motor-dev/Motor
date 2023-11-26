import threading
from typing import List, Optional, Tuple, Union, overload
from typing_extensions import Literal, TypeAlias

exclude_regs: str = ...
_OpenTextModeWriting: TypeAlias = Literal["w", "wt", "tw", "a", "at", "ta", "x", "xt", "tx"]
_OpenTextModeReading: TypeAlias = Literal["r", "rt", "tr", "U", "rU", "Ur", "rtU", "rUt", "Urt", "trU", "tUr", "Utr"]
_OpenBinaryModeWriting: TypeAlias = Literal["wb", "bw", "ab", "ba", "xb", "bx"]
_OpenBinaryModeReading: TypeAlias = Literal["rb", "br", "rbU", "rUb", "Urb", "brU", "bUr", "Ubr"]


class Node(object):
    __slots__: Tuple[str, ...] = ('name', 'parent', 'children', 'cache_abspath', 'cache_isdir')

    def __init__(self, name: str, parent: Optional["Node"]):
        self.name = name
        self.parent: "Node" = ...

    def __str__(self) -> str:
        ...

    def __repr__(self) -> str:
        ...

    @overload
    def read(self, flags: _OpenTextModeReading = 'r', encoding: Optional[str] = ...) -> str:
        ...

    @overload
    def read(self, flags: _OpenBinaryModeReading, encoding: None = ...) -> bytes:
        ...

    @overload
    def write(self, data: str, flags: _OpenTextModeWriting = 'w', encoding: Optional[str] = ...) -> None:
        ...

    @overload
    def write(self, data: bytes, flags: _OpenBinaryModeWriting, encoding: None = ...) -> None:
        ...

    def exists(self) -> bool:
        ...

    def isdir(self) -> bool:
        ...

    def chmod(self, val: int) -> None:
        ...

    def delete(self, evict: bool = ...) -> None:
        ...

    def evict(self) -> None:
        ...

    def suffix(self) -> str:
        ...

    def height(self) -> int:
        ...

    def listdir(self) -> List[str]:
        ...

    def mkdir(self) -> None:
        ...

    def find_node(self, lst: Union[str, List[str]]) -> Optional["Node"]:
        ...

    def make_node(self, lst: Union[str, List[str]]) -> "Node":
        ...

    def search_node(self, lst: Union[str, List[str]]) -> Optional["Node"]:
        ...

    def path_from(self, node: "Node") -> str:
        ...

    def abspath(self) -> str:
        ...

    def is_child_of(self, node: "Node") -> bool:
        ...

    def ant_glob(
            self,
            incl: Union[str, List[str]] = ...,
            excl: Union[str, List[str]] = ...,
            dir: bool = ...,
            src: bool = ...,
            maxdepth: int = ...,
            ignorecase: bool = ...,
            generator: bool = ...,
            remove: bool = ...,
            quiet: bool = ...
    ) -> List["Node"]:
        ...

    def is_src(self) -> bool:
        ...

    def is_bld(self) -> bool:
        ...

    def get_src(self) -> "Node":
        ...

    def get_bld(self) -> "Node":
        ...

    def find_resource(self, lst: Union[str, List[str]]) -> Optional["Node"]:
        ...

    def find_or_declare(self, lst: Union[str, List[str]]) -> "Node":
        ...

    def find_dir(self, lst: Union[str, List[str]]) -> Optional["Node"]:
        ...

    # helpers for building things
    def change_ext(self, ext: str, ext_in: Optional[str] = ...) -> "Node":
        ...

    def bldpath(self) -> str:
        ...

    def srcpath(self) -> str:
        ...

    def relpath(self) -> str:
        ...

    def bld_dir(self) -> str:
        ...

    def h_file(self) -> bytes:
        ...

    def get_bld_sig(self) -> bytes:
        ...


Nod3 = Node
pickle_lock: threading.Lock
