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
    bld.headers('motor.mak', path=bld.motornode.find_node('mak'), features=['Makefile'], uselib=['cxx14'])
    bld.headers('motor.config', [])
    bld.headers(
        'motor.kernel', ['motor.config'],
        extra_public_includes=[bld.path.make_node('motor/kernel/api.cpu')],
        uselib=['cxx14']
    )
    bld.library('motor.minitl', bld.platforms + ['motor.mak', 'motor.kernel'], uselib=['cxx14'])
    bld.library('motor.core', ['motor.minitl', 'motor.kernel'], uselib=['cxx14'])
    bld.library('motor.network', ['motor.core'], uselib=['cxx14'])
    bld.library('motor.meta', ['motor.core', 'motor.network'], ['motor.3rdparty.system.zlib'], uselib=['cxx14'])
    bld.library('motor.filesystem', ['motor.core', 'motor.meta'], ['motor.3rdparty.system.minizip'], uselib=['cxx14'])
    bld.library('motor.introspect', ['motor.core', 'motor.meta', 'motor.filesystem'], uselib=['cxx14'])
    bld.library(
        'motor.reflection', ['motor.core', 'motor.meta', 'motor.filesystem', 'motor.introspect'], uselib=['cxx14']
    )
    bld.library('motor.settings', ['motor.meta', 'motor.reflection'], uselib=['cxx14'])
    bld.library('motor.resource', ['motor.core', 'motor.meta', 'motor.filesystem'], uselib=['cxx14'])
    bld.library('motor.scheduler', ['motor.core', 'motor.meta', 'motor.resource', 'motor.settings'], uselib=['cxx14'])
    bld.library(
        'motor.plugin', ['motor.core', 'motor.meta', 'motor.filesystem', 'motor.resource', 'motor.scheduler'],
        uselib=['cxx14']
    )
    bld.library(
        'motor.world', ['motor.core', 'motor.meta', 'motor.resource', 'motor.scheduler', 'motor.plugin'],
        uselib=['cxx14']
    )
    bld.shared_library(
        'motor', [
            'motor.core', 'motor.meta', 'motor.introspect', 'motor.reflection', 'motor.settings', 'motor.scheduler',
            'motor.filesystem', 'motor.world', 'motor.plugin'
        ],
        project_name='motor.motor',
        path=bld.path.find_node('motor/motor'),
        uselib=['cxx14']
    )

    bld.engine('motor.launcher', ['motor'], uselib=['cxx14'])


