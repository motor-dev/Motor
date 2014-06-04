
def options(opt):
    pass

def setup(conf):
    if 'posix' in conf.env.VALID_PLATFORMS:
        try:
            conf.pkg_config('zlib', var='3rdparty.zlib')
        except Exception:
            pass
        else:
            conf.env.SYSTEM_ZLIB = True


def build(bld):
    if not bld.env.SYSTEM_ZLIB:
        bld.shared_library('3rdparty.zlib', bld.platforms, use_master=False,
                           extra_defines=['ZLIB_DLL'], extra_public_defines=['ZLIB_DLL'],
                           warnings=False, export_all=True)