from waflib import Options
from waflib.TaskGen import feature, after_method
import os


def build_binary(bld, name, env, path):
    tg = bld.thirdparty(
        name,
        source_node=path,
        feature='OpenCL',
        use=['motor.3rdparty.graphics.OpenGL'],
        env=env,
    )
    tg.export_includes = [bld.path.parent.find_node('api')]
    return tg


def build(bld):
    bld.package('motor.3rdparty.compute.OpenCL', 'OPENCL_BINARY', build_binary, 'OPENCL_SOURCE', None)
