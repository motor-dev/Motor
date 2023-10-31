from typing import Any
from ..Configure import ConfigurationContext


def check(self: ConfigurationContext, *k: Any, **kw: Any) -> bool:
    ...
