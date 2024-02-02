"""
    Use this file to declare all libraries and modules in the motor engine
"""
import build_framework
import waflib.Options
import waflib.TaskGen


@waflib.TaskGen.feature('motor:python_versions')
@waflib.TaskGen.before_method('process_source')
def define_python_versions(task_gen: waflib.TaskGen.task_gen) -> None:
    defines = getattr(task_gen, 'defines')
    env = task_gen.env
    versions = [v.replace('.', '') for v in env.PYTHON_VERSIONS[::-1]]
    versions = [v for v in versions if env['check_python%s' % v]]
    defines.append('MOTOR_PYTHON_VERSIONS=%s' % ','.join(versions))


def build_externals(build_context: build_framework.BuildContext) -> None:
    """
        Declares all external modules
    """
    build_framework.external(build_context, 'motor.3rdparty.compute.cpu')
    build_framework.external(build_context, 'motor.3rdparty.system.zlib')
    build_framework.external(build_context, 'motor.3rdparty.system.X11')
    build_framework.external(build_context, 'motor.3rdparty.system.win32')
    build_framework.external(build_context, 'motor.3rdparty.graphics.DirectX')
    build_framework.external(build_context, 'motor.3rdparty.graphics.OpenGL')
    build_framework.external(build_context, 'motor.3rdparty.graphics.OpenGLES2')
    build_framework.external(build_context, 'motor.3rdparty.graphics.freetype')
    build_framework.external(build_context, 'motor.3rdparty.gui.gtk3')
    build_framework.external(build_context, 'motor.3rdparty.compute.OpenCL')
    build_framework.external(build_context, 'motor.3rdparty.compute.CUDA')
    build_framework.external(build_context, 'motor.3rdparty.physics.bullet')
    build_framework.external(build_context, 'motor.3rdparty.scripting.lua')
    build_framework.external(build_context, 'motor.3rdparty.scripting.python')


def build_motor(build_context: build_framework.BuildContext) -> None:
    """
        Declares the main library and entry point
    """
    if build_context.env.PROJECTS:
        build_framework.headers(
            build_context, 'motor.mak',
            path=build_context.motornode.find_node('mak'),
            project_name='motor.mak',
            features=['motor:makefile'], uselib=['cxx14']
        )
    build_framework.headers(build_context, 'motor.config', [])
    build_framework.headers(
        build_context,
        'motor.kernel',
        ['motor.config'],
        extra_public_includes=[build_context.path.make_node('motor/kernel/api.cpu')],
        uselib=['cxx14']
    )
    build_framework.library(
        build_context,
        'motor.minitl',
        build_context.platforms + ['motor.mak', 'motor.kernel'],
        uselib=['cxx14']
    )
    build_framework.library(
        build_context,
        'motor.core',
        ['motor.minitl', 'motor.kernel'],
        uselib=['cxx14'])
    build_framework.library(build_context, 'motor.network', ['motor.core'], uselib=['cxx14'])
    build_framework.library(
        build_context,
        'motor.meta',
        ['motor.core', 'motor.network'],
        ['motor.3rdparty.system.zlib'],
        uselib=['cxx14']
    )
    build_framework.library(
        build_context,
        'motor.filesystem',
        ['motor.core', 'motor.meta'],
        ['motor.3rdparty.system.minizip'],
        uselib=['cxx14']
    )
    build_framework.library(
        build_context,
        'motor.introspect',
        ['motor.core', 'motor.meta', 'motor.filesystem'],
        uselib=['cxx14']
    )
    build_framework.library(
        build_context,
        'motor.reflection',
        ['motor.core', 'motor.meta', 'motor.filesystem', 'motor.introspect'],
        uselib=['cxx14']
    )
    build_framework.library(build_context, 'motor.settings', ['motor.meta', 'motor.reflection'], uselib=['cxx14'])
    build_framework.library(
        build_context,
        'motor.resource',
        ['motor.core', 'motor.meta', 'motor.filesystem'],
        uselib=['cxx14']
    )
    build_framework.library(
        build_context,
        'motor.scheduler',
        ['motor.core', 'motor.meta', 'motor.resource', 'motor.settings'],
        uselib=['cxx14']
    )
    build_framework.library(
        build_context,
        'motor.plugin',
        ['motor.core', 'motor.meta', 'motor.filesystem', 'motor.resource', 'motor.scheduler'],
        uselib=['cxx14']
    )
    build_framework.library(
        build_context,
        'motor.world',
        ['motor.core', 'motor.meta', 'motor.resource', 'motor.scheduler', 'motor.plugin'],
        uselib=['cxx14']
    )
    build_framework.shared_library(
        build_context,
        'motor',
        [
            'motor.core', 'motor.meta', 'motor.introspect', 'motor.reflection',
            'motor.settings', 'motor.scheduler',
            'motor.filesystem', 'motor.world', 'motor.plugin'
        ],
        project_name='motor.motor',
        path=build_context.path.find_node('motor/motor'),
        uselib=['cxx14']
    )

    build_framework.engine(build_context, 'motor.launcher', ['motor'], uselib=['cxx14'])


