def setup(configuration_context):
    env = configuration_context.env
    if not env.PROJECTS:
        configuration_context.start_msg_setup()
        configuration_context.end_msg(
            ', '.join(['vanilla'] + env.VECTOR_OPTIM_VARIANTS), color='GREEN'
        )
        env.append_value('KERNEL_TOOLCHAINS', [('cpu', env.TOOLCHAIN)])
    node = configuration_context.bldnode.make_node(
        '%s/include/kernel_variants.hh' % (env.TOOLCHAIN_NAME))
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
