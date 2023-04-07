from pyxx import cxx, messages
from ircc import ir_parser


def build(build_context):
    cxx.Cxx14Parser(None, build_context.bldnode.parent.parent.abspath())
    ir_parser.IrParser(build_context.bldnode.parent.parent.abspath())
    build_context.pyxx_nodes = [build_context.motornode.find_node('mak/tools/macros_def.json')]
    build_context.pyxx_nodes += build_context.motornode.find_node('mak/libs/pyxx').ant_glob('**/*.py', excl=[])
    build_context.pyxx_nodes += build_context.motornode.find_node('mak/libs/glrp').ant_glob('**/*.py', excl=[])