def build_plugins(bld):
    """
        Declares all plugins
    """
    bld.recurse('plugin/compute/opencl/mak/build.py')
    bld.plugin('plugin.debug.runtime', ['motor'], uselib=['cxx14'])
    bld.plugin('plugin.debug.assert', ['motor', 'plugin.debug.runtime'], uselib=['cxx14'])

    bld.plugin('plugin.scripting.package', ['motor'], uselib=['cxx14'])

    bld.plugin('plugin.physics.bullet', ['motor'], ['motor.3rdparty.physics.bullet'], uselib=['cxx14'])

    bld.plugin('plugin.graphics.3d', ['motor'], uselib=['cxx14'])
    bld.plugin('plugin.graphics.shadermodel1', ['motor', 'plugin.graphics.3d'], uselib=['cxx14'])
    bld.plugin(
        'plugin.graphics.shadermodel2', ['motor', 'plugin.graphics.3d', 'plugin.graphics.shadermodel1'],
        uselib=['cxx14']
    )
    bld.plugin(
        'plugin.graphics.shadermodel3',
        ['motor', 'plugin.graphics.3d', 'plugin.graphics.shadermodel1', 'plugin.graphics.shadermodel2'],
        uselib=['cxx14']
    )
    bld.plugin(
        'plugin.graphics.shadermodel4', [
            'motor', 'plugin.graphics.3d', 'plugin.graphics.shadermodel1', 'plugin.graphics.shadermodel2',
            'plugin.graphics.shadermodel3'
        ],
        uselib=['cxx14']
    )

    #bld.plugin('plugin.audio.AL',
    #           ['motor'],
    #           ['motor.3rdparty.audio.OpenAL'])

    bld.plugin('plugin.scripting.lua', ['motor'], ['motor.3rdparty.scripting.lua'], uselib=['cxx14'])
    bld.plugin('plugin.input.input', ['motor'], uselib=['cxx14'])
    bld.shared_library('plugin.scripting.pythonlib', ['motor'], conditions=['python'], uselib=['cxx14'])
    bld.plugin(
        'plugin.scripting.python', ['motor', 'plugin.scripting.pythonlib'], conditions=['python'], uselib=['cxx14']
    )
    bld.python_module(
        'py_motor', ['motor', 'plugin.scripting.pythonlib'],
        path=bld.path.find_node('plugin/scripting/pythonmodule'),
        conditions=['python'],
        uselib=['cxx14']
    )
    if bld.env.PROJECTS:
        python_deps = [
            'motor.3rdparty.scripting.python%s' % version.replace('.', '') for version in bld.env.PYTHON_VERSIONS
        ]
        bld.plugin(
            'plugin.scripting.pythonbinding', ['motor', 'plugin.scripting.pythonlib'] + python_deps, uselib=['cxx14']
        )
    else:
        for version in bld.env.PYTHON_VERSIONS:
            short_version = version.replace('.', '')
            bld.plugin(
                'plugin.scripting.python%s' % short_version, ['motor', 'plugin.scripting.python'],
                ['motor.3rdparty.scripting.python%s' % short_version],
                path=bld.path.find_node('plugin/scripting/pythonbinding'),
                conditions=['python%s' % version],
                uselib=['cxx14']
            )

    bld.plugin('plugin.compute.cpu', ['motor'], features=['motor:cpu:variants'], uselib=['cxx14'])
    bld.plugin(
        'plugin.compute.opencl', ['motor', 'plugin.compute.cpu'], ['motor.3rdparty.compute.OpenCL'],
        conditions=['OpenCL'],
        extra_defines=['CL_TARGET_OPENCL_VERSION=120'],
        extra_public_defines=['CL_TARGET_OPENCL_VERSION=120'],
        uselib=['cxx14']
    )
    #bld.plugin(
    #    'plugin.compute.opencl_gl',
    #    ['motor', 'plugin.graphics.GL4', 'plugin.compute.opencl', 'plugin.compute.cpu'],
    #    ['motor.3rdparty.graphics.OpenGL', 'motor.3rdparty.compute.OpenCL'],
    #    features=['OpenGL', 'OpenCL', 'GUI']
    #)
    bld.plugin('plugin.compute.cuda', ['motor'], ['motor.3rdparty.compute.CUDA'], conditions=['cuda'], uselib=['cxx14'])

    bld.plugin(
        'plugin.graphics.nullrender', [
            'motor', 'plugin.graphics.3d', 'plugin.graphics.shadermodel1', 'plugin.graphics.shadermodel2',
            'plugin.graphics.shadermodel3', 'plugin.graphics.shadermodel4'
        ],
        uselib=['cxx14']
    )
    bld.plugin(
        'plugin.graphics.windowing', ['motor', 'plugin.graphics.3d'],
        ['motor.3rdparty.system.X11', 'motor.3rdparty.graphics.OpenGL'],
        conditions=['GUI'],
        uselib=['cxx14']
    )
    bld.plugin(
        'plugin.graphics.GL4', ['motor', 'plugin.graphics.windowing'], ['motor.3rdparty.graphics.OpenGL'],
        conditions=['OpenGL', 'GUI'],
        uselib=['cxx14']
    )
    #bld.plugin('plugin.graphics.dx12',
    #           ['motor', 'plugin.graphics.windowing'],
    #           ['motor.3rdparty.graphics.DirectX12'],
    #           conditions=['DirectX12', 'GUI'])
    #bld.plugin('plugin.graphics.vulkan',
    #           ['motor', 'plugin.graphics.windowing'],
    #           ['motor.3rdparty.graphics.vulkan'],
    #           conditions=['Vulkan', 'GUI'])
    bld.plugin(
        'plugin.graphics.GLES2', ['motor', 'plugin.graphics.windowing'], ['motor.3rdparty.graphics.OpenGLES2'],
        conditions=['OpenGLES2', 'GUI'],
        uselib=['cxx14']
    )

    bld.plugin(
        'plugin.graphics.text', ['motor', 'plugin.graphics.3d'],
        ['motor.3rdparty.graphics.freetype', 'motor.3rdparty.system.fontconfig'],
        uselib=['cxx14']
    )

    bld.plugin('plugin.gameplay.subworld', ['motor'], uselib=['cxx14'])
    bld.plugin('plugin.gameplay.logic', ['motor'], uselib=['cxx14'])
    bld.plugin('plugin.gameplay.time', ['motor'], uselib=['cxx14'])

    if bld.env.check_gtk3 or bld.env.PROJECTS:
        bld.plugin('plugin.gui.gtk3', ['motor'], ['motor.3rdparty.gui.gtk3'], uselib=['cxx14'])
    bld.plugin('tool.motoreditor.ui', ['motor'], uselib=['cxx14'])


def build_games(bld):
    """
        Declares all games/samples/tools/autotests
    """
    bld.game(
        'motoreditor', ['motor', 'tool.motoreditor.ui', 'plugin.scripting.package'],
        path=bld.path.find_node('tool/motoreditor/main'),
        uselib=['cxx14']
    )
    bld.game('sample.text', ['motor', 'plugin.scripting.package', 'plugin.graphics.3d'], uselib=['cxx14'])
    bld.game('sample.python', ['motor', 'plugin.scripting.package'], uselib=['cxx14'])
    bld.game('sample.lua', ['motor', 'plugin.scripting.package', 'plugin.scripting.lua'], uselib=['cxx14'])
    if bld.env.check_gtk3 or bld.env.PROJECTS:
        bld.game('sample.gtk', ['motor', 'plugin.scripting.package', 'plugin.gui.gtk3'], uselib=['cxx14'])
    bld.game('help', ['motor', 'plugin.scripting.package'], path=bld.path.find_node('tool/help'), uselib=['cxx14'])
    if Options.options.tests:
        bld.game(
            'test.world', ['motor', 'plugin.scripting.package'], root_namespace='Motor::Test::World', uselib=['cxx14']
        )
        bld.game('test.settings', ['motor'], uselib=['cxx14'])
        bld.game(
            'test.compute.unittests', ['motor', 'plugin.scripting.package'],
            root_namespace='Motor::Test::Compute::UnitTests',
            uselib=['cxx14']
        )


def build(bld):
    """
        Declares each motor module and their dependencies
    """
    build_externals(bld)
    build_motor(bld)
    build_plugins(bld)
    build_games(bld)
