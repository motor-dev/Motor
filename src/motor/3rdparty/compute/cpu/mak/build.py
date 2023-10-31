import build_framework


def build(build_context: build_framework.BuildContext) -> None:
    build_context.load('kernel_cpu', tooldir=[build_context.path.make_node('tools').abspath()])
