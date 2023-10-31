import argparse
import build_framework
from pyxx import cxx, messages
from ircc import ir_parser


def build(build_context: build_framework.BuildContext) -> None:
    argument_context = argparse.ArgumentParser()
    messages.init_arguments(argument_context)
    arguments = argument_context.parse_args([])
    logger = messages.load_arguments(arguments)
    cxx.Cxx14Parser(logger, build_context.bldnode.parent.parent.abspath())
    ir_parser.IrParser(build_context.bldnode.parent.parent.abspath())
    build_context.pyxx_nodes = [build_context.motornode.make_node('mak/tools/macros_def.json')]
    build_context.pyxx_nodes += build_context.motornode.make_node('mak/lib/pyxx').ant_glob('**/*.py', excl=[])
    build_context.pyxx_nodes += build_context.motornode.make_node('mak/lib/glrp').ant_glob('**/*.py', excl=[])
