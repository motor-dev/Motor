from ..Configure import ConfigurationContext
from typing import Callable, Dict, List, Optional, Tuple

_MsvcVersion = Tuple[List[str], List[str], List[str]]


class target_compiler(object):

    def __init__(
            self,
            ctx: ConfigurationContext,
            compiler: str,
            cpu: str,
            version: str,
            bat_target: str,
            bat: str,
            callback: Optional[Callable[["target_compiler", _MsvcVersion], _MsvcVersion]] = ...) -> None:
        self.is_valid: bool = ...

    def evaluate(self) -> None:
        ...

    def __str__(self) -> str:
        ...

    def __repr__(self) -> str:
        ...


def gather_msvc_targets(
        conf: ConfigurationContext,
        versions: Dict[str, Dict[str, target_compiler]],
        version: str,
        vc_path: str,
        vc_kind: str = ...
) -> None:
    ...
