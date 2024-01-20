import sys
import build_framework
import waflib.Node
import waflib.Task
from typing import List, Tuple


class ircc(waflib.Task.Task):
    color = 'CYAN'
    ircc_dep_nodes = []  # type: List[waflib.Node.Node]

    def run(self) -> int:
        return self.exec_command(
            [
                sys.executable, self.generator.bld.env.KERNEL_CLT, '--tmp',
                self.generator.bld.bldnode.abspath(), self.inputs[0].abspath(), self.outputs[0].abspath(),
                'none'
            ]
        )

    def scan(self) -> Tuple[List[waflib.Node.Node], List[str]]:  # type: ignore
        return self.ircc_dep_nodes, []


def build(build_context: build_framework.BuildContext) -> None:
    ircc.ircc_dep_nodes = []
    mak_node = build_context.motornode.make_node('mak')
    ircc.ircc_dep_nodes = [mak_node.make_node('bin/ir_compile.py')]
    if not build_context.env.PROJECTS:
        build_context.env.KERNEL_CLT = build_context.motornode.make_node('mak/bin/ir_compile.py').abspath()
