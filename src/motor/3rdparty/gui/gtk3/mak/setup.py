import build_framework
import waflib.Errors
import waflib.Options

GTK3_API = 'https://github.com/motor-dev/Motor/releases/download/prebuilt/gtk+-3.0-api.tgz'
GTK3_BINARIES = 'https://github.com/motor-dev/Motor/releases/download/prebuilt/gtk+-3.0-%(platform)s-%(arch)s.tgz'


def setup_pkgconfig(setup_context: build_framework.SetupContext) -> bool:
    try:
        build_framework.pkg_config(setup_context, 'gtk+-3.0', var='gtk3')
    except waflib.Errors.WafError:
        return False
    else:
        setup_context.env.GTK3_BINARY = True
        setup_context.end_msg('from pkg-config')
        return True


def setup_system(setup_context: build_framework.SetupContext) -> bool:
    if build_framework.check_lib(
            setup_context,
            [
                'gtk-3.0', 'gdk-3.0', 'pangocairo-1.0', 'pango-1.0', 'atk-1.0', 'cairo-gobject', 'cairo',
                'gdk_pixbuf-2.0',
                'gobject-2.0', 'glib-2.0', 'intl'
            ],
            var='gtk3',
            includes=['gtk/gtk.h'],
            includepath=sum(
                [
                    ['=/usr/include/%s' % lib, '=/usr/local/include/%s' % lib] for lib in
                    [
                        'gtk-3.0',
                        'pango-1.0',
                        'glib-2.0',
                        'cairo',
                        'gdk-pixbuf-2.0',
                        'atk-1.0',
                        'harfbuzz',
                    ]
                ], []
            ) + [
                            '=/usr/lib/glib-2.0/include', '=/usr/local/lib/glib-2.0/include',
                            '=/usr/lib64/glib-2.0/include',
                            '=/usr/local/lib64/glib-2.0/include', '=/usr/lib32/glib-2.0/include',
                            '=/usr/local/lib32/glib-2.0/include'
                        ],
            functions=['gtk_application_window_new']
    ):
        setup_context.env.GTK3_BINARY = True
        setup_context.end_msg('from system')
        return True
    return False


def setup_api(setup_context: build_framework.SetupContext) -> bool:
    try:
        gtk3_node = build_framework.pkg_unpack(setup_context, 'gtk3_api', GTK3_API)
    except waflib.Errors.WafError:
        setup_context.end_msg('disabled - code completion for GTK will not work')
        return False
    else:
        setup_context.env.GTK3_SOURCE = gtk3_node.path_from(setup_context.package_node)
        setup_context.end_msg('headers for code completion')
        return True


def setup_prebuilt(setup_context: build_framework.SetupContext) -> bool:
    try:
        gtk3_node = build_framework.pkg_unpack(setup_context, 'gtk3_bin_%(platform)s-%(arch)s', GTK3_BINARIES)
        if not build_framework.check_package(
                setup_context,
                ['gtk-3.0', 'gdk-3.0', 'gobject-2.0', 'glib-2.0'],
                gtk3_node,
                var='gtk3',
                includes=['gtk/gtk.h'],
                functions=['gtk_application_window_new']
        ):
            raise waflib.Errors.WafError('using GTK3 from source')
    except waflib.Errors.WafError:
        return False
    else:
        setup_context.env.GTK3_BINARY = gtk3_node.path_from(setup_context.package_node)
        setup_context.end_msg('from prebuilt')
        return True


def setup_source(_: build_framework.SetupContext) -> bool:
    return False


def setup(setup_context: build_framework.SetupContext) -> None:
    build_framework.register_setup_option(setup_context, 'gtk3_package')
    found = False
    if setup_context.env.PROJECTS:
        build_framework.start_msg_setup(setup_context)
        setup_api(setup_context)
    elif 'pc' in setup_context.env.VALID_PLATFORMS:
        build_framework.start_msg_setup(setup_context)
        if not found and waflib.Options.options.gtk3_package in ('best', 'pkgconfig'):
            found = setup_pkgconfig(setup_context)
        if not found and waflib.Options.options.gtk3_package in ('best', 'system'):
            found = setup_system(setup_context)
        if not found and waflib.Options.options.gtk3_package in ('best', 'prebuilt'):
            found = setup_prebuilt(setup_context)
        if not found and waflib.Options.options.gtk3_package in ('best', 'source'):
            found = setup_source(setup_context)
        if not found:
            setup_context.end_msg('disabled - editor will not be built', color='RED')
