from ..Task import Task
from ..Node import Node
from ..ConfigSet import ConfigSet
from typing import Dict, List, Optional, Tuple


def scan(task: Task) -> Tuple[List[Node], List[str]]:
    ...


class c_parser(object):

    def __init__(self, nodepaths: Optional[List[Node]] = ..., defines: Optional[Dict[str, str]] = ...):
        self.nodes: List[Node] = ...
        self.names: List[str] = ...

    def start(self, node: Node, env: ConfigSet) -> None:
        ...
