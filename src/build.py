"""
    Use this file to declare all libraries and modules in the motor
"""
from waflib import Options


def build_externals(bld):
    """
        Declares all external modules
    """
    bld.external('motor.3rdparty.compute.cpu')
    bld.external('motor.3rdparty.system.zlib')
    bld.external('motor.3rdparty.system.X11')
    bld.external('motor.3rdparty.system.win32')
    bld.external('motor.3rdparty.graphics.DirectX')
    bld.external('motor.3rdparty.graphics.OpenGL')
    bld.external('motor.3rdparty.graphics.OpenGLES2')
    bld.external('motor.3rdparty.graphics.freetype')
    bld.external('motor.3rdparty.gui.gtk3')
    bld.external('motor.3rdparty.compute.OpenCL')
    bld.external('motor.3rdparty.compute.CUDA')
    bld.external('motor.3rdparty.physics.bullet')
    bld.external('motor.3rdparty.scripting.lua')
    bld.external('motor.3rdparty.scripting.python')


def build_motor(bld):
    """
        Declares the main library and entry point
    """
    bld.headers('motor.mak', path=bld.motornode.find_node('mak'), features=['Makefile'])
    bld.headers('motor.config', [])
    bld.headers('motor.kernel', ['motor.config'], extra_public_includes=[bld.path.make_node('motor/kernel/api.cpu')])
    bld.library('motor.minitl', bld.platforms + ['motor.mak', 'motor.kernel'])
    bld.library('motor.core', ['motor.minitl', 'motor.kernel'])
    bld.library('motor.network', ['motor.core'])
    bld.library('motor.meta', ['motor.core', 'motor.network'], ['motor.3rdparty.system.zlib'])
    bld.library('motor.filesystem', ['motor.core', 'motor.meta'], ['motor.3rdparty.system.minizip'])
    bld.library('motor.introspect', ['motor.core', 'motor.meta', 'motor.filesystem'])
    bld.library('motor.reflection', ['motor.core', 'motor.meta', 'motor.filesystem', 'motor.introspect'])
    bld.library('motor.settings', ['motor.meta', 'motor.reflection'])
    bld.library('motor.resource', ['motor.core', 'motor.meta', 'motor.filesystem'])
    bld.library('motor.scheduler', ['motor.core', 'motor.meta', 'motor.resource', 'motor.settings'])
    bld.library('motor.plugin', ['motor.core', 'motor.meta', 'motor.filesystem', 'motor.resource', 'motor.scheduler'])
    bld.library('motor.world', ['motor.core', 'motor.meta', 'motor.resource', 'motor.scheduler', 'motor.plugin'])
    bld.shared_library(
        'motor', [
            'motor.core', 'motor.meta', 'motor.introspect', 'motor.reflection', 'motor.settings', 'motor.scheduler',
            'motor.filesystem', 'motor.world', 'motor.plugin'
        ],
        path=bld.path.find_node('motor/motor')
    )

    bld.engine('motor.launcher', ['motor'])


