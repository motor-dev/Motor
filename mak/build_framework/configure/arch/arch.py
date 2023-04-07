import os


def configure(configuration_context):
    configuration_context.recurse(configuration_context.env.ARCH_NAME + '.py', once=False)
    for arch in os.listdir(configuration_context.path.abspath()):
        arch_name = os.path.splitext(arch)[0]
        if arch not in ('arch'):
            configuration_context.common_env.append_unique('ALL_ARCHS', arch_name)
