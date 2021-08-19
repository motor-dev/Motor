def setup(configuration_context):
    category_node = configuration_context.path.make_node('../src/motor/3rdparty/android')
    for third_party in category_node.listdir():
        configuration_context.recurse('../src/motor/3rdparty/android/%s/mak/setup.py' % (third_party), once=False)