def build_plugins(build_context: build_framework.BuildContext) -> None:
    """
        Declares all plugins
    """
    build_context.recurse('plugin/compute/opencl/mak/build.py')
    build_context.recurse('plugin/compute/cuda/mak/build.py')

    build_framework.plugin(build_context, 'plugin.debug.runtime', ['motor'], uselib=['cxx14'])
    build_framework.plugin(build_context, 'plugin.debug.assert', ['motor', 'plugin.debug.runtime'], uselib=['cxx14'])

    build_framework.plugin(build_context, 'plugin.scripting.package', ['motor'], uselib=['cxx14'])

    build_framework.plugin(
        build_context, 'plugin.physics.bullet', ['motor'], ['motor.3rdparty.physics.bullet'],
        uselib=['cxx14']
    )

    build_framework.plugin(build_context, 'plugin.graphics.3d', ['motor'], uselib=['cxx14'])
    build_framework.plugin(
        build_context, 'plugin.graphics.shadermodel1', ['motor', 'plugin.graphics.3d'],
        uselib=['cxx14']
    )
    build_framework.plugin(
        build_context,
        'plugin.graphics.shadermodel2',
        ['motor', 'plugin.graphics.3d', 'plugin.graphics.shadermodel1'],
        uselib=['cxx14']
    )
    build_framework.plugin(
        build_context,
        'plugin.graphics.shadermodel3',
        ['motor', 'plugin.graphics.3d', 'plugin.graphics.shadermodel1',
         'plugin.graphics.shadermodel2'],
        uselib=['cxx14']
    )
    build_framework.plugin(
        build_context,
        'plugin.graphics.shadermodel4', [
            'motor', 'plugin.graphics.3d', 'plugin.graphics.shadermodel1',
            'plugin.graphics.shadermodel2',
            'plugin.graphics.shadermodel3'
        ],
        uselib=['cxx14']
    )

    build_framework.plugin(
        build_context, 'plugin.scripting.lua', ['motor'], ['motor.3rdparty.scripting.lua'],
        uselib=['cxx14']
    )
    build_framework.plugin(build_context, 'plugin.input.input', ['motor'], uselib=['cxx14'])
    build_framework.shared_library(
        build_context, 'plugin.scripting.pythonlib', ['motor'], conditions=['python'],
        uselib=['cxx14']
    )
    build_framework.plugin(
        build_context,
        'plugin.scripting.python', ['motor', 'plugin.scripting.pythonlib'], conditions=['python'],
        uselib=['cxx14'], features=['motor:python_versions']
    )
    getattr(build_context, 'python_module')(
        'py_motor', ['motor', 'plugin.scripting.pythonlib'],
        path=build_context.path.find_node('plugin/scripting/pythonmodule'),
        conditions=['python'],
        uselib=['cxx14'],
        project_name='plugin.scripting.pythonlib.py_motor'
    )
    if build_context.env.PROJECTS:
        build_framework.plugin(
            build_context,
            'plugin.scripting.python3', ['motor', 'plugin.scripting.python'],
            extra_defines=['PYTHON_LIBRARY=python3'],
            path=build_context.path.find_node('plugin/scripting/pythonbinding'), uselib=['cxx14']
        )
    else:
        for version in build_context.env.PYTHON_VERSIONS:
            short_version = version.replace('.', '')
            p = build_framework.plugin(
                build_context,
                'plugin.scripting.python%s' % short_version, ['motor', 'plugin.scripting.python'],
                ['motor.3rdparty.scripting.python%s' % short_version],
                path=build_context.path.find_node('plugin/scripting/pythonbinding'),
                conditions=['python%s' % version],
                uselib=['cxx14']
            )

    build_framework.plugin(build_context, 'plugin.compute.cpu', ['motor'], uselib=['cxx14'])
    build_framework.plugin(
        build_context,
        'plugin.compute.opencl', ['motor', 'plugin.compute.cpu'], ['motor.3rdparty.compute.OpenCL'],
        conditions=['OpenCL'],
        extra_defines=['CL_TARGET_OPENCL_VERSION=120'],
        extra_public_defines=['CL_TARGET_OPENCL_VERSION=120'],
        uselib=['cxx14']
    )

    build_framework.plugin(
        build_context, 'plugin.compute.cuda', ['motor'], ['motor.3rdparty.compute.CUDA'],
        conditions=['CUDA'],
        uselib=['cxx14']
    )

    build_framework.plugin(
        build_context,
        'plugin.graphics.nullrender', [
            'motor', 'plugin.graphics.3d', 'plugin.graphics.shadermodel1', 'plugin.graphics.shadermodel2',
            'plugin.graphics.shadermodel3', 'plugin.graphics.shadermodel4'
        ],
        uselib=['cxx14']
    )
    build_framework.plugin(
        build_context,
        'plugin.graphics.windowing', ['motor', 'plugin.graphics.3d'],
        ['motor.3rdparty.system.X11', 'motor.3rdparty.graphics.OpenGL'],
        conditions=['GUI'],
        uselib=['cxx14']
    )
    build_framework.plugin(
        build_context,
        'plugin.graphics.GL4', ['motor', 'plugin.graphics.windowing'], ['motor.3rdparty.graphics.OpenGL'],
        conditions=['OpenGL', 'GUI'],
        uselib=['cxx14']
    )
    build_framework.plugin(
        build_context,
        'plugin.graphics.GLES2', ['motor', 'plugin.graphics.windowing'], ['motor.3rdparty.graphics.OpenGLES2'],
        conditions=['OpenGLES2', 'GUI'],
        uselib=['cxx14']
    )

    build_framework.plugin(
        build_context,
        'plugin.graphics.text', ['motor', 'plugin.graphics.3d'],
        ['motor.3rdparty.graphics.freetype', 'motor.3rdparty.system.fontconfig'],
        uselib=['cxx14']
    )

    build_framework.plugin(build_context, 'plugin.gameplay.subworld', ['motor'], uselib=['cxx14'])
    build_framework.plugin(build_context, 'plugin.gameplay.logic', ['motor'], uselib=['cxx14'])
    build_framework.plugin(build_context, 'plugin.gameplay.time', ['motor'], uselib=['cxx14'])

    build_framework.plugin(build_context, 'plugin.gui.gtk3', ['motor'], ['motor.3rdparty.gui.gtk3'],
                           uselib=['cxx14'], conditions=['gtk3'])
    build_framework.plugin(build_context, 'tool.motoreditor.ui', ['motor'], uselib=['cxx14'])


