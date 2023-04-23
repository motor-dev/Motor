from waflib.TaskGen import feature, task_gen
from waflib import Context
import os


def build(bld):
    if not bld.env.PROJECTS:
        root = bld.path.parent
        tg = task_gen(bld=bld, target='package')

        source_node = root.find_node('src/motor/launcher/src')
        resource_node = root.find_node('src/motor/launcher/res')
        resources = bld(
            target='motor.android.resource',
            features=['motor:android:aapt_resource'],
            resource=resource_node,
            destfile=tg.make_bld_node('apk', '', 'resources.apk')
        )
        out_dir = tg.make_bld_node('jar', '', '')
        launcher = bld(
            target='motor.android.launcher',
            features=['cxx', 'javac', 'dex'],
            source_nodes=[source_node, resource_node],
            destfile='classes.dex'
        )

        appname = getattr(Context.g_module, Context.APPNAME, bld.srcnode.name)
        package_unsigned = tg.make_bld_node('apk', '', appname + '.unsigned.apk')
        package_unaligned = tg.make_bld_node('apk', '', appname + '.unaligned.apk')
        package_final = tg.make_bld_node('apk', '', appname + '.apk')

        bld.android_package_task = tg.create_task('aapt_pkg', [resources.destfile], [package_unsigned])
        if bld.env.JARSIGNER:
            sign_task = tg.create_task('jarsigner', [package_unsigned], [package_unaligned])
        else:
            sign_task = tg.create_task('apksigner', [package_unsigned], [package_unaligned])
        align_task = tg.create_task('zipalign', [package_unaligned], [package_final])

        bld.add_to_group(tg)
        tg.install_files(os.path.join(bld.env.PREFIX, bld.optim), package_final, original_install=True)

    bld.platforms.append(bld.external('motor.3rdparty.android.libc++'))
    bld.platforms.append(bld.external('motor.3rdparty.android.libklcompat'))


def plugin(bld):
    pass
