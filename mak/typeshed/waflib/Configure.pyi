import waflib.Context
from .Context import Context
from .ConfigSet import ConfigSet
from .Node import Node
from typing import Any, Callable, Dict, List, Optional, Union
from typing_extensions import Concatenate, ParamSpec

WAF_CONFIG_LOG: str = ...
autoconfig: bool = ...
conf_template: str = ...


class ConfigurationContext(Context):
    variant: str = ...

    def __init__(self, **kw: Any) -> None:
        Context.__init__(self, **kw)
        self.environ: Dict[str, str] = ...
        self.all_envs: Dict[str, ConfigSet] = ...

        self.top_dir: str = ...
        self.out_dir: str = ...

        self.hash: bytes = ...
        self.files: List[str] = ...

        self.srcnode: Node = ...
        self.bldnode: Node = ...
        self.cachedir: Node = ...

    def setenv(self, name: str, env: Optional[ConfigSet] = ...) -> None:
        ...

    def get_env(self) -> ConfigSet:
        ...

    def set_env(self, val: ConfigSet) -> None:
        ...

    def init_dirs(self) -> None:
        ...

    def execute(self) -> Optional[str]:
        ...

    def prepare_env(self, env: ConfigSet) -> None:
        ...

    def store(self) -> None:
        ...

    def load(
            self,
            tool_list: Union[str, List[str]],
            tooldir: Union[str, List[str], None] = ...,
            with_sys_path: bool = ...,
            cache: bool = ...
    ) -> None:
        ...

    def post_recurse(self, node: Node) -> None:
        ...

    def eval_rules(self, rules: List[str]) -> None:
        ...

    def cmd_to_list(self, cmd: Union[str, List[str]]) -> List[str]:
        ...

    def check_waf_version(self, mini: str = ..., maxi: str = ..., **kw: Any) -> None:
        ...

    def find_file(self, filename: str, path_list: List[str] = ...) -> None:
        ...

    def find_program(
            self,
            filename: str,
            mandatory: bool = ...,
            path_list: Optional[List[str]] = ...,
            var: Optional[str] = ...,
            value: Optional[List[str]] = ...,
            ext: Optional[List[str]] = ...,
            msg: Optional[str] = ...,
            interpreter: Optional[str] = ...,
            quiet: bool = ...
    ) -> Optional[List[str]]:
        ...

    def find_binary(self, filenames: List[str], exts: List[str], paths: List[str]) -> Optional[str]:
        ...

    env = property(ConfigurationContext.get_env, ConfigurationContext.set_env)


P = ParamSpec('P')


def conf(f: Callable[Concatenate[Context, P], Any]) -> Callable[Concatenate[Context, P], Any]:
    ...


def find_program(
        self: Context,
        filename: str,
        mandatory: bool = ...,
        path_list: Optional[List[str]] = ...,
        var: Optional[str] = ...,
        value: Optional[List[str]] = ...,
        ext: Optional[List[str]] = ...,
        msg: Optional[str] = ...,
        interpreter: Optional[str] = ...,
        quiet: bool = ...
) -> Optional[List[str]]:
    ...


def find_binary(self: Context, filenames: List[str], exts: List[str], paths: List[str]) -> Optional[str]:
    ...