def build_games(build_context: build_framework.BuildContext) -> None:
    """
        Declares all games/samples/tools/autotests
    """
    build_framework.game(
        build_context,
        'motoreditor', ['motor', 'tool.motoreditor.ui', 'plugin.scripting.package'],
        path=build_context.path.find_node('tool/motoreditor/main'),
        uselib=['cxx14'],
        project_name='tool.motoreditor.motoreditor'
    )
    build_framework.game(
        build_context, 'sample.text', ['motor', 'plugin.scripting.package', 'plugin.graphics.3d'],
        uselib=['cxx14']
    )
    build_framework.game(build_context, 'sample.python', ['motor', 'plugin.scripting.package'], uselib=['cxx14'])
    build_framework.game(
        build_context, 'sample.lua', ['motor', 'plugin.scripting.package', 'plugin.scripting.lua'],
        uselib=['cxx14']
    )
    if build_context.env.check_gtk3 or build_context.env.PROJECTS:
        build_framework.game(
            build_context, 'sample.gtk', ['motor', 'plugin.scripting.package', 'plugin.gui.gtk3'],
            uselib=['cxx14']
        )
    build_framework.game(
        build_context, 'help', ['motor', 'plugin.scripting.package'], path=build_context.path.find_node('tool/help'),
        uselib=['cxx14'],
        project_name='tool.help'
    )
    if waflib.Options.options.tests:
        build_framework.game(
            build_context, 'test.world', ['motor', 'plugin.scripting.package'], root_namespace='Motor::Test::World',
            uselib=['cxx14']
        )
        build_framework.game(build_context, 'test.settings', ['motor'], uselib=['cxx14'])
        build_framework.game(
            build_context,
            'test.compute.unittests', ['motor', 'plugin.scripting.package'],
            root_namespace='Motor::Test::Compute::UnitTests',
            uselib=['cxx14']
        )


def build(build_context: build_framework.BuildContext) -> None:
    """
        Declares each motor module and their dependencies
    """
    build_externals(build_context)
    build_motor(build_context)
    build_plugins(build_context)
    build_games(build_context)
