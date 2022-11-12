import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(sys.argv[0]))), 'libs'))

if __name__ == '__main__':
    import pyxx
    argument_context = pyxx.init_arguments()
    argument_context.add_argument(
        "-p", "--pch", dest="pch", help="Insert an include for precompiled header at the start of the file"
    )
    argument_context.add_argument("-m", "--module", dest="module", help="Module root")
    argument_context.add_argument("-r", "--root", dest="root", help="Namespace root")
    argument_context.add_argument(
        "out",
        help="Output cc file",
        metavar="OUT",
    )
    argument_context.add_argument(
        "doc",
        help="Output doc file",
        metavar="DOC",
    )
    argument_context.add_argument(
        "namespaces",
        help="Output namespace file",
        metavar="NS",
    )

    arguments = argument_context.parse_args()
    results = pyxx.run(arguments)
    with open(arguments.out, 'w') as out:
        with open(arguments.doc, 'w') as doc:
            with open(arguments.namespaces, 'w') as ns:
                pass
