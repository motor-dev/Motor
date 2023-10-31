from ..Node import Node
from ..Task import Task
from ..TaskGen import task_gen
from typing import Dict, List, Set, Union

USELIB_VARS: Dict[str, Set[str]] = ...


def get_uselib_vars(self: task_gen) -> List[str]:
    ...


def to_incnodes(self: task_gen, inlst: Union[str, List[Union[str, Node]]]) -> List[Node]:
    ...


class link_task(Task):
    ...
