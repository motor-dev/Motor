from waflib.Errors import WafError
from waflib import Options
import os

LUA_SOURCES = 'https://www.lua.org/ftp/lua-5.3.5.tar.gz'
LUA_BINARIES = 'https://github.com/motor-dev/Motor/releases/download/prebuilt/lua-5.3.5-%(platform)s-%(arch)s-%(abi)s.tgz'


def setup_pkgconfig(conf):
    for v in '-5.4', '5.4', '-5.3', '5.3', '-5.2', '5.2', '-5.1', '5.1':
        try:
            conf.pkg_config('lua%s' % v, var='lua')
        except WafError as e:
            pass
        else:
            conf.env.LUA_BINARY = True
            conf.end_msg('version %s from pkg-config' % v)
            return True
    else:
        return False


def setup_system(conf):
    if 'windows' not in conf.env.VALID_PLATFORMS:
        for v in '-5.4', '5.4', '-5.3', '5.3', '-5.2', '5.2', '-5.1', '5.1':
            version = '%s%s' % (v[-3], v[-1])
            if conf.check_lib(
                'lua%s' % v,
                var='lua',
                includepath=['=/usr/include/lua%s' % version,
                             '=/usr/local/include/lua%s' % version],
                includes_externc=['lua.h'],
                functions=['lua_newstate']
            ):
                conf.env.LUA_BINARY = True
                conf.end_msg('version %s from system' % v)
                return True
    return False


def setup_prebuilt(conf):
    try:
        node = conf.pkg_unpack('lua_bin_%(platform)s-%(arch)s-%(abi)s', LUA_BINARIES)
        if not conf.check_package('motor.3rdparty.scripting.lua', node, var='lua'):
            raise WafError('no prebuilt binaries')
    except WafError:
        return False
    else:
        conf.env.LUA_BINARY = node.path_from(conf.package_node)
        conf.end_msg('from prebuilt')
        return True


def setup_source(conf):
    try:
        node = conf.pkg_unpack('lua_src', LUA_SOURCES, conf.path.parent.ant_glob(['patches/*.*']))
    except WafError:
        return False
    else:
        conf.env.LUA_SOURCE = node.path_from(conf.package_node)
        conf.end_msg('from source')
        return True


def setup(conf):
    conf.register_setup_option('lua_package')
    conf.start_msg_setup()
    found = False
    if conf.env.PROJECTS:
        found = setup_source(conf)
    if not found and Options.options.lua_package in ('best', 'pkgconfig'):
        found = setup_pkgconfig(conf)
    if not found and Options.options.lua_package in ('best', 'system'):
        found = setup_system(conf)
    if not found and Options.options.lua_package in ('best', 'prebuilt'):
        found = setup_prebuilt(conf)
    if not found and Options.options.lua_package in ('best', 'source'):
        found = setup_source(conf)
    if not found:
        conf.end_msg('disabled', color='RED')
