from pyxx import cxx
from ircc import ir_parser


def build(build_context):
    cxx.Cxx17Parser(build_context.bldnode.parent.parent.abspath())
    ir_parser.IrParser(build_context.bldnode.parent.parent.abspath())