def build_plugins(bld):
    """
        Declares all plugins
    """
    bld.recurse('plugin/compute/opencl/mak/build.py')
    bld.plugin('plugin.debug.runtime', ['motor'])
    bld.plugin('plugin.debug.assert', ['motor', 'plugin.debug.runtime'])

    bld.plugin('plugin.scripting.package', ['motor'])

    bld.plugin('plugin.physics.bullet', ['motor'], ['motor.3rdparty.physics.bullet'])

    bld.plugin('plugin.graphics.3d', ['motor'])
    bld.plugin('plugin.graphics.shadermodel1', ['motor', 'plugin.graphics.3d'])
    bld.plugin('plugin.graphics.shadermodel2', ['motor', 'plugin.graphics.3d', 'plugin.graphics.shadermodel1'])
    bld.plugin(
        'plugin.graphics.shadermodel3',
        ['motor', 'plugin.graphics.3d', 'plugin.graphics.shadermodel1', 'plugin.graphics.shadermodel2']
    )
    bld.plugin(
        'plugin.graphics.shadermodel4', [
            'motor', 'plugin.graphics.3d', 'plugin.graphics.shadermodel1', 'plugin.graphics.shadermodel2',
            'plugin.graphics.shadermodel3'
        ]
    )

    #bld.plugin('plugin.audio.AL',
    #           ['motor'],
    #           ['motor.3rdparty.audio.OpenAL'])

    bld.plugin('plugin.scripting.lua', ['motor'], ['motor.3rdparty.scripting.lua'])
    bld.plugin('plugin.input.input', ['motor'])
    bld.shared_library('plugin.scripting.pythonlib', ['motor'], conditions=['python'])
    bld.plugin('plugin.scripting.python', ['motor', 'plugin.scripting.pythonlib'], conditions=['python'])
    bld.python_module(
        'py_motor', ['motor', 'plugin.scripting.pythonlib'],
        path=bld.path.find_node('plugin/scripting/pythonmodule'),
        conditions=['python']
    )
    if bld.env.PROJECTS:
        python_deps = [
            'motor.3rdparty.scripting.python%s' % version.replace('.', '') for version in bld.env.PYTHON_VERSIONS
        ]
        bld.plugin('plugin.scripting.pythonbinding', ['motor', 'plugin.scripting.pythonlib'] + python_deps)
    else:
        for version in bld.env.PYTHON_VERSIONS:
            short_version = version.replace('.', '')
            bld.plugin(
                'plugin.scripting.python%s' % short_version, ['motor', 'plugin.scripting.python'],
                ['motor.3rdparty.scripting.python%s' % short_version],
                path=bld.path.find_node('plugin/scripting/pythonbinding'),
                conditions=['python%s' % version]
            )

    bld.plugin('plugin.compute.cpu', ['motor'], features=['motor:cpu:variants'])
    bld.plugin(
        'plugin.compute.opencl', ['motor', 'plugin.compute.cpu'], ['motor.3rdparty.compute.OpenCL'],
        conditions=['OpenCL'],
        extra_defines=['CL_TARGET_OPENCL_VERSION=120'],
        extra_public_defines=['CL_TARGET_OPENCL_VERSION=120']
    )
    #bld.plugin(
    #    'plugin.compute.opencl_gl',
    #    ['motor', 'plugin.graphics.GL4', 'plugin.compute.opencl', 'plugin.compute.cpu'],
    #    ['motor.3rdparty.graphics.OpenGL', 'motor.3rdparty.compute.OpenCL'],
    #    features=['OpenGL', 'OpenCL', 'GUI']
    #)
    bld.plugin('plugin.compute.cuda', ['motor'], ['motor.3rdparty.compute.CUDA'], conditions=['cuda'])

    bld.plugin(
        'plugin.graphics.nullrender', [
            'motor', 'plugin.graphics.3d', 'plugin.graphics.shadermodel1', 'plugin.graphics.shadermodel2',
            'plugin.graphics.shadermodel3', 'plugin.graphics.shadermodel4'
        ]
    )
    bld.plugin(
        'plugin.graphics.windowing', ['motor', 'plugin.graphics.3d'],
        ['motor.3rdparty.system.X11', 'motor.3rdparty.graphics.OpenGL'],
        conditions=['GUI']
    )
    bld.plugin(
        'plugin.graphics.GL4', ['motor', 'plugin.graphics.windowing'], ['motor.3rdparty.graphics.OpenGL'],
        conditions=['OpenGL', 'GUI']
    )
    bld.plugin(
        'plugin.graphics.Dx9', ['motor', 'plugin.graphics.windowing'], ['motor.3rdparty.graphics.DirectX9'],
        conditions=['DirectX9', 'GUI']
    )
    #bld.plugin('plugin.graphics.Dx10',
    #           ['motor', 'plugin.graphics.windowing'],
    #           ['motor.3rdparty.graphics.DirectX10'],
    #           conditions=['DirectX10', 'GUI'])
    #bld.plugin('plugin.graphics.Dx11',
    #           ['motor', 'plugin.graphics.windowing'],
    #           ['motor.3rdparty.graphics.DirectX11'],
    #           conditions=['DirectX11', 'GUI'])
    bld.plugin(
        'plugin.graphics.GLES2', ['motor', 'plugin.graphics.windowing'], ['motor.3rdparty.graphics.OpenGLES2'],
        conditions=['OpenGLES2', 'GUI']
    )

    bld.plugin(
        'plugin.graphics.text', ['motor', 'plugin.graphics.3d'],
        ['motor.3rdparty.graphics.freetype', 'motor.3rdparty.system.fontconfig']
    )

    bld.plugin('plugin.gameplay.subworld', ['motor'])
    bld.plugin('plugin.gameplay.logic', ['motor'])
    bld.plugin('plugin.gameplay.time', ['motor'])

    if bld.env.check_gtk3 or bld.env.PROJECTS:
        bld.plugin('plugin.gui.gtk3', ['motor'], ['motor.3rdparty.gui.gtk3'])
    bld.plugin('tool.motoreditor.ui', ['motor'])


def build_games(bld):
    """
        Declares all games/samples/tools/autotests
    """
    bld.game(
        'motoreditor', ['motor', 'tool.motoreditor.ui', 'plugin.scripting.package'],
        path=bld.path.find_node('tool/motoreditor/main')
    )
    bld.game('sample.text', ['motor', 'plugin.scripting.package', 'plugin.graphics.3d'])
    bld.game('sample.python', ['motor', 'plugin.scripting.package'])
    bld.game('sample.lua', ['motor', 'plugin.scripting.package', 'plugin.scripting.lua'])
    if bld.env.check_gtk3 or bld.env.PROJECTS:
        bld.game('sample.gtk', ['motor', 'plugin.scripting.package', 'plugin.gui.gtk3'])
    bld.game('help', ['motor', 'plugin.scripting.package'], path=bld.path.find_node('tool/help'))
    if Options.options.tests:
        bld.game('test.world', ['motor', 'plugin.scripting.package'], root_namespace='Motor::Test::World')
        bld.game('test.settings', ['motor'])
        bld.game(
            'test.compute.unittests', ['motor', 'plugin.scripting.package'],
            root_namespace='Motor::Test::Compute::UnitTests'
        )


def build(bld):
    """
        Declares each motor module and their dependencies
    """
    build_externals(bld)
    build_motor(bld)
    build_plugins(bld)
    build_games(bld)
