def build(bld):
    if bld.env.TCLTK_BINARY:
        bld.thirdparty(
            'motor.3rdparty.scripting.tcltk',
            path=bld.package_node.make_node(bld.env.TCLTK_BINARY),
        )
