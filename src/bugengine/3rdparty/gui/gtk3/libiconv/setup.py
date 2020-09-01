LIBICONV_SOURCES = 'https://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.16.tar.gz'


def setup(conf):
    libiconv_node = conf.pkg_unpack('libiconv_src', LIBICONV_SOURCES, conf.path.ant_glob(['patches/*.*']))
    conf.env.LIBICONV_SOURCE = libiconv_node.path_from(conf.package_node)
