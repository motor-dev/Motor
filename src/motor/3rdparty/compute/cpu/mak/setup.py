import build_framework


def setup(setup_context: build_framework.SetupContext) -> None:
    env = setup_context.env
    if not env.PROJECTS:
        build_framework.start_msg_setup(setup_context)
        setup_context.end_msg(
            ', '.join(['vanilla'] + env.VECTOR_OPTIM_VARIANTS), color='GREEN'
        )
        env.append_value('KERNEL_TOOLCHAINS', [('cpu', env.TOOLCHAIN)])
    node = setup_context.bldnode.make_node(
        '%s/include/kernel_variants.hh' % env.TOOLCHAIN_NAME)
    node.parent.mkdir()
    node.write(
        "static const char* s_cpuVariants[] = { %s };\n"
        "static const i32 s_cpuVariantCount = %d;\n"
        "" % (
            ', '.join('"%s"' % o for o in [''] + [v[1:] for v in env.VECTOR_OPTIM_VARIANTS]
                      ), 1 + len(env.VECTOR_OPTIM_VARIANTS)
        )
    )
    env.append_unique('INCLUDES', [node.parent.abspath()])
