
def options(opt):
    pass

def setup(conf):
    pass

def build(bld):
    stdcpp = bld.static_library('3rdparty.stl-gabi++', warnings=False)