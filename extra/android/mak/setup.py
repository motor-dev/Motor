import build_framework


def setup(setup_context: build_framework.SetupContext) -> None:
    category_node = setup_context.path.make_node('../src/motor/3rdparty/android')
    for third_party in category_node.listdir():
        setup_context.recurse('../src/motor/3rdparty/android/%s/mak/setup.py' % third_party, once=False)
