import optparse
from typing import Any, Callable, Dict, List, Optional
from typing_extensions import Literal
from .Context import Context
from .Node import Node


class _Values(object):
    def __init__(self) -> None:
        self.environ: Dict[str, str] = ...

    def __getattr__(self, name: str) -> Any:
        ...


options: _Values = ...
commands: List[str] = ...
lockfile: str = ...


class OptionsContext(Context):

    def __init__(self, **kw: Any) -> None:
        Context.__init__(self, **kw)

        self.hash: bytes = ...
        self.files: List[str] = ...

    def jobs(self) -> int:
        ...

    def add_option(
            self,
            short: str,
            long: str = ...,
            action: Literal[
                'store',
                'store_const',
                'store_true',
                'store_false',
                'append',
                'append_const',
                'count',
                'callback',
                'help',
                'version',
            ] = ...,
            const: Any = ...,
            type: str = ...,
            dest: str = ...,
            nargs: int = ...,
            metavar: str = '',
            default: Any = ...,
            help: str = '',
            callback: Callable[..., Any] = ...,
            callback_args: List[Any] = ...,
            callback_kwargs: Dict[str, Any] = ...
    ) -> optparse.Option:
        ...

    def add_option_group(self, title: str, description: str = ...) -> optparse.OptionGroup:
        ...

    def get_option_group(self, opt_str: str) -> Optional[optparse.OptionGroup]:
        ...

    def sanitize_path(self, path: str, cwd: Optional[str] = ...) -> str:
        ...

    def parse_cmd_args(self, _args: Optional[List[str]] = ..., cwd: Optional[str] = ...,
                       allow_unknown: bool = ...) -> None:
        ...

    def parse_args(self, _args: Optional[List[str]] = ...) -> None:
        ...

    def execute(self) -> None:
        ...

    def post_recurse(self, node: Node) -> None:
        ...
