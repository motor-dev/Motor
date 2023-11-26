import os
import build_framework
import waflib.Context


def build(build_context: build_framework.BuildContext) -> None:
    if not build_context.env.PROJECTS:
        root = build_context.path.parent
        tg = build_context(group=build_context.motor_variant, target='package')

        source_node = root.find_node('src/motor/launcher/src')
        resource_node = root.find_node('src/motor/launcher/res')
        resources = build_context(
            group=build_context.motor_variant,
            target='motor.android.resource',
            features=['motor:android:aapt_resource'],
            resource=resource_node,
            destfile=build_framework.make_bld_node(tg, 'apk', '', 'resources.apk')
        )
        build_context(
            group=build_context.motor_variant,
            target='motor.android.launcher',
            features=['cxx', 'javac', 'dex'],
            source_nodes=[source_node, resource_node],
            destfile='classes.dex'
        )

        appname = getattr(waflib.Context.g_module, waflib.Context.APPNAME, build_context.srcnode.name)
        package_unsigned = build_framework.make_bld_node(tg, 'apk', '', appname + '.unsigned.apk')
        package_unaligned = build_framework.make_bld_node(tg, 'apk', '', appname + '.unaligned.apk')
        package_final = build_framework.make_bld_node(tg, 'apk', '', appname + '.apk')

        setattr(build_context, 'android_package_task',
                tg.create_task('aapt_pkg', [getattr(resources, 'destfile')], [package_unsigned]))
        if build_context.env.JARSIGNER:
            tg.create_task('jarsigner', [package_unsigned], [package_unaligned])
        else:
            tg.create_task('apksigner', [package_unsigned], [package_unaligned])
        tg.create_task('zipalign', [package_unaligned], [package_final])
        build_framework.install_files(tg, os.path.join(build_context.env.PREFIX, build_context.env.OPTIM),
                                      [package_final],
                                      original_install=True)

    build_context.platforms.append(build_framework.external(build_context, 'motor.3rdparty.android.libcxx'))
    build_context.platforms.append(build_framework.external(build_context, 'motor.3rdparty.android.libklcompat'))
